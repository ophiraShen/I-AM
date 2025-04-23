#I-AM/project/backend/schemas/meditation.py
from typing import Dict
from pydantic import Field, HttpUrl
from .base import BaseSchema, TimeStampSchema

class MeditationBase(BaseSchema):
    """冥想基础信息"""
    audio_url: HttpUrl
    script: Dict = Field(..., description="冥想引导脚本")

class MeditationCreate(MeditationBase):
    """创建冥想请求"""
    chat_id: int

class MeditationInDB(MeditationBase, TimeStampSchema):
    """数据库中的冥想信息"""
    id: int
    user_id: int
    chat_id: int

class MeditationResponse(MeditationBase, TimeStampSchema):
    """冥想响应"""
    id: int 