#I-AM/project/backend/models/affirmation.py
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Affirmation(BaseModel):
    __tablename__ = "affirmations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    content = Column(JSON, nullable=False)  # 存储肯定语列表

    # 关系定义
    user = relationship("User", back_populates="affirmations")
    chat = relationship("Chat", back_populates="affirmations") 