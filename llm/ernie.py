"""
百度文心一言客户端
"""

import json
import os
from typing import Any, Dict

from erniebot import ChatCompletion

from .base import LLMClient


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