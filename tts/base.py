"""
TTS客户端基础模块

包含TTSClient抽象类
"""

from typing import Any, Dict, Optional


class TTSClient:
    """TTS客户端抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        raise NotImplementedError("子类必须实现synthesize方法")