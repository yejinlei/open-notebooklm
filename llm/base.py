"""
LLM客户端基础模块

包含LLMClient抽象类
"""

from typing import Any, Dict


class LLMClient:
    """大模型客户端抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def generate(self, system_prompt: str, user_prompt: str, response_format: Any) -> Any:
        """生成对话"""
        raise NotImplementedError("子类必须实现generate方法")