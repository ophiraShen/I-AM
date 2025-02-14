#I-AM/project/backend/models/__init__.py
from .base import BaseModel
from .user import User
from .chat import Chat
from .affirmation import Affirmation
from .meditation import Meditation

# 用于数据库迁移
__all__ = ["BaseModel", "User", "Chat", "Affirmation", "Meditation"] 