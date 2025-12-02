"""
硅基流动语音合成客户端模块

包含SiliconFlowTTSClient类
"""

import time
import os
import requests
from typing import Any, Dict, Optional

import logging
logger = logging.getLogger(__name__)

from .base import TTSClient


class SiliconFlowTTSClient(TTSClient):
    """硅基流动语音合成客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        # 确保配置包含必要的属性
        if "retry_attempts" not in config:
            config["retry_attempts"] = int(os.getenv("SILICONFLOW_TTS_RETRY_ATTEMPTS", "3"))
        if "retry_delay" not in config:
            config["retry_delay"] = int(os.getenv("SILICONFLOW_TTS_RETRY_DELAY", "5"))
        if "speed" not in config:
            config["speed"] = float(os.getenv("SILICONFLOW_TTS_SPEED", "1.0"))
        if "voice_name" not in config:
            config["voice_name"] = {"Host": "FunAudioLLM/CosyVoice2-0.5B:alex", "Guest": "FunAudioLLM/CosyVoice2-0.5B:anna"}
            
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("SILICONFLOW_API_KEY")
        self.model_id = config.get("model_id") or os.getenv("SILICONFLOW_TTS_MODEL_ID", "FunAudioLLM/CosyVoice2-0.5B")
        if not self.api_key:
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
    
    def synthesize(self, text: str, speaker: str, language: str, output_dir: Optional[str] = None, sequence_number: Optional[int] = None) -> str:
        """使用硅基流动API合成语音"""
        # 确定语音类型
        voice_name = self.config["voice_name"].get(speaker, self.config["voice_name"]["Host"])
        
        # 根据硅基流动文档，对话文本需要使用[S1]、[S2]、[S3]等标签
        # 将文本转换为硅基流动要求的格式
        # 支持多个嘉宾的区分，使用不同的S标签
        
        # 检查是否为批量合成（speaker为"Combined"且文本包含多个标签）
        if speaker == "Combined" and any(f"[S{i}]" in text for i in range(1, 6)):
            # 批量合成模式：文本已经包含标签，直接使用
            formatted_text = text
            logger.info(f"Using batch synthesis mode for SiliconFlow TTS")
        else:
            # 单条合成模式：根据speaker添加标签
            logger.info(f"speaker: {speaker}, text: {text}")
            if speaker == "Host (Jane)":
                formatted_text = f"[S1]{text}"
            elif speaker == "Guest":
                formatted_text = f"[S2]{text}"
            elif speaker == "Guest 2":
                formatted_text = f"[S3]{text}"
            elif speaker == "Guest 3":
                formatted_text = f"[S4]{text}"
            elif speaker == "Guest 4":
                formatted_text = f"[S5]{text}"
            else:
                # 如果有其他speaker类型，默认使用S2标签
                formatted_text = f"[S2]{text}"
        
        # 硅基流动TTS API调用
        for attempt in range(self.config["retry_attempts"]):
            try:
                # 硅基流动TTS API端点
                url = "https://api.siliconflow.cn/v1/audio/speech"
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model_id,
                    "input": formatted_text,
                    "voice": voice_name,
                    "response_format": "mp3",
                    "speed": self.config["speed"]
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                
                # 生成唯一文件名，使用speaker+sequence_number+timestamp格式
                timestamp = int(time.time())
                if sequence_number is not None:
                    filename = f"siliconflow_audio_{speaker}_{sequence_number}_{timestamp}.mp3"
                else:
                    filename = f"siliconflow_audio_{speaker}_{timestamp}.mp3"
                
                # 如果指定了输出目录，使用该目录，否则使用当前目录
                if output_dir:
                    file_path = os.path.join(output_dir, filename)
                else:
                    file_path = filename
                
                # 保存音频文件
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return file_path
                
            except Exception as e:
                if attempt == self.config["retry_attempts"] - 1:  # Last attempt
                    raise Exception(f"硅基流动TTS API错误: {str(e)}")
                time.sleep(self.config["retry_delay"])  # Wait for X second before retrying