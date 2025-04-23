#I-AM/project/backend/models/chat.py
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Chat(BaseModel):
    __tablename__ = "chats"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    messages = Column(JSON, nullable=False, default=list)
    
    # 关系定义
    user = relationship("User", back_populates="chats")
    affirmations = relationship("Affirmation", back_populates="chat")
    meditations = relationship("Meditation", back_populates="chat") 