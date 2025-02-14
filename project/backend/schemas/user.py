#I-AM/project/backend/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .base import BaseSchema, TimeStampSchema

class UserBase(BaseSchema):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """用户创建请求"""
    password: str = Field(..., min_length=6, max_length=50)

class UserUpdate(BaseSchema):
    """用户信息更新请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)

class UserInDB(UserBase, TimeStampSchema):
    """数据库中的用户信息"""
    id: int
    is_active: bool
    
class UserResponse(UserBase, TimeStampSchema):
    """用户信息响应"""
    id: int
    is_active: bool

class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None 