"""
utils.py

Functions:
- generate_script: Get the dialogue from the LLM.
- call_llm: Call the LLM with the given prompt and dialogue format.
- parse_url: Parse the given URL and return the text content.
"""

# Standard library imports
import time
from typing import Any, Union, Dict, Optional

# Third-party imports
import requests

# Local imports
import logging
from constants import (
    DEFAULT_LLM_PLATFORM,
    LLM_PLATFORMS,
    JINA_READER_URL,
    JINA_RETRY_ATTEMPTS,
    JINA_RETRY_DELAY,
)
from schema import ShortDialogue, MediumDialogue
from llm import LLMClientFactory

# 配置日志
logger = logging.getLogger(__name__)

# 初始化大模型客户端
llm_client = None

def init_llm_client(platform: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Any:
    """初始化大模型客户端"""
    global llm_client
    
    # 确定目标平台和配置
    target_platform = platform or DEFAULT_LLM_PLATFORM
    target_config = config or LLM_PLATFORMS.get(target_platform)
    
    if not target_config:
        raise ValueError(f"找不到大模型平台配置: {target_platform}")
    
    # 如果指定了不同的平台或客户端尚未初始化，重新初始化客户端
    if not llm_client or (platform and platform != getattr(llm_client, 'platform', None)):
        try:
            llm_client = LLMClientFactory.create_client(target_platform, target_config)
            # 保存平台信息
            llm_client.platform = target_platform
        except Exception as e:
            logger.warning(f"初始化大模型客户端失败: {e}")
            # 如果初始化失败，保持llm_client为None
            llm_client = None
            raise
    
    return llm_client

def generate_script(
    system_prompt: str,
    input_text: str,
    output_model: Union[ShortDialogue, MediumDialogue],
    llm_platform: Optional[str] = None,
) -> Union[ShortDialogue, MediumDialogue]:
    """Get the dialogue from the LLM."""
    
    logger.info("=== 播客脚本生成开始 ===")
    logger.info(f"目标模型: {output_model.__name__}")
    logger.info(f"输入文本长度: {len(input_text)}")

    # Call the LLM for the first time
    logger.info("--- 第一次大模型调用：生成初稿 ---")
    first_draft_dialogue = call_llm(system_prompt, input_text, output_model, llm_platform)
    logger.info("--- 第一次大模型调用完成 ---")

    # 检查返回的是否是Pydantic模型对象
    if hasattr(first_draft_dialogue, 'model_dump_json'):
        # 如果是Pydantic模型对象，使用model_dump_json()
        dialogue_json = first_draft_dialogue.model_dump_json()
    else:
        # 如果是字符串或其他类型，直接使用
        dialogue_json = str(first_draft_dialogue)

    # Call the LLM a second time to improve the dialogue
    logger.info("--- 第二次大模型调用：改进对话 ---")
    system_prompt_with_dialogue = f"{system_prompt}\n\n这是你提供的对话初稿：\n\n{dialogue_json}."
    final_dialogue = call_llm(system_prompt_with_dialogue, "请改进对话，使其更自然、更吸引人。", output_model, llm_platform)
    logger.info("--- 第二次大模型调用完成 ---")
    
    logger.info("=== 播客脚本生成完成 ===")

    return final_dialogue


def call_llm(system_prompt: str, text: str, dialogue_format: Any, platform: Optional[str] = None) -> Any:
    """Call the LLM with the given prompt and dialogue format."""
    try:
        # 获取大模型客户端
        client = init_llm_client(platform)
        
        # 记录大模型交互信息
        logger.info("=== 大模型交互开始 ===")
        logger.info(f"使用平台: {platform or '默认平台'}")
        logger.info(f"系统提示词 (长度: {len(system_prompt)}):\n{system_prompt}")
        logger.info(f"用户输入 (长度: {len(text)}):\n{text}")
        
        # 调用大模型生成对话
        result = client.generate(system_prompt, text, dialogue_format)
        
        # 记录生成结果
        if hasattr(result, 'model_dump_json'):
            # 如果是Pydantic模型对象，记录JSON格式
            result_json = result.model_dump_json(indent=2)
            logger.info(f"生成对话结果 (JSON格式):\n{result_json}")
        else:
            # 如果是字符串或其他类型，直接记录
            logger.info(f"生成对话结果 (文本格式):\n{result}")
        
        logger.info("=== 大模型交互结束 ===")
        
        return result
    except Exception as e:
        # 记录错误信息
        logger.error(f"大模型调用失败: {str(e)}")
        if platform:
            logger.error(f"失败平台: {platform}")
        
        # 添加更详细的错误信息
        error_msg = f"大模型调用失败: {str(e)}"
        if platform:
            error_msg += f" (平台: {platform})"
        raise Exception(error_msg) from e


def parse_url(url: str) -> str:
    """Parse the given URL and return the text content."""
    for attempt in range(JINA_RETRY_ATTEMPTS):
        try:
            full_url = f"{JINA_READER_URL}{url}"
            response = requests.get(full_url, timeout=120)
            response.raise_for_status()  # Raise an exception for bad status codes
            break
        except requests.RequestException as e:
            if attempt == JINA_RETRY_ATTEMPTS - 1:  # Last attempt
                raise ValueError(
                    f"Failed to fetch URL after {JINA_RETRY_ATTEMPTS} attempts: {e}"
                ) from e
            time.sleep(JINA_RETRY_DELAY)  # Wait for X second before retrying
    return response.text



