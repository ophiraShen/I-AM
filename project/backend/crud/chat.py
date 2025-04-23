#I-AM/project/backend/crud/chat.py
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.chat import Chat
from models.user import User
from schemas.chat import ChatCreate, ChatUpdate
from app.exceptions import NotFoundException

async def create_chat(
    db: AsyncSession, 
    user: User,
    chat_in: ChatCreate
) -> Chat:
    """创建新对话"""
    db_chat = Chat(
        user_id=user.id,
        session_id=str(uuid4()),
        messages=chat_in.messages
    )
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat

async def get_chat(
    db: AsyncSession, 
    user: User,
    chat_id: int
) -> Optional[Chat]:
    """获取单个对话"""
    result = await db.execute(
        select(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == user.id)
        .options(selectinload(Chat.user))
    )
    return result.scalar_one_or_none()

async def get_chat_by_session(
    db: AsyncSession,
    user: User,
    session_id: str
) -> Optional[Chat]:
    """通过会话ID获取对话，确保只能获取用户自己的对话"""
    result = await db.execute(
        select(Chat)
        .filter(
            Chat.session_id == session_id,
            Chat.user_id == user.id  # 添加用户ID过滤
        )
        .options(selectinload(Chat.user))
    )
    return result.scalar_one_or_none()

async def get_user_chats(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 10
) -> List[Chat]:
    """获取用户的对话列表"""
    result = await db.execute(
        select(Chat)
        .filter(Chat.user_id == user.id)
        .options(selectinload(Chat.user))
        .offset(skip)
        .limit(limit)
        .order_by(Chat.created_at.desc())
    )
    return result.scalars().all()

async def update_chat(
    db: AsyncSession,
    chat: Chat,
    chat_in: ChatUpdate
) -> Chat:
    """更新对话"""
    update_data = chat_in.model_dump(exclude_unset=True)
    
    # 添加调试日志
    print("Updating chat with messages:")
    if 'messages' in update_data:
        for msg in update_data['messages']:
            print(f"{msg['role']}: {msg['content']}")
    
    for field, value in update_data.items():
        setattr(chat, field, value)
    
    await db.commit()
    await db.refresh(chat)
    return chat

async def delete_chat(
    db: AsyncSession,
    user: User,
    chat_id: int
) -> None:
    """删除对话"""
    chat = await get_chat(db, user, chat_id)
    if not chat:
        raise NotFoundException("Chat not found")
    await db.delete(chat)
    await db.commit() 