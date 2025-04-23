#I-AM/project/backend/schemas/chat.py
from typing import List, Dict, Optional
from pydantic import Field
from .base import BaseSchema, TimeStampSchema

class Message(BaseSchema):
    """单条消息"""
    role: str
    content: str

class ChatBase(BaseSchema):
    """对话基础信息"""
    session_id: str = Field(..., min_length=1, max_length=50)
    messages: List[Dict] = Field(default_factory=list)

class ChatCreate(ChatBase):
    """创建对话请求"""
    pass

class ChatUpdate(BaseSchema):
    """更新对话请求"""
    messages: Optional[List[Dict]] = None

class ChatInDB(ChatBase, TimeStampSchema):
    """数据库中的对话信息"""
    id: int
    user_id: int

class ChatResponse(ChatBase, TimeStampSchema):
    """对话信息响应"""
    id: int 