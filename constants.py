"""
constants.py
"""

import os

from pathlib import Path

# Key constants
APP_TITLE = "AI播客 🎙️"
CHARACTER_LIMIT = 100_000

# Gradio-related constants
GRADIO_CACHE_DIR = "./gradio_cached_examples/tmp/"
GRADIO_CLEAR_CACHE_OLDER_THAN = 1 * 60 * 60  # 1 hour

# Error messages-related constants
ERROR_MESSAGE_NO_INPUT = "请至少提供一个Word/PDF/TXT类型文件或URL。"
ERROR_MESSAGE_NOT_PDF = "提供的文件不是PDF/Word/TXT文档。请只上传PDF/Word/TXT文件。"
ERROR_MESSAGE_NOT_SUPPORTED_IN_MELO_TTS = "所选语言在不使用高级音频生成的情况下不受支持。请启用高级音频生成或选择受支持的语言。"
ERROR_MESSAGE_READING_PDF = "读取PDF文件时出错"
ERROR_MESSAGE_TOO_LONG = "总内容过长。请确保PDF和URL的组合文本少于{CHARACTER_LIMIT}个字符。"

# 大模型平台配置
DEFAULT_LLM_PLATFORM = os.getenv("DEFAULT_LLM_PLATFORM", "siliconflow")

# 百度文心一言 API 相关常量
ERNIE_CONFIG = {
    "api_key": os.getenv("ERNIE_API_KEY"),
    "secret_key": os.getenv("ERNIE_SECRET_KEY"),
    "model_id": os.getenv("ERNIE_MODEL_ID", "ernie-4.0"),
    "max_tokens": int(os.getenv("ERNIE_MAX_TOKENS", "16384")),
    "temperature": float(os.getenv("ERNIE_TEMPERATURE", "0.1")),
}

# 阿里通义千问 API 相关常量
QIANWEN_CONFIG = {
    "api_key": os.getenv("QIANWEN_API_KEY"),
    "secret_key": os.getenv("QIANWEN_SECRET_KEY"),
    "model_id": os.getenv("QIANWEN_MODEL_ID", "qwen-plus"),
    "max_tokens": int(os.getenv("QIANWEN_MAX_TOKENS", "16384")),
    "temperature": float(os.getenv("QIANWEN_TEMPERATURE", "0.1")),
}

