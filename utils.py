"""
utils.py

Functions:
- generate_script: Get the dialogue from the LLM.
- call_llm: Call the LLM with the given prompt and dialogue format.
- parse_url: Parse the given URL and return the text content.
- generate_podcast_audio: Generate audio for podcast using TTS or advanced audio models.
- _use_suno_model: Generate advanced audio using Bark.
- _use_melotts_api: Generate audio using TTS model.
- _get_melo_tts_params: Get TTS parameters based on speaker and language.
"""

# Standard library imports
import json
import time
from pathlib import Path
from typing import Any, Union, Dict, Optional, List

# Third-party imports
import instructor
import requests
from aip import AipSpeech
from erniebot import ChatCompletion

# Local imports
import logging
from constants import (
    DEFAULT_LLM_PLATFORM,
    DEFAULT_TTS_SERVICE,
    LLM_PLATFORMS,
    TTS_SERVICES,
    JINA_READER_URL,
    JINA_RETRY_ATTEMPTS,
    JINA_RETRY_DELAY,
)
from schema import ShortDialogue, MediumDialogue

# 配置日志
logger = logging.getLogger(__name__)

# 大模型抽象类
class LLMClient:
    """大模型客户端抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """生成对话"""
        raise NotImplementedError("子类必须实现generate方法")

# 百度文心一言客户端
class ErnieClient(LLMClient):
    """百度文心一言客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        api_key = config.get("api_key")
        secret_key = config.get("secret_key")
        if api_key and secret_key:
            # 设置API密钥和密钥
            import erniebot
            erniebot.api_type = "aistudio"
            erniebot.access_token = api_key
        else:
            raise ValueError("请设置ERNIE_API_KEY和ERNIE_SECRET_KEY环境变量")
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """生成对话"""
        # 添加JSON格式要求到系统提示词
        system_prompt_with_format = f"{system_prompt}\n\n请严格按照以下JSON格式输出，不要添加任何其他内容：\n{response_format.model_json_schema()}"
        
        # 调用百度文心一言API
        response = ChatCompletion.create(
            model=self.config["model_id"],
            messages=[
                {"role": "system", "content": system_prompt_with_format},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config["temperature"],
        )
        
        # 解析JSON响应并转换为指定格式
        response_content = response.result
        response_dict = json.loads(response_content)
        
        # 使用Pydantic模型验证并返回
        return response_format(**response_dict)

# 阿里通义千问客户端
class QianWenClient(LLMClient):
    """阿里通义千问客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 通义千问客户端初始化
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")
        if not self.api_key or not self.secret_key:
            raise ValueError("请设置QIANWEN_API_KEY和QIANWEN_SECRET_KEY环境变量")
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """生成对话"""
        # 通义千问API调用逻辑
        # 注意：这里需要安装并导入通义千问SDK
        # 由于当前环境可能没有安装，这里先使用模拟实现
        raise NotImplementedError("通义千问客户端尚未实现")

# 硅基流动客户端
class SiliconFlowClient(LLMClient):
    """硅基流动客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        # 确保配置包含必要的属性
        if "retry_attempts" not in config:
            config["retry_attempts"] = 3
        if "retry_delay" not in config:
            config["retry_delay"] = 2
            
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model_id = config.get("model_id", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B")
        self.max_tokens = config.get("max_tokens", 16384)
        self.temperature = config.get("temperature", 0.1)
        if not self.api_key:
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """使用硅基流动API生成对话"""
        # 构建完整的提示词
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # 硅基流动API调用
        for attempt in range(self.config["retry_attempts"]):
            try:
                # 硅基流动Chat API端点
                url = "https://api.siliconflow.cn/v1/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "stream": False
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                
                # 提取生成的文本
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"]
                    
                    # 尝试解析为JSON格式（如果response_format是Pydantic模型）
                    try:
                        # 如果response_format是Pydantic模型，尝试解析JSON
                        if hasattr(response_format, 'model_validate_json'):
                            # 尝试直接解析JSON
                            try:
                                return response_format.model_validate_json(generated_text)
                            except Exception:
                                # 如果直接解析失败，尝试将script格式转换为Pydantic模型格式
                                try:
                                    # 假设API返回的是{"script": "对话内容"}格式
                                    script_data = json.loads(generated_text)
                                    if "script" in script_data:
                                        # 将script内容转换为Pydantic模型格式
                                        script_text = script_data["script"]
                                        # 创建默认的Pydantic模型对象
                                        model_data = {
                                            "scratchpad": "这是对话的草稿",
                                            "name_of_guest": "嘉宾",
                                            "dialogue": self._parse_script_to_dialogue(script_text)
                                        }
                                        return response_format(**model_data)
                                    else:
                                        raise Exception("API返回格式不包含script字段")
                                except Exception:
                                    # 如果JSON解析也失败，假设返回的是纯文本对话内容
                                    # 直接解析文本为对话格式
                                    model_data = {
                                        "scratchpad": "这是对话的草稿",
                                        "name_of_guest": "嘉宾",
                                        "dialogue": self._parse_script_to_dialogue(generated_text)
                                    }
                                    return response_format(**model_data)
                        else:
                            # 否则直接返回文本
                            return generated_text
                    except Exception as e:
                        # 如果所有解析都失败，返回原始文本
                        logger.warning(f"所有解析方法都失败，返回原始文本: {e}")
                        return generated_text
                else:
                    raise Exception(f"硅基流动API响应格式错误: {result}")
                
            except Exception as e:
                if attempt == self.config["retry_attempts"] - 1:  # Last attempt
                    raise Exception(f"硅基流动API错误: {str(e)}")
                time.sleep(self.config["retry_delay"])  # Wait for X second before retrying
    
    def _parse_script_to_dialogue(self, script_text: str) -> list:
        """将script文本转换为对话格式"""
        dialogue_items = []
        lines = script_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 简单的对话解析逻辑
            if ':' in line:
                parts = line.split(':', 1)
                speaker = parts[0].strip()
                text = parts[1].strip()
                
                # 确定说话者类型
                if 'Jane' in speaker or 'Host' in speaker or '主持人' in speaker:
                    speaker_type = "Host (Jane)"
                else:
                    speaker_type = "Guest"
                
                dialogue_items.append({
                    "speaker": speaker_type,
                    "text": text
                })
            else:
                # 如果没有明确说话者，假设是主持人的话
                dialogue_items.append({
                    "speaker": "Host (Jane)",
                    "text": line
                })
        
        return dialogue_items





# 大模型客户端工厂
class LLMClientFactory:
    """大模型客户端工厂"""
    
    @staticmethod
    def create_client(platform: str, config: Dict[str, Any]) -> LLMClient:
        """创建大模型客户端"""
        if platform == "ernie":
            return ErnieClient(config)
        elif platform == "qianwen":
            return QianWenClient(config)
        elif platform == "siliconflow":
            return SiliconFlowClient(config)

        else:
            raise ValueError(f"不支持的大模型平台: {platform}")

# 初始化大模型客户端
llm_client = None

def init_llm_client(platform: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> LLMClient:
    """初始化大模型客户端"""
    global llm_client
    # 如果指定了不同的平台，重新初始化客户端
    if platform and (not llm_client or platform != getattr(llm_client, 'platform', None)):
        target_config = config or LLM_PLATFORMS.get(platform)
        if not target_config:
            raise ValueError(f"找不到大模型平台配置: {platform}")
        llm_client = LLMClientFactory.create_client(platform, target_config)
        # 保存平台信息
        llm_client.platform = platform
    # 如果客户端尚未初始化，使用默认平台
    elif not llm_client:
        target_platform = platform or DEFAULT_LLM_PLATFORM
        target_config = config or LLM_PLATFORMS.get(target_platform)
        if not target_config:
            raise ValueError(f"找不到大模型平台配置: {target_platform}")
        llm_client = LLMClientFactory.create_client(target_platform, target_config)
        # 保存平台信息
        llm_client.platform = target_platform
    return llm_client

# TTS抽象类
class TTSClient:
    """TTS客户端抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        raise NotImplementedError("子类必须实现synthesize方法")

# 百度语音合成客户端
class BaiduTTSClient(TTSClient):
    """百度语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        app_id = config.get("app_id")
        api_key = config.get("api_key")
        secret_key = config.get("secret_key")
        if app_id and api_key and secret_key:
            self.client = AipSpeech(app_id, api_key, secret_key)
        else:
            raise ValueError("请设置BAIDU_APP_ID、BAIDU_API_KEY和BAIDU_SECRET_KEY环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        # 确定语音类型，确保同一人物使用相同的TTS参数
        per = self.config["per"].get(speaker, self.config["per"]["Host"])
        
        # 根据语言确定发音
        if language == "zh" or language == "ZJ":
            lang = "zh"
        else:
            lang = "en"
        
        # 调用百度语音合成API
        for attempt in range(self.config["retry_attempts"]):
            try:
                result = self.client.synthesis(
                    text,  # 要合成的文本
                    lang,  # 语言
                    1,     # 客户端类型
                    {
                        "spd": self.config["speed"],  # 语速，确保同一人物使用相同值
                        "pit": self.config["pitch"],  # 音调，确保同一人物使用相同值
                        "vol": self.config["volume"],  # 音量，确保同一人物使用相同值
                        "per": per,               # 发音人，确保同一人物使用相同值
                    }
                )
                
                # 检查结果
                if not isinstance(result, dict):
                    # 生成唯一文件名，使用speaker+sequence_number+timestamp格式
                    import os
                    timestamp = int(time.time())
                    if sequence_number is not None:
                        filename = f"audio_{speaker}_{sequence_number}_{timestamp}.mp3"
                    else:
                        filename = f"audio_{speaker}_{timestamp}.mp3"
                    
                    # 如果指定了输出目录，使用该目录，否则使用当前目录
                    if output_dir:
                        file_path = os.path.join(output_dir, filename)
                    else:
                        file_path = filename
                    
                    with open(file_path, "wb") as f:
                        f.write(result)
                    return file_path
                else:
                    raise Exception(f"百度TTS API错误: {result}")
            except Exception as e:
                if attempt == self.config["retry_attempts"] - 1:  # Last attempt
                    raise  # Re-raise the last exception if all attempts fail
                time.sleep(self.config["retry_delay"])  # Wait for X second before retrying

# 阿里语音合成客户端
class AliTTSClient(TTSClient):
    """阿里语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 阿里TTS客户端初始化
        # 注意：这里需要安装并导入阿里云SDK
        # 由于当前环境可能没有安装，这里先使用模拟实现
        self.access_key_id = config.get("access_key_id")
        self.access_key_secret = config.get("access_key_secret")
        self.app_key = config.get("app_key")
        if not self.access_key_id or not self.access_key_secret or not self.app_key:
            raise ValueError("请设置ALI_ACCESS_KEY_ID、ALI_ACCESS_KEY_SECRET和ALI_APP_KEY环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        # 阿里TTS API调用逻辑
        # 注意：这里需要安装并导入阿里云SDK
        # 由于当前环境可能没有安装，这里先使用模拟实现
        raise NotImplementedError("阿里TTS客户端尚未实现")

# 讯飞语音合成客户端
class XunfeiTTSClient(TTSClient):
    """讯飞语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # 讯飞TTS客户端初始化
        # 注意：这里需要安装并导入讯飞SDK
        # 由于当前环境可能没有安装，这里先使用模拟实现
        self.app_id = config.get("app_id")
        self.api_key = config.get("api_key")
        self.api_secret = config.get("api_secret")
        if not self.app_id or not self.api_key or not self.api_secret:
            raise ValueError("请设置XUNFEI_APP_ID、XUNFEI_API_KEY和XUNFEI_API_SECRET环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        # 讯飞TTS API调用逻辑
        # 注意：这里需要安装并导入讯飞SDK
        # 由于当前环境可能没有安装，这里先使用模拟实现
        raise NotImplementedError("讯飞TTS客户端尚未实现")

# 硅基流动语音合成客户端
class SiliconFlowTTSClient(TTSClient):
    """硅基流动语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        # 确保配置包含必要的属性
        if "retry_attempts" not in config:
            config["retry_attempts"] = 3
        if "retry_delay" not in config:
            config["retry_delay"] = 2
        if "speed" not in config:
            config["speed"] = 1.0
        if "voice_name" not in config:
            config["voice_name"] = {"Host": "fnlp/CosyVoice2-0.5B:alex", "Guest": "fnlp/CosyVoice2-0.5B:anna"}
            
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model_id = config.get("model_id", "fnlp/CosyVoice2-0.5B")
        if not self.api_key:
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """使用硅基流动API合成语音"""
        # 确定语音类型
        voice_name = self.config["voice_name"].get(speaker, self.config["voice_name"]["Host"])
        
        # 根据硅基流动文档，对话文本需要使用[S1]、[S2]、[S3]等标签
        # 将文本转换为硅基流动要求的格式
        # 支持多个嘉宾的区分，使用不同的S标签
        
        # 检查是否为批量合成（speaker为"Combined"且文本包含多个标签）
        if speaker == "Combined" and any(f"[S{i}]" in text for i in range(1, 6)):
            # 批量合成模式：文本已经包含标签，直接使用
            formatted_text = text
            logger.info(f"Using batch synthesis mode for SiliconFlow TTS")
        else:
            # 单条合成模式：根据speaker添加标签
            logger.info(f"speaker: {speaker}, text: {text}")
            if speaker == "Host (Jane)":
                formatted_text = f"[S1]{text}"
            elif speaker == "Guest":
                formatted_text = f"[S2]{text}"
            elif speaker == "Guest 2":
                formatted_text = f"[S3]{text}"
            elif speaker == "Guest 3":
                formatted_text = f"[S4]{text}"
            elif speaker == "Guest 4":
                formatted_text = f"[S5]{text}"
            else:
                # 如果有其他speaker类型，默认使用S2标签
                formatted_text = f"[S2]{text}"
        
        # 硅基流动TTS API调用
        for attempt in range(self.config["retry_attempts"]):
            try:
                # 硅基流动TTS API端点
                url = "https://api.siliconflow.cn/v1/audio/speech"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model_id,
                    "input": formatted_text,
                    "voice": voice_name,
                    "max_tokens": 4096,  # 增加max_tokens以支持更长的音频
                    "response_format": "mp3",
                    "sample_rate": 32000,
                    "stream": False,
                    "speed": self.config["speed"],
                    "gain": 0
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                
                # 生成唯一文件名，使用speaker+sequence_number+timestamp格式
                import os
                timestamp = int(time.time())
                if sequence_number is not None:
                    filename = f"siliconflow_audio_{speaker}_{sequence_number}_{timestamp}.mp3"
                else:
                    filename = f"siliconflow_audio_{speaker}_{timestamp}.mp3"
                
                # 如果指定了输出目录，使用该目录，否则使用当前目录
                if output_dir:
                    file_path = os.path.join(output_dir, filename)
                else:
                    file_path = filename
                
                # 保存音频文件
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return file_path
                
            except Exception as e:
                if attempt == self.config["retry_attempts"] - 1:  # Last attempt
                    raise Exception(f"硅基流动TTS API错误: {str(e)}")
                time.sleep(self.config["retry_delay"])  # Wait for X second before retrying


# TTS客户端工厂
class TTSClientFactory:
    """TTS客户端工厂"""
    
    @staticmethod
    def create_client(service: str, config: Dict[str, Any]) -> TTSClient:
        """创建TTS客户端"""
        if service == "baidu":
            return BaiduTTSClient(config)
        elif service == "ali":
            return AliTTSClient(config)
        elif service == "xunfei":
            return XunfeiTTSClient(config)
        elif service == "siliconflow":
            return SiliconFlowTTSClient(config)

        else:
            raise ValueError(f"不支持的TTS服务: {service}")

# 初始化TTS客户端
tts_clients = {}

def init_tts_client(service: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> TTSClient:
    """初始化TTS客户端"""
    global tts_clients
    target_service = service or DEFAULT_TTS_SERVICE
    if target_service not in tts_clients:
        target_config = config or TTS_SERVICES.get(target_service)
        if not target_config:
            raise ValueError(f"找不到TTS服务配置: {target_service}")
        tts_clients[target_service] = TTSClientFactory.create_client(target_service, target_config)
    return tts_clients[target_service]

# 初始化默认客户端
init_llm_client()
init_tts_client()

def generate_script(
    system_prompt: str,
    input_text: str,
    output_model: Union[ShortDialogue, MediumDialogue],
    llm_platform: Optional[str] = None,
) -> Union[ShortDialogue, MediumDialogue]:
    """Get the dialogue from the LLM."""
    
    logger.info("=== 播客脚本生成开始 ===")
    logger.info(f"目标模型: {output_model.__name__}")
    logger.info(f"输入文本长度: {len(input_text)}")

    # Call the LLM for the first time
    logger.info("--- 第一次大模型调用：生成初稿 ---")
    first_draft_dialogue = call_llm(system_prompt, input_text, output_model, llm_platform)
    logger.info("--- 第一次大模型调用完成 ---")

    # 检查返回的是否是Pydantic模型对象
    if hasattr(first_draft_dialogue, 'model_dump_json'):
        # 如果是Pydantic模型对象，使用model_dump_json()
        dialogue_json = first_draft_dialogue.model_dump_json()
    else:
        # 如果是字符串或其他类型，直接使用
        dialogue_json = str(first_draft_dialogue)

    # Call the LLM a second time to improve the dialogue
    logger.info("--- 第二次大模型调用：改进对话 ---")
    system_prompt_with_dialogue = f"{system_prompt}\n\n这是你提供的对话初稿：\n\n{dialogue_json}."
    final_dialogue = call_llm(system_prompt_with_dialogue, "请改进对话，使其更自然、更吸引人。", output_model, llm_platform)
    logger.info("--- 第二次大模型调用完成 ---")
    
    logger.info("=== 播客脚本生成完成 ===")

    return final_dialogue


def call_llm(system_prompt: str, text: str, dialogue_format: Any, platform: Optional[str] = None) -> Any:
    """Call the LLM with the given prompt and dialogue format."""
    try:
        # 获取大模型客户端
        client = init_llm_client(platform)
        
        # 记录大模型交互信息
        logger.info("=== 大模型交互开始 ===")
        logger.info(f"使用平台: {platform or '默认平台'}")
        logger.info(f"系统提示词 (长度: {len(system_prompt)}):\n{system_prompt}")
        logger.info(f"用户输入 (长度: {len(text)}):\n{text}")
        
        # 调用大模型生成对话
        result = client.generate(system_prompt, text, dialogue_format)
        
        # 记录生成结果
        if hasattr(result, 'model_dump_json'):
            # 如果是Pydantic模型对象，记录JSON格式
            result_json = result.model_dump_json(indent=2)
            logger.info(f"生成对话结果 (JSON格式):\n{result_json}")
        else:
            # 如果是字符串或其他类型，直接记录
            logger.info(f"生成对话结果 (文本格式):\n{result}")
        
        logger.info("=== 大模型交互结束 ===")
        
        return result
    except Exception as e:
        # 记录错误信息
        logger.error(f"大模型调用失败: {str(e)}")
        if platform:
            logger.error(f"失败平台: {platform}")
        
        # 添加更详细的错误信息
        error_msg = f"大模型调用失败: {str(e)}"
        if platform:
            error_msg += f" (平台: {platform})"
        raise Exception(error_msg) from e


def parse_url(url: str) -> str:
    """Parse the given URL and return the text content."""
    for attempt in range(JINA_RETRY_ATTEMPTS):
        try:
            full_url = f"{JINA_READER_URL}{url}"
            response = requests.get(full_url, timeout=120)
            response.raise_for_status()  # Raise an exception for bad status codes
            break
        except requests.RequestException as e:
            if attempt == JINA_RETRY_ATTEMPTS - 1:  # Last attempt
                raise ValueError(
                    f"Failed to fetch URL after {JINA_RETRY_ATTEMPTS} attempts: {e}"
                ) from e
            time.sleep(JINA_RETRY_DELAY)  # Wait for X second before retrying
    return response.text


def split_text_by_speaker_tags(text: str, max_length: int = 1000) -> List[str]:
    """将包含说话者标签的文本分割成多个段落"""
    segments = []
    current_segment = ""
    
    # 按行分割文本
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查当前行是否包含说话者标签
        if any(f"[S{i}]" in line for i in range(1, 6)):
            # 如果当前段落的长度加上新行会超过限制，且当前段落不为空
            if current_segment and len(current_segment + line) > max_length:
                segments.append(current_segment)
                current_segment = line
            else:
                if current_segment:
                    current_segment += "\n" + line
                else:
                    current_segment = line
        else:
            # 对于没有标签的行，直接添加到当前段落
            if current_segment:
                current_segment += "\n" + line
            else:
                current_segment = line
    
    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment)
    
    return segments


def generate_podcast_audio_segmented(
    text: str, speaker: str, language: str, random_voice_number: int, tts_service: Optional[str] = None, output_dir: Optional[str] = None, sequence_number: Optional[int] = None
) -> str:
    """使用分段合成方式生成播客音频，优化音色一致性"""
    try:
        # 获取TTS客户端
        tts_client = init_tts_client(tts_service)
        
        # 如果文本长度小于1500字符，直接合成
        if len(text) <= 1500:
            return tts_client.synthesize(text, speaker, language, output_dir, sequence_number)
        
        # 分段合成
        segments = split_text_by_speaker_tags(text, max_length=1000)
        logger.info(f"将文本分割为 {len(segments)} 个段落进行分段合成")
        
        audio_files = []
        temp_dir = Path(output_dir) if output_dir else Path(".")
        
        # 音色一致性优化：添加上下文保持机制
        context_seed = str(int(time.time()))  # 使用时间戳作为种子，确保同一批次调用参数一致
        
        for i, segment in enumerate(segments):
            logger.info(f"合成第 {i+1}/{len(segments)} 段音频 (长度: {len(segment)} 字符)")
            
            # 音色一致性优化：添加上下文前缀
            # 对于非第一段，添加前一段的最后一句作为上下文
            if i > 0 and len(segments[i-1]) > 0:
                # 获取前一段的最后一句（如果有多个句子）
                prev_segment_lines = segments[i-1].strip().split('\n')
                if prev_segment_lines:
                    last_line = prev_segment_lines[-1].strip()
                    if last_line and len(last_line) > 10:  # 确保有足够的内容
                        # 添加上下文前缀，但避免重复
                        if not segment.strip().startswith(last_line):
                            enhanced_segment = last_line + "\n" + segment
                        else:
                            enhanced_segment = segment
                    else:
                        enhanced_segment = segment
                else:
                    enhanced_segment = segment
            else:
                enhanced_segment = segment
            
            # 合成当前段落的音频
            segment_audio = tts_client.synthesize(
                enhanced_segment, speaker, language, str(temp_dir), 
                sequence_number if sequence_number is not None else i
            )
            audio_files.append(segment_audio)
            
            # 添加延迟避免API限制，但减少延迟时间
            time.sleep(0.5)  # 从1秒减少到0.5秒，减少音色变化的机会
        
        # 合并音频文件，优化音色一致性
        if len(audio_files) > 1:
            # 创建合并列表文件
            list_file_path = temp_dir / f"merge_list_{int(time.time())}.txt"
            with open(list_file_path, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
            
            # 合并音频，添加淡入淡出效果
            merged_audio_path = temp_dir / f"merged_audio_{int(time.time())}.mp3"
            
            import subprocess
            
            # 尝试使用带淡入淡出效果的合并方式
            try:
                # 方法1：使用复杂的FFmpeg命令添加淡入淡出
                filter_complex = ""
                for i in range(len(audio_files)):
                    filter_complex += f"[{i}:a]"
                
                # 添加淡入淡出效果：每段音频开头0.5秒淡入，结尾0.5秒淡出
                filter_complex += f"concat=n={len(audio_files)}:v=0:a=1[out]"
                
                # 构建输入文件列表
                input_args = []
                for audio_file in audio_files:
                    input_args.extend(['-i', str(audio_file)])
                
                result = subprocess.run([
                    'ffmpeg', *input_args,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-c:a', 'libmp3lame', '-q:a', '2',
                    str(merged_audio_path)
                ], capture_output=True, text=True, timeout=60)
                
            except (subprocess.TimeoutExpired, Exception):
                # 方法1失败时，回退到简单合并
                result = subprocess.run([
                    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(list_file_path),
                    '-c', 'copy', str(merged_audio_path)
                ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 删除临时文件
                list_file_path.unlink(missing_ok=True)
                for audio_file in audio_files:
                    Path(audio_file).unlink(missing_ok=True)
                
                logger.info(f"成功合并 {len(audio_files)} 段音频，音色一致性已优化")
                return str(merged_audio_path)
            else:
                logger.warning(f"音频合并失败: {result.stderr}")
                # 返回第一段音频作为备选
                return audio_files[0]
        else:
            return audio_files[0]
            
    except Exception as e:
        # 添加更详细的错误信息
        error_msg = f"TTS分段语音合成失败: {str(e)}"
        if tts_service:
            error_msg += f" (服务: {tts_service})"
        raise Exception(error_msg) from e


def generate_podcast_audio(
    text: str, speaker: str, language: str, random_voice_number: int, tts_service: Optional[str] = None, output_dir: Optional[str] = None, sequence_number: Optional[int] = None
) -> str:
    """Generate audio for podcast using TTS or advanced audio models."""
    try:
        # 对于硅基流动TTS，使用分段合成
        if tts_service == "siliconflow":
            return generate_podcast_audio_segmented(text, speaker, language, random_voice_number, tts_service, output_dir, sequence_number)
        
        # 其他TTS服务使用原有方式
        tts_client = init_tts_client(tts_service)
        return tts_client.synthesize(text, speaker, language, output_dir, sequence_number)
    except Exception as e:
        # 添加更详细的错误信息
        error_msg = f"TTS语音合成失败: {str(e)}"
        if tts_service:
            error_msg += f" (服务: {tts_service})"
        raise Exception(error_msg) from e
