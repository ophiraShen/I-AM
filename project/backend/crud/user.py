#I-AM/project/backend/crud/user.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.security import get_password_hash, verify_password
from models.user import User
from schemas.user import UserCreate, UserUpdate
from app.exceptions import BadRequestException

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """通过邮箱获取用户"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """创建新用户"""
    # 检查用户名是否已存在
    if await get_user_by_username(db, username=user_in.username):
        raise BadRequestException("Username already registered")
    
    # 检查邮箱是否已存在
    if await get_user_by_email(db, email=user_in.email):
        raise BadRequestException("Email already registered")
    
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError:
        await db.rollback()
        raise BadRequestException("Database error")

async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """用户认证"""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def update_user(
    db: AsyncSession, user: User, user_in: UserUpdate
) -> User:
    """更新用户信息"""
    update_data = user_in.model_dump(exclude_unset=True)
    
    if update_data.get("password"):
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise BadRequestException("Database error") 