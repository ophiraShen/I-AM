#I-AM/project/backend/models/meditation.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Meditation(BaseModel):
    __tablename__ = "meditations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    audio_url = Column(String(200), nullable=False)
    script = Column(JSON, nullable=False)  # 存储冥想脚本

    # 关系定义
    user = relationship("User", back_populates="meditations")
    chat = relationship("Chat", back_populates="meditations") 