"""
硅基流动客户端
"""

import json
import time
from typing import Any, Dict

import requests
import logging

from .base import LLMClient

logger = logging.getLogger(__name__)


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