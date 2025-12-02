"""
utils.py

Functions:
- generate_script: Get the dialogue from the LLM.
- call_llm: Call the LLM with the given prompt and dialogue format.
- parse_url: Parse the given URL and return the text content.
"""

# Standard library imports
import json
import time
from pathlib import Path
from typing import Any, Union, Dict, Optional, List

# Third-party imports
import instructor
import requests
from erniebot import ChatCompletion

# Local imports
import logging
from constants import (
    DEFAULT_LLM_PLATFORM,
    LLM_PLATFORMS,
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


# 初始化默认客户端
init_llm_client()

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



