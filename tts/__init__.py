"""
TTS模块

提供语音合成客户端和工厂类，支持多种TTS服务：
- 百度语音合成 (baidu)
- 阿里语音合成 (ali) 
- 讯飞语音合成 (xunfei)
- 硅基流动语音合成 (siliconflow)
"""

from .base import TTSClient
from .baidu import BaiduTTSClient
from .ali import AliTTSClient
from .xunfei import XunfeiTTSClient
from .siliconflow import SiliconFlowTTSClient
from .factory import TTSClientFactory
from .config import (
    DEFAULT_TTS_SERVICE,
    BAIDU_TTS_CONFIG,
    ALI_TTS_CONFIG,
    XUNFEI_TTS_CONFIG,
    SILICONFLOW_TTS_CONFIG,
    TTS_SERVICES
)
from .tools import (
    generate_podcast_audio,
    generate_podcast_audio_segmented,
    split_text_by_speaker_tags,
    init_tts_client
)

__all__ = [
    "TTSClient",
    "BaiduTTSClient", 
    "AliTTSClient",
    "XunfeiTTSClient",
    "SiliconFlowTTSClient",
    "TTSClientFactory",
    "generate_podcast_audio",
    "generate_podcast_audio_segmented", 
    "split_text_by_speaker_tags",
    "init_tts_client",
    "DEFAULT_TTS_SERVICE",
    "BAIDU_TTS_CONFIG",
    "ALI_TTS_CONFIG", 
    "XUNFEI_TTS_CONFIG",
    "SILICONFLOW_TTS_CONFIG",
    "TTS_SERVICES"
]