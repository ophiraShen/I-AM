#I-AM/project/backend/api/v1/affirmation.py
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_current_active_user
from crud import affirmation as affirmation_crud
from crud import chat as chat_crud
from schemas.affirmation import AffirmationCreate, AffirmationResponse
from schemas.user import UserInDB
from agents.affirmation_agent import AffirmationAgent

router = APIRouter()
affirmation_agent = AffirmationAgent()

@router.post("/generate", response_model=AffirmationResponse)
async def generate_affirmation(
    *,
    db: AsyncSession = Depends(get_db),
    chat_id: int,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """基于对话生成肯定语"""
    # 获取对话内容
    chat = await chat_crud.get_chat(db, current_user, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    try:
        # 使用 AffirmationAgent 生成肯定语
        affirmations = []
        async for response in affirmation_agent.create_graph().stream(
            {"messages": chat.messages}
        ):
            if isinstance(response, dict) and "messages" in response:
                for msg in response["messages"]:
                    if hasattr(msg, 'content'):
                        affirmations.append(msg.content)

        # 创建肯定语记录
        affirmation_in = AffirmationCreate(
            chat_id=chat_id,
            content=affirmations
        )
        return await affirmation_crud.create_affirmation(db, current_user, affirmation_in)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=List[AffirmationResponse])
async def get_affirmation_history(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """获取肯定语历史"""
    affirmations = await affirmation_crud.get_user_affirmations(
        db, current_user, skip=skip, limit=limit
    )
    return affirmations

@router.get("/chat/{chat_id}", response_model=List[AffirmationResponse])
async def get_chat_affirmations(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """获取特定对话的肯定语"""
    affirmations = await affirmation_crud.get_chat_affirmations(
        db, current_user, chat_id
    )
    return affirmations

@router.delete("/{affirmation_id}")
async def delete_affirmation(
    affirmation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """删除肯定语"""
    await affirmation_crud.delete_affirmation(db, current_user, affirmation_id)
    return {"status": "success"} 