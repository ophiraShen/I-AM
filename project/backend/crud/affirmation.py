#I-AM/project/backend/crud/affirmation.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.affirmation import Affirmation
from models.user import User
from models.chat import Chat
from schemas.affirmation import AffirmationCreate
from app.exceptions import NotFoundException, BadRequestException

async def create_affirmation(
    db: AsyncSession,
    user: User,
    affirmation_in: AffirmationCreate
) -> Affirmation:
    """创建新的肯定语"""
    # 验证对话存在且属于当前用户
    chat_result = await db.execute(
        select(Chat).filter(
            Chat.id == affirmation_in.chat_id,
            Chat.user_id == user.id
        )
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise NotFoundException("Chat not found")

    db_affirmation = Affirmation(
        user_id=user.id,
        chat_id=affirmation_in.chat_id,
        content=affirmation_in.content
    )
    db.add(db_affirmation)
    await db.commit()
    await db.refresh(db_affirmation)
    return db_affirmation

async def get_affirmation(
    db: AsyncSession,
    user: User,
    affirmation_id: int
) -> Optional[Affirmation]:
    """获取单个肯定语"""
    result = await db.execute(
        select(Affirmation)
        .filter(
            Affirmation.id == affirmation_id,
            Affirmation.user_id == user.id
        )
        .options(selectinload(Affirmation.chat))
    )
    return result.scalar_one_or_none()

async def get_user_affirmations(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 10
) -> List[Affirmation]:
    """获取用户的肯定语列表"""
    result = await db.execute(
        select(Affirmation)
        .filter(Affirmation.user_id == user.id)
        .options(selectinload(Affirmation.chat))
        .offset(skip)
        .limit(limit)
        .order_by(Affirmation.created_at.desc())
    )
    return result.scalars().all()

async def get_chat_affirmations(
    db: AsyncSession,
    user: User,
    chat_id: int
) -> List[Affirmation]:
    """获取特定对话的肯定语列表"""
    result = await db.execute(
        select(Affirmation)
        .filter(
            Affirmation.chat_id == chat_id,
            Affirmation.user_id == user.id
        )
        .options(selectinload(Affirmation.chat))
        .order_by(Affirmation.created_at.desc())
    )
    return result.scalars().all()

async def delete_affirmation(
    db: AsyncSession,
    user: User,
    affirmation_id: int
) -> None:
    """删除肯定语"""
    affirmation = await get_affirmation(db, user, affirmation_id)
    if not affirmation:
        raise NotFoundException("Affirmation not found")
    await db.delete(affirmation)
    await db.commit()

async def create_affirmation_from_agent(
    db: AsyncSession,
    user: User,
    chat_id: int,
    agent_response: dict
) -> Affirmation:
    """从Agent响应创建肯定语记录"""
    try:
        # 验证对话存在且属于当前用户
        chat_result = await db.execute(
            select(Chat).filter(
                Chat.id == chat_id,
                Chat.user_id == user.id
            )
        )
        chat = chat_result.scalar_one_or_none()
        if not chat:
            raise NotFoundException("Chat not found")

        # 从agent响应中提取肯定语
        if not agent_response.get('data') or not agent_response['data'].get('affirmations'):
            raise BadRequestException("No affirmations in agent response")

        # 创建肯定语记录
        db_affirmation = Affirmation(
            user_id=user.id,
            chat_id=chat_id,
            content=agent_response['data']['affirmations']
        )
        
        db.add(db_affirmation)
        await db.commit()
        await db.refresh(db_affirmation)
        
        return db_affirmation
        
    except Exception as e:
        await db.rollback()
        raise BadRequestException(f"Failed to create affirmation: {str(e)}") 