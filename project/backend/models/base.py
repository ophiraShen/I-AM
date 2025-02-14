#I-AM/project/backend/models/base.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.database import Base

class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 