#I-AM/project/backend/schemas/affirmation.py
from typing import List
from pydantic import Field
from .base import BaseSchema, TimeStampSchema

class AffirmationBase(BaseSchema):
    """肯定语基础信息"""
    content: List[str] = Field(..., min_items=1)

class AffirmationCreate(AffirmationBase):
    """创建肯定语请求"""
    chat_id: int

class AffirmationInDB(AffirmationBase, TimeStampSchema):
    """数据库中的肯定语信息"""
    id: int
    user_id: int
    chat_id: int

class AffirmationResponse(AffirmationBase, TimeStampSchema):
    """肯定语响应"""
    id: int 