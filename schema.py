"""
schema.py
"""

from typing import Literal, List

from pydantic import BaseModel, Field


class DialogueItem(BaseModel):
    """单个对话项。"""

    speaker: Literal["Host (Jane)", "Guest"]
    text: str


class ShortDialogue(BaseModel):
    """主持人和嘉宾之间的对话。"""

    scratchpad: str
    name_of_guest: str
    dialogue: List[DialogueItem] = Field(
        ..., description="对话项列表，通常包含11到17个项"
    )


class MediumDialogue(BaseModel):
    """主持人和嘉宾之间的对话。"""

    scratchpad: str
    name_of_guest: str
    dialogue: List[DialogueItem] = Field(
        ..., description="对话项列表，通常包含19到29个项"
    )
