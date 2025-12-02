"""
main.py
"""

# Standard library imports
import glob
import os
import shutil
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Optional

# Third-party imports
import gradio as gr
import random
from loguru import logger
from pypdf import PdfReader
from docx import Document
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Local imports
from constants import (
    APP_TITLE,
    CHARACTER_LIMIT,
    ERROR_MESSAGE_NOT_PDF,
    ERROR_MESSAGE_NO_INPUT,
    ERROR_MESSAGE_READING_PDF,
    ERROR_MESSAGE_TOO_LONG,
    GRADIO_CACHE_DIR,
    GRADIO_CLEAR_CACHE_OLDER_THAN,
    LANGUAGE_MAPPING,
    UI_ALLOW_FLAGGING,
    UI_API_NAME,
    UI_CACHE_EXAMPLES,
    UI_CONCURRENCY_LIMIT,
    UI_DESCRIPTION,
    UI_EXAMPLES,
    UI_INPUTS,
    UI_OUTPUTS,
    UI_SHOW_API,
)
from prompts import (
    LANGUAGE_MODIFIER,
    LENGTH_MODIFIERS,
    QUESTION_MODIFIER,
    SYSTEM_PROMPT,
    TONE_MODIFIER,
)
from schema import DialogueItem, ShortDialogue, MediumDialogue, LongDialogue
from utils import generate_script
from tts import generate_podcast_audio
from tool import process_files, process_url


def generate_podcast(
    files: List[str],
    url: Optional[str],
    question: Optional[str],
    tone: Optional[str],
    length: Optional[str],
    language: str,
    llm_platform: str,
    tts_service: str
) -> Tuple[str, str]:
    """Generate the audio and transcript from the PDFs and/or URL."""

    text = ""

    # Choose random number from 0 to 8
    random_voice_number = random.randint(0, 8) # this is for suno model

    # 移除对旧TTS服务的支持检查，百度TTS支持所有语言

    # Check if at least one input is provided
    if not files and not url:
        raise gr.Error(ERROR_MESSAGE_NO_INPUT)

    # Process PDFs and Word documents if any
    if files:
        try:
            files_text = process_files(files)
            if files_text:
                text += files_text + "\n\n"
        except ValueError as e:
            # 重新抛出不支持文件类型的错误
            raise gr.Error(str(e))
        except Exception as e:
            raise gr.Error(f"读取文件时出错: {str(e)}")

    # Process URL if provided
    if url:
        try:
            url_text = process_url(url)
            if url_text:
                text += "\n\n" + url_text
            else:
                logger.warning(f"URL解析成功，但未提取到文本: {url}")
                # 继续执行，不中断流程
        except ValueError as e:
            raise gr.Error(str(e))
        except Exception as e:
            # 捕获所有异常，提供更友好的错误信息
            raise gr.Error(f"处理URL时出错: {str(e)}")

    # Check total character count
    if len(text) > CHARACTER_LIMIT:
        raise gr.Error(ERROR_MESSAGE_TOO_LONG)

    # Modify the system prompt based on the user input
    modified_system_prompt = SYSTEM_PROMPT

    if question:
        modified_system_prompt += f"\n\n{QUESTION_MODIFIER} {question}"
    if tone:
        modified_system_prompt += f"\n\n{TONE_MODIFIER} {tone}."
    if length:
        modified_system_prompt += f"\n\n{LENGTH_MODIFIERS[length]}"
    if language:
        modified_system_prompt += f"\n\n{LANGUAGE_MODIFIER} {language}."

    # Call the LLM with improved error handling
    try:
        if length == "短 (1-2分钟)":
            llm_output = generate_script(modified_system_prompt, text, ShortDialogue, llm_platform)
        elif length == "长 (15-20分钟)":
            llm_output = generate_script(modified_system_prompt, text, LongDialogue, llm_platform)
        else:
            llm_output = generate_script(modified_system_prompt, text, MediumDialogue, llm_platform)

        logger.info(f"Generated dialogue: {llm_output}")
    except Exception as e:
        logger.error(f"大模型调用失败: {str(e)}")
        raise gr.Error(f"生成播客脚本失败: {str(e)}")

    # Create a unique temporary directory for this podcast generation session
    session_id = str(int(time.time()))
    
    # 生成基于文件名的目录名
    import re
    if files:
        # 获取第一个文件名（不含扩展名）
        first_file = Path(files[0])
        filename = first_file.stem  # 获取文件名（不含扩展名）
        # 清理文件名，只保留字母、数字、下划线和连字符
        filename_clean = re.sub(r'[^\w\-]', '_', filename)
        # 限制文件名长度
        filename_clean = filename_clean[:30] if len(filename_clean) > 30 else filename_clean
        dir_name = f"{filename_clean}_{session_id}"
    else:
        # 如果没有文件上传，使用URL的简化版本或默认值
        if url:
            url_simplified = re.sub(r'[^\w\-]', '_', url[:20])
            filename_clean = url_simplified
        else:
            filename_clean = "url"
        dir_name = f"{filename_clean}_{session_id}"
    
    podcast_temp_dir = Path(GRADIO_CACHE_DIR) / dir_name
    podcast_temp_dir.mkdir(exist_ok=True)
    
    logger.info(f"Created temporary directory for podcast: {podcast_temp_dir}")

    # Process the dialogue
    audio_segments = []
    transcript = ""
    total_characters = 0
    
    # 使用新的语言映射
    language_for_tts = LANGUAGE_MAPPING[language]
    
    # 检查是否为硅基流动TTS服务，需要批量合成
    if tts_service == "siliconflow":
        # 硅基流动需要一次性调用API来保持音色一致性
        # 将所有对话内容合并成一个文本，使用标签区分不同角色
        combined_text = ""
        for i, line in enumerate[DialogueItem](llm_output.dialogue):
            logger.info(f"Preparing audio for {line.speaker}: {line.text}")
            if line.speaker == "Host (Jane)":
                speaker = f"**Host**: {line.text}"
                # 硅基流动使用[S1]标签表示主持人
                tts_text = f"[S1]{line.text}"
            elif line.speaker == "Guest":
                speaker = f"**{llm_output.name_of_guest}**: {line.text}"
                # 硅基流动使用[S2]标签表示嘉宾
                tts_text = f"[S2]{line.text}"
            elif line.speaker == "Guest 2":
                speaker = f"**{llm_output.name_of_guest} 2**: {line.text}"
                # 硅基流动使用[S3]标签表示第二个嘉宾
                tts_text = f"[S3]{line.text}"
            elif line.speaker == "Guest 3":
                speaker = f"**{llm_output.name_of_guest} 3**: {line.text}"
                # 硅基流动使用[S4]标签表示第三个嘉宾
                tts_text = f"[S4]{line.text}"
            elif line.speaker == "Guest 4":
                speaker = f"**{llm_output.name_of_guest} 4**: {line.text}"
                # 硅基流动使用[S5]标签表示第四个嘉宾
                tts_text = f"[S5]{line.text}"
            else:
                speaker = f"**{line.speaker}**: {line.text}"
                # 默认使用S2标签
                tts_text = f"[S2]{line.text}"
            transcript += speaker + "\n\n"
            total_characters += len(line.text)
            combined_text += tts_text + "\n"
        
        # 一次性调用硅基流动TTS API合成整个对话
        logger.info(f"Calling SiliconFlow TTS API with combined text (length: {len(combined_text)})")
        audio_file_path = generate_podcast_audio(
            combined_text, "Combined", language_for_tts, random_voice_number, tts_service, str(podcast_temp_dir), 0
        )
        
        # 将合成的音频文件添加到列表
        audio_segments.append(audio_file_path)
    else:
        # 其他TTS服务使用逐条合成的方式
        for i, line in enumerate[DialogueItem](llm_output.dialogue):
            logger.info(f"Generating audio for {line.speaker}: {line.text}")
            if line.speaker == "Host (Jane)":
                speaker = f"**Host**: {line.text}"
            else:
                speaker = f"**{llm_output.name_of_guest}**: {line.text}"
            transcript += speaker + "\n\n"
            total_characters += len(line.text)

            # Get audio file path with sequence number
            audio_file_path = generate_podcast_audio(
                line.text, line.speaker, language_for_tts, random_voice_number, tts_service, str(podcast_temp_dir), i
            )
            
            # Add audio file path directly to the list
            audio_segments.append(audio_file_path)

    # Merge all audio segments into a single podcast file using FFmpeg
    if not audio_segments:
        raise gr.Error("No audio files were generated")
    
    # Create a list file for FFmpeg concatenation
    list_file_path = podcast_temp_dir / "audio_list.txt"
    with open(list_file_path, 'w', encoding='utf-8') as f:
        for audio_file in audio_segments:
            f.write(f"file '{audio_file}'\n")
    
    # Generate merged audio file with filename+timestamp format
    merged_audio_path = podcast_temp_dir / f"{filename_clean}_{session_id}.mp3"
    
    try:
        # Use FFmpeg to concatenate audio files with improved parameters
        import subprocess
        result = subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', str(list_file_path),
            '-c', 'libmp3lame', '-q:a', '2', '-ar', '44100', '-ac', '2', str(merged_audio_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"FFmpeg concatenation failed: {result.stderr}")
            # Fallback: Try alternative FFmpeg command
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', f"concat:{'|'.join(audio_segments)}",
                    '-c', 'libmp3lame', '-q:a', '2', '-ar', '44100', '-ac', '2', str(merged_audio_path)
                ], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.warning(f"Alternative FFmpeg concatenation also failed: {result.stderr}")
                    # Fallback to first audio file if both FFmpeg commands fail
                    temporary_file = Path(audio_segments[0])
                else:
                    temporary_file = merged_audio_path
                    logger.info(f"Successfully merged {len(audio_segments)} audio files into: {temporary_file}")
            except Exception as alt_e:
                logger.warning(f"Alternative FFmpeg command failed: {alt_e}")
                # Fallback to first audio file if FFmpeg is not available
                temporary_file = Path(audio_segments[0])
        else:
            temporary_file = merged_audio_path
            logger.info(f"Successfully merged {len(audio_segments)} audio files into: {temporary_file}")
            
    except Exception as e:
        logger.warning(f"FFmpeg not available or failed: {e}")
        # Fallback to first audio file if FFmpeg is not available
        temporary_file = Path(audio_segments[0])

    # Clean up old podcast directories (over a day old)
    temporary_directory = GRADIO_CACHE_DIR
    for item in Path(temporary_directory).iterdir():
        if item.is_dir() and "_" in item.name:  # 匹配所有包含下划线的目录（新的命名格式）
            try:
                # Check if directory is older than GRADIO_CLEAR_CACHE_OLDER_THAN
                if time.time() - item.stat().st_mtime > GRADIO_CLEAR_CACHE_OLDER_THAN:
                    # Remove all files in the directory
                    for file_in_dir in item.iterdir():
                        if file_in_dir.is_file():
                            file_in_dir.unlink()
                    # Remove the directory itself
                    item.rmdir()
                    logger.info(f"Cleaned up old podcast directory: {item}")
            except Exception as e:
                logger.warning(f"Failed to clean up directory {item}: {e}")

    logger.info(f"Generated {total_characters} characters of audio in directory: {podcast_temp_dir}")

    return str(temporary_file), transcript


def clear_cache() -> str:
    """手动清理所有缓存文件"""
    cache_dir = Path(GRADIO_CACHE_DIR)
    if cache_dir.exists():
        try:
            # 删除整个缓存目录
            shutil.rmtree(cache_dir)
            # 重新创建空目录
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("手动清理缓存成功")
            return "✅ 缓存清理完成！所有临时MP3文件已删除。"
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return f"❌ 缓存清理失败: {str(e)}"
    else:
        return "ℹ️ 缓存目录不存在，无需清理。"


demo = gr.Interface(
    title=APP_TITLE,
    description=UI_DESCRIPTION,
    fn=generate_podcast,
    inputs=[
        gr.File(
            label=UI_INPUTS["file_upload"]["label"],  # Step 1: File upload
            file_types=UI_INPUTS["file_upload"]["file_types"],
            file_count=UI_INPUTS["file_upload"]["file_count"],
        ),
        gr.Textbox(
            label=UI_INPUTS["url"]["label"],  # Step 2: URL
            placeholder=UI_INPUTS["url"]["placeholder"],
        ),
        gr.Textbox(label=UI_INPUTS["question"]["label"]),  # Step 3: Question
        gr.Dropdown(
            label=UI_INPUTS["tone"]["label"],  # Step 4: Tone
            choices=UI_INPUTS["tone"]["choices"],
            value=UI_INPUTS["tone"]["value"],
        ),
        gr.Dropdown(
            label=UI_INPUTS["length"]["label"],  # Step 5: Length
            choices=UI_INPUTS["length"]["choices"],
            value=UI_INPUTS["length"]["value"],
        ),
        gr.Dropdown(
            choices=UI_INPUTS["language"]["choices"],  # Step 6: Language
            value=UI_INPUTS["language"]["value"],
            label=UI_INPUTS["language"]["label"],
        ),
        gr.Dropdown(
            label=UI_INPUTS["llm_platform"]["label"],  # Step 7: LLM Platform
            choices=UI_INPUTS["llm_platform"]["choices"],
            value=UI_INPUTS["llm_platform"]["value"],
        ),
        gr.Dropdown(
            label=UI_INPUTS["tts_service"]["label"],  # Step 8: TTS Service
            choices=UI_INPUTS["tts_service"]["choices"],
            value=UI_INPUTS["tts_service"]["value"],
        ),
    ],
    outputs=[
        gr.Audio(
            label=UI_OUTPUTS["audio"]["label"], format=UI_OUTPUTS["audio"]["format"]
        ),
        gr.Markdown(label=UI_OUTPUTS["transcript"]["label"]),
    ],
    allow_flagging=UI_ALLOW_FLAGGING,
    api_name=UI_API_NAME,
    theme=gr.themes.Ocean(),
    concurrency_limit=UI_CONCURRENCY_LIMIT,
    examples=UI_EXAMPLES,
    cache_examples=UI_CACHE_EXAMPLES,
)

if __name__ == "__main__":
    demo.launch(show_api=UI_SHOW_API)