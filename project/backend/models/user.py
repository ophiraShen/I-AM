#I-AM/project/backend/models/user.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    # 关系定义
    chats = relationship("Chat", back_populates="user")
    affirmations = relationship("Affirmation", back_populates="user")
    meditations = relationship("Meditation", back_populates="user") 