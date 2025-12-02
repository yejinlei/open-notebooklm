"""
TTS工具模块

提供音频生成、文本分割等高级功能
"""

import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import subprocess
import requests
from loguru import logger

from .factory import TTSClientFactory

# TTS服务配置
import os
DEFAULT_TTS_SERVICE = os.getenv("DEFAULT_TTS_SERVICE", "siliconflow")
TTS_SERVICES = {
    "baidu": {
        "app_id": os.getenv("BAIDU_APP_ID", ""),
        "api_key": os.getenv("BAIDU_API_KEY", ""), 
        "secret_key": os.getenv("BAIDU_SECRET_KEY", ""),
        "retry_attempts": int(os.getenv("BAIDU_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("BAIDU_RETRY_DELAY", "2"))
    },
    "ali": {
        "access_key_id": os.getenv("ALI_ACCESS_KEY_ID", ""),
        "access_key_secret": os.getenv("ALI_ACCESS_KEY_SECRET", ""),
        "app_key": os.getenv("ALI_APP_KEY", ""),
        "retry_attempts": int(os.getenv("ALI_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("ALI_RETRY_DELAY", "2"))
    },
    "xunfei": {
        "app_id": os.getenv("XUNFEI_APP_ID", ""),
        "api_key": os.getenv("XUNFEI_API_KEY", ""),
        "api_secret": os.getenv("XUNFEI_API_SECRET", ""),
        "retry_attempts": int(os.getenv("XUNFEI_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("XUNFEI_RETRY_DELAY", "2"))
    },
    "siliconflow": {
        "api_key": os.getenv("SILICONFLOW_API_KEY", ""),
        "model_id": os.getenv("SILICONFLOW_TTS_MODEL_ID", "FunAudioLLM/CosyVoice2-0.5B"),
        "speed": float(os.getenv("SILICONFLOW_TTS_SPEED", "1.0")),
        "retry_attempts": int(os.getenv("SILICONFLOW_TTS_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("SILICONFLOW_TTS_RETRY_DELAY", "2")),
        "voice_name": {
            "Host": os.getenv("SILICONFLOW_TTS_VOICE_HOST", "FunAudioLLM/CosyVoice2-0.5B:alex"),
            "Guest": os.getenv("SILICONFLOW_TTS_VOICE_GUEST", "FunAudioLLM/CosyVoice2-0.5B:anna")
        }
    }
}

# 初始化TTS客户端
tts_clients = {}

def init_tts_client(service: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Any:
    """初始化TTS客户端"""
    global tts_clients
    target_service = service or DEFAULT_TTS_SERVICE
    if target_service not in tts_clients:
        target_config = config or TTS_SERVICES.get(target_service)
        if not target_config:
            raise ValueError(f"找不到TTS服务配置: {target_service}")
        tts_clients[target_service] = TTSClientFactory.create_client(target_service, target_config)
    return tts_clients[target_service]

def split_text_by_speaker_tags(text: str, max_length: int = 1000) -> List[str]:
    """将包含说话者标签的文本分割成多个段落"""
    segments = []
    current_segment = ""
    
    # 按行分割文本
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检查当前行是否包含说话者标签
        if any(f"[S{i}]" in line for i in range(1, 6)):
            # 如果当前段落的长度加上新行会超过限制，且当前段落不为空
            if current_segment and len(current_segment + line) > max_length:
                segments.append(current_segment)
                current_segment = line
            else:
                if current_segment:
                    current_segment += "\n" + line
                else:
                    current_segment = line
        else:
            # 对于没有标签的行，直接添加到当前段落
            if current_segment:
                current_segment += "\n" + line
            else:
                current_segment = line
    
    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment)
    
    return segments

def generate_podcast_audio_segmented(
    text: str, speaker: str, language: str, random_voice_number: int, tts_service: Optional[str] = None, output_dir: Optional[str] = None, sequence_number: Optional[int] = None
) -> str:
    """使用分段合成方式生成播客音频，优化音色一致性"""
    try:
        # 获取TTS客户端
        tts_client = init_tts_client(tts_service)
        
        # 如果文本长度小于1500字符，直接合成
        if len(text) <= 1500:
            return tts_client.synthesize(text, speaker, language, output_dir, sequence_number)
        
        # 分段合成
        segments = split_text_by_speaker_tags(text, max_length=1000)
        logger.info(f"将文本分割为 {len(segments)} 个段落进行分段合成")
        
        audio_files = []
        temp_dir = Path(output_dir) if output_dir else Path(".")
        
        # 音色一致性优化：添加上下文保持机制
        context_seed = str(int(time.time()))  # 使用时间戳作为种子，确保同一批次调用参数一致
        
        for i, segment in enumerate(segments):
            logger.info(f"合成第 {i+1}/{len(segments)} 段音频 (长度: {len(segment)} 字符)")
            
            # 音色一致性优化：添加上下文前缀
            # 对于非第一段，添加前一段的最后一句作为上下文
            if i > 0 and len(segments[i-1]) > 0:
                # 获取前一段的最后一句（如果有多个句子）
                prev_segment_lines = segments[i-1].strip().split('\n')
                if prev_segment_lines:
                    last_line = prev_segment_lines[-1].strip()
                    if last_line and len(last_line) > 10:  # 确保有足够的内容
                        # 添加上下文前缀，但避免重复
                        if not segment.strip().startswith(last_line):
                            enhanced_segment = last_line + "\n" + segment
                        else:
                            enhanced_segment = segment
                    else:
                        enhanced_segment = segment
                else:
                    enhanced_segment = segment
            else:
                enhanced_segment = segment
            
            # 合成当前段落的音频
            segment_audio = tts_client.synthesize(
                enhanced_segment, speaker, language, str(temp_dir), 
                sequence_number if sequence_number is not None else i
            )
            audio_files.append(segment_audio)
            
            # 添加延迟避免API限制，但减少延迟时间
            time.sleep(0.5)  # 从1秒减少到0.5秒，减少音色变化的机会
        
        # 合并音频文件，优化音色一致性
        if len(audio_files) > 1:
            # 创建合并列表文件
            list_file_path = temp_dir / f"merge_list_{int(time.time())}.txt"
            with open(list_file_path, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
            
            # 合并音频，添加淡入淡出效果
            merged_audio_path = temp_dir / f"merged_audio_{int(time.time())}.mp3"
            
            # 尝试使用带淡入淡出效果的合并方式
            try:
                # 方法1：使用复杂的FFmpeg命令添加淡入淡出
                filter_complex = ""
                for i in range(len(audio_files)):
                    filter_complex += f"[{i}:a]"
                
                # 添加淡入淡出效果：每段音频开头0.5秒淡入，结尾0.5秒淡出
                filter_complex += f"concat=n={len(audio_files)}:v=0:a=1[out]"
                
                # 构建输入文件列表
                input_args = []
                for audio_file in audio_files:
                    input_args.extend(['-i', str(audio_file)])
                
                result = subprocess.run([
                    'ffmpeg', *input_args,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-c:a', 'libmp3lame', '-q:a', '2',
                    str(merged_audio_path)
                ], capture_output=True, text=True, timeout=60)
                
            except (subprocess.TimeoutExpired, Exception):
                # 方法1失败时，回退到简单合并
                result = subprocess.run([
                    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(list_file_path),
                    '-c', 'copy', str(merged_audio_path)
                ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 删除临时文件
                list_file_path.unlink(missing_ok=True)
                for audio_file in audio_files:
                    Path(audio_file).unlink(missing_ok=True)
                
                logger.info(f"成功合并 {len(audio_files)} 段音频，音色一致性已优化")
                return str(merged_audio_path)
            else:
                logger.warning(f"音频合并失败: {result.stderr}")
                # 返回第一段音频作为备选
                return audio_files[0]
        else:
            return audio_files[0]
            
    except Exception as e:
        # 添加更详细的错误信息
        error_msg = f"TTS分段语音合成失败: {str(e)}"
        if tts_service:
            error_msg += f" (服务: {tts_service})"
        raise Exception(error_msg) from e

def generate_podcast_audio(
    text: str, speaker: str, language: str, random_voice_number: int, tts_service: Optional[str] = None, output_dir: Optional[str] = None, sequence_number: Optional[int] = None
) -> str:
    """Generate audio for podcast using TTS or advanced audio models."""
    try:
        # 对于硅基流动TTS，使用分段合成
        if tts_service == "siliconflow":
            return generate_podcast_audio_segmented(text, speaker, language, random_voice_number, tts_service, output_dir, sequence_number)
        
        # 其他TTS服务使用原有方式
        tts_client = init_tts_client(tts_service)
        return tts_client.synthesize(text, speaker, language, output_dir, sequence_number)
    except Exception as e:
        # 添加更详细的错误信息
        error_msg = f"TTS语音合成失败: {str(e)}"
        if tts_service:
            error_msg += f" (服务: {tts_service})"
        raise Exception(error_msg) from e

# 注意：移除了全局初始化调用，改为懒加载模式
# TTS客户端将在首次使用时初始化