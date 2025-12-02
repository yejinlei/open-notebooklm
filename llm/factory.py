"""
LLM客户端工厂模块

包含LLMClientFactory类，用于创建不同类型的大模型客户端实例。
"""

from typing import Any, Dict

from .base import LLMClient
from .ernie import ErnieClient
from .qianwen import QianWenClient
from .siliconflow import SiliconFlowClient


# LLM客户端工厂
class LLMClientFactory:
    """LLM客户端工厂"""
    
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