# 硅基流动 API 相关常量
SILICONFLOW_CONFIG = {
    "api_key": os.getenv("SILICONFLOW_API_KEY"),
    "model_id": os.getenv("SILICONFLOW_MODEL_ID", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"),
    "max_tokens": int(os.getenv("SILICONFLOW_MAX_TOKENS", "16384")),
    "temperature": float(os.getenv("SILICONFLOW_TEMPERATURE", "0.1")),
    "retry_attempts": int(os.getenv("SILICONFLOW_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("SILICONFLOW_RETRY_DELAY", "2")),
}



# 大模型平台配置映射
LLM_PLATFORMS = {
    "ernie": ERNIE_CONFIG,
    "qianwen": QIANWEN_CONFIG,
    "siliconflow": SILICONFLOW_CONFIG,
}

# TTS服务配置
DEFAULT_TTS_SERVICE = os.getenv("DEFAULT_TTS_SERVICE", "baidu")

# 百度语音合成 API 相关常量
BAIDU_TTS_CONFIG = {
    "app_id": os.getenv("BAIDU_APP_ID"),
    "api_key": os.getenv("BAIDU_API_KEY"),
    "secret_key": os.getenv("BAIDU_SECRET_KEY"),
    "speed": int(os.getenv("BAIDU_TTS_SPEED", "5")),  # 语速，取值0-9，默认为5中语速
    "pitch": int(os.getenv("BAIDU_TTS_PITCH", "5")),  # 音调，取值0-9，默认为5中语调
    "volume": int(os.getenv("BAIDU_TTS_VOLUME", "5")),  # 音量，取值0-9，默认为5中音量
    "per": {
        "Host": "103",  # 度小宇，男声
        "Guest": "105"  # 度小美，女声
    },
    "retry_attempts": int(os.getenv("BAIDU_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("BAIDU_RETRY_DELAY", "5")),  # in seconds
}

# 阿里语音合成 API 相关常量
ALI_TTS_CONFIG = {
    "access_key_id": os.getenv("ALI_ACCESS_KEY_ID"),
    "access_key_secret": os.getenv("ALI_ACCESS_KEY_SECRET"),
    "app_key": os.getenv("ALI_APP_KEY"),
    "voice": {
        "Host": "zh-CN_XiaoyunVoice",  # 阿里云晓云，女声
        "Guest": "zh-CN_YunxiVoice"   # 阿里云云溪，男声
    },
    "speed": float(os.getenv("ALI_TTS_SPEED", "1.0")),  # 语速，取值0.6-2.0，默认为1.0
    "pitch": float(os.getenv("ALI_TTS_PITCH", "1.0")),  # 音调，取值0.6-2.0，默认为1.0
    "volume": float(os.getenv("ALI_TTS_VOLUME", "50")),  # 音量，取值0-100，默认为50
    "retry_attempts": int(os.getenv("ALI_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("ALI_RETRY_DELAY", "5")),  # in seconds
}

# 讯飞语音合成 API 相关常量
XUNFEI_TTS_CONFIG = {
    "app_id": os.getenv("XUNFEI_APP_ID"),
    "api_key": os.getenv("XUNFEI_API_KEY"),
    "api_secret": os.getenv("XUNFEI_API_SECRET"),
    "voice_name": {
        "Host": "xiaoyan",  # 讯飞小燕，女声
        "Guest": "xiaofeng"  # 讯飞小峰，男声
    },
    "speed": int(os.getenv("XUNFEI_TTS_SPEED", "50")),  # 语速，取值0-100，默认为50
    "pitch": int(os.getenv("XUNFEI_TTS_PITCH", "50")),  # 音调，取值0-100，默认为50
    "volume": int(os.getenv("XUNFEI_TTS_VOLUME", "50")),  # 音量，取值0-100，默认为50
    "retry_attempts": int(os.getenv("XUNFEI_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("XUNFEI_RETRY_DELAY", "5")),  # in seconds
}

# 硅基流动语音合成 API 相关常量
SILICONFLOW_TTS_CONFIG = {
    "api_key": os.getenv("SILICONFLOW_API_KEY"),
    "model_id": os.getenv("SILICONFLOW_TTS_MODEL_ID", "fnlp/MOSS-TTSD-v0.5"),
    "voice_name": {
        "Host": "fnlp/MOSS-TTSD-v0.5:alex",    # 男声
        "Guest": "fnlp/MOSS-TTSD-v0.5:anna"     # 女声
    },
    "speed": float(os.getenv("SILICONFLOW_TTS_SPEED", "1.0")),  # 语速，取值0.25-4.0，默认为1.0
    "retry_attempts": int(os.getenv("SILICONFLOW_RETRY_ATTEMPTS", "3")),
    "retry_delay": int(os.getenv("SILICONFLOW_RETRY_DELAY", "5")),  # in seconds
}

# TTS服务配置映射
TTS_SERVICES = {
    "baidu": BAIDU_TTS_CONFIG,
    "ali": ALI_TTS_CONFIG,
    "xunfei": XUNFEI_TTS_CONFIG,
    "siliconflow": SILICONFLOW_TTS_CONFIG,
}

# 语言映射
LANGUAGE_MAPPING = {
    "中文": "zh",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Polish": "pl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
}

# Jina Reader-related constants
JINA_READER_URL = "https://r.jina.ai/"
JINA_RETRY_ATTEMPTS = 3
JINA_RETRY_DELAY = 5  # in seconds

# UI-related constants
UI_DESCRIPTION = """
使用国内AI从PDF和Word文档生成播客。

构建使用：
- [百度文心一言 🤖](https://cloud.baidu.com/product/wenxinworkshop) 
- [百度语音合成 🎤](https://cloud.baidu.com/product/speech/tts)
- [Jina Reader 🔍](https://jina.ai/reader/)

**注意：** 仅处理文本（100k字符限制）。
"""
UI_AVAILABLE_LANGUAGES = list(set(LANGUAGE_MAPPING.keys()))
UI_INPUTS = {
    "file_upload": {
        "label": "1. 📄 上传您的文档文件（支持PDF、Word等格式）",
        "file_types": None,
        "file_count": "multiple",
    },
    "url": {
        "label": "2. 🔗 粘贴URL（可选）",
        "placeholder": "输入URL以包含其内容",
    },
    "question": {
        "label": "3. 🤔 您有特定的问题或主题吗？",
        "placeholder": "输入问题或主题",
    },
    "tone": {
        "label": "4. 🎭 选择语气",
        "choices": ["有趣", "正式"],
        "value": "有趣",
    },
    "length": {
        "label": "5. ⏱️ 选择长度",
        "choices": ["短 (1-2分钟)", "中 (3-5分钟)", "长 (15-20分钟)"],
        "value": "中 (3-5分钟)",
    },
    "language": {
        "label": "6. 🌐 选择语言",
        "choices": UI_AVAILABLE_LANGUAGES,
        "value": "中文",
    },
    "llm_platform": {
        "label": "7. 🤖 选择大模型平台",
        "choices": list(LLM_PLATFORMS.keys()),
        "value": "siliconflow",
    },
    "tts_service": {
        "label": "8. 🎤 选择TTS服务",
        "choices": list(TTS_SERVICES.keys()),
        "value": "baidu",
    },
}
UI_OUTPUTS = {
    "audio": {"label": "🔊 播客", "format": "mp3"},
    "transcript": {
        "label": "📜  transcript",
    },
}
UI_API_NAME = "generate_podcast"
UI_ALLOW_FLAGGING = "never"
UI_CONCURRENCY_LIMIT = 1
UI_EXAMPLES = [
    [
        [str(Path("examples/1310.4546v1.pdf"))],
        "",
        "用5岁孩子能理解的方式解释这篇论文",
        "有趣",
        "短 (1-2分钟)",
        "中文",
        "siliconflow",
        "siliconflow",
        True,
    ],
    [
        [],
        "https://zh.wikipedia.org/wiki/Hugging_Face",
        "Hugging Face是如何变得如此成功的？",
        "有趣",
        "短 (1-2分钟)",
        "中文",
        "siliconflow",
        "siliconflow",
        False,
    ],
    [
        [],
        "https://zh.wikipedia.org/wiki/泰勒·斯威夫特",
        "为什么泰勒·斯威夫特如此受欢迎？",
        "有趣",
        "短 (1-2分钟)",
        "中文",
        "siliconflow",
        "siliconflow",
        False,
    ],
]
UI_CACHE_EXAMPLES = False
UI_SHOW_API = True
