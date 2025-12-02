"""
百度语音合成客户端模块

包含BaiduTTSClient类
"""

import json
import time
import os
from typing import Any, Dict, Optional

import requests
from aip import AipSpeech

import logging
logger = logging.getLogger(__name__)

from .base import TTSClient


class BaiduTTSClient(TTSClient):
    """百度语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get("app_id")
        self.api_key = config.get("api_key")
        self.secret_key = config.get("secret_key")
        if not self.app_id or not self.api_key or not self.secret_key:
            raise ValueError("请设置BAIDU_APP_ID、BAIDU_API_KEY和BAIDU_SECRET_KEY环境变量")
        
        # 初始化百度语音合成客户端
        self.client = AipSpeech(self.app_id, self.api_key, self.secret_key)
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """合成语音"""
        # 百度TTS API调用逻辑
        # 根据speaker和language选择合适的语音参数
        if language == "zh":
            voice = 0  # 女声
            if speaker == "Host (Jane)":
                voice = 0  # 女声
            elif speaker == "Guest":
                voice = 1  # 男声
            elif speaker == "Guest 2":
                voice = 3  # 情感男声
            elif speaker == "Guest 3":
                voice = 4  # 情感女声
            elif speaker == "Guest 4":
                voice = 1  # 男声
            else:
                voice = 0  # 默认女声
        else:
            voice = 0  # 默认女声
        
        # 调用百度TTS API
        result = self.client.synthesis(text, 'zh', 1, {
            'vol': 5,  # 音量
            'per': voice,  # 发音人
            'spd': 5,  # 语速
            'pit': 5,  # 音调
        })
        
        # 检查是否发生错误
        if isinstance(result, dict):
            raise Exception(f"百度TTS API错误: {result.get('err_msg', '未知错误')}")
        
        # 生成唯一文件名，使用speaker+sequence_number+timestamp格式
        timestamp = int(time.time())
        if sequence_number is not None:
            filename = f"baidu_audio_{speaker}_{sequence_number}_{timestamp}.mp3"
        else:
            filename = f"baidu_audio_{speaker}_{timestamp}.mp3"
        
        # 如果指定了输出目录，使用该目录，否则使用当前目录
        if output_dir:
            file_path = os.path.join(output_dir, filename)
        else:
            file_path = filename
        
        # 保存音频文件
        with open(file_path, "wb") as f:
            f.write(result)
        
        return file_path