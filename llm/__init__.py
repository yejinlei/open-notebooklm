"""
LLM模块

包含大模型客户端抽象类、工厂类以及各个平台的具体实现。
"""

from .base import LLMClient
from .factory import LLMClientFactory

__all__ = ["LLMClient", "LLMClientFactory"]