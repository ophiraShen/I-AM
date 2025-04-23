#I-AM/project/backend/schemas/base.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """所有模式的基类"""
    model_config = ConfigDict(from_attributes=True)

class TimeStampSchema(BaseSchema):
    """包含时间戳的基础模式"""
    created_at: datetime
    updated_at: datetime 