"""
TTS客户端工厂模块

包含TTSClientFactory类，用于创建不同类型的TTS客户端实例。
"""

from typing import Any, Dict

from .base import TTSClient
from .baidu import BaiduTTSClient
from .ali import AliTTSClient
from .xunfei import XunfeiTTSClient
from .siliconflow import SiliconFlowTTSClient

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