"""
TTS配置管理模块
从各个TTS客户端获取默认配置，并支持环境变量覆盖
"""

import os
from typing import Dict, Any

# 导入各个TTS客户端以获取默认配置
from .baidu import BaiduTTSClient
from .ali import AliTTSClient
from .xunfei import XunfeiTTSClient
from .siliconflow import SiliconFlowTTSClient

# TTS服务配置
DEFAULT_TTS_SERVICE = os.getenv("DEFAULT_TTS_SERVICE", "baidu")

def get_config_with_env_overrides(client_class, env_prefix: str) -> Dict[str, Any]:
    """
    获取配置，支持环境变量覆盖默认值
    
    Args:
        client_class: TTS客户端类
        env_prefix: 环境变量前缀
        
    Returns:
        合并后的配置字典
    """
    config = client_class.DEFAULT_CONFIG.copy()
    
    # 遍历配置项，检查是否有对应的环境变量
    for key in config.keys():
        env_key = f"{env_prefix}_{key.upper()}"
        
        # 对于硅基流动TTS，使用特定的TTS环境变量前缀
        if env_prefix == "SILICONFLOW" and key == "model_id":
            # 优先使用SILICONFLOW_TTS_MODEL_ID环境变量
            tts_model_id = os.getenv("SILICONFLOW_TTS_MODEL_ID")
            if tts_model_id:
                config[key] = tts_model_id
                continue
        
        if os.getenv(env_key):
            # 根据值的类型进行转换
            if isinstance(config[key], int):
                config[key] = int(os.getenv(env_key))
            elif isinstance(config[key], float):
                config[key] = float(os.getenv(env_key))
            else:
                config[key] = os.getenv(env_key)
    
    return config

# 获取各个TTS服务的配置（支持环境变量覆盖）
BAIDU_TTS_CONFIG = get_config_with_env_overrides(BaiduTTSClient, "BAIDU")
ALI_TTS_CONFIG = get_config_with_env_overrides(AliTTSClient, "ALI")
XUNFEI_TTS_CONFIG = get_config_with_env_overrides(XunfeiTTSClient, "XUNFEI")
SILICONFLOW_TTS_CONFIG = get_config_with_env_overrides(SiliconFlowTTSClient, "SILICONFLOW")

# TTS服务配置映射
TTS_SERVICES = {
    "baidu": BAIDU_TTS_CONFIG,
    "ali": ALI_TTS_CONFIG,
    "xunfei": XUNFEI_TTS_CONFIG,
    "siliconflow": SILICONFLOW_TTS_CONFIG,
}