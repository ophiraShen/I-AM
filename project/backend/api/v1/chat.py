#I-AM/project/backend/api/v1/chat.py
from typing import List, Any
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import AIMessage
import asyncio
import time
import random

from api.deps import get_db, get_current_active_user
from app.security import verify_token
from crud import chat as chat_crud
from crud.user import get_user_by_username
from schemas.chat import ChatCreate, ChatUpdate, ChatResponse, Message
from schemas.user import UserInDB
from agents.chat_agent import ChatAgent

router = APIRouter()
chat_agent = ChatAgent()

@router.post("/create", response_model=ChatResponse)
async def create_chat(
    *,
    db: AsyncSession = Depends(get_db),
    chat_in: ChatCreate,
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """创建新对话"""
    chat = await chat_crud.create_chat(db, current_user, chat_in)
    return chat

@router.get("/sessions", response_model=List[ChatResponse])
async def get_all_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """获取用户的所有对话会话列表"""
    chats = await chat_crud.get_user_chats(db, current_user)
    return chats

@router.get("/sessions/{session_id}", response_model=ChatResponse)
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """获取单个对话的所有消息"""
    chat = await chat_crud.get_chat_by_session(db, current_user, session_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat

@router.post("/session", response_model=ChatResponse)
async def create_session(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """创建新的对话会话"""
    # 生成唯一的会话ID：用户名_时间戳_随机数
    session_id = f"{current_user.username}_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # 创建新的对话
    chat_in = ChatCreate(session_id=session_id, messages=[])
    chat = await chat_crud.create_chat(db, current_user, chat_in)
    return chat

@router.websocket("/ws/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket 对话连接"""
    await websocket.accept()
    try:
        # 获取认证信息
        auth = await websocket.receive_text()
        try:
            # 验证用户
            token_data = verify_token(auth)
            user = await get_user_by_username(db, token_data["username"])
            if not user:
                await websocket.send_text("认证失败：用户不存在")
                await websocket.close()
                return
            if not user.is_active:
                await websocket.send_text("认证失败：用户未激活")
                await websocket.close()
                return
            
            # 认证成功通知
            await websocket.send_text("认证成功")
            
        except Exception as e:
            await websocket.send_text(f"认证失败：{str(e)}")
            await websocket.close()
            return

        while True:
            # 接收消息
            message = await websocket.receive_text()
            print(f"Received message: {message}")
            
            # 获取对话会话
            chat = await chat_crud.get_chat_by_session(db, user, session_id)
            if not chat:
                # 如果对话不存在，创建新对话
                chat_in = ChatCreate(session_id=session_id, messages=[])
                chat = await chat_crud.create_chat(db, user, chat_in)
            
            # 确保 messages 是列表
            if not chat.messages:
                chat.messages = []
            
            full_response = ""
            try:
                # 处理聊天响应
                seen_responses = set()
                async for chunk in chat_agent.chat(message, thread_id=session_id):
                    if isinstance(chunk, dict) and "messages" in chunk:
                        for msg in chunk["messages"]:
                            if (isinstance(msg, AIMessage) and 
                                msg.content not in seen_responses):
                                await websocket.send_text(msg.content)
                                seen_responses.add(msg.content)
                                full_response = msg.content
                
                # 更新对话历史
                if full_response:
                    # 添加新的消息到现有消息列表
                    new_messages = chat.messages + [
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": full_response}
                    ]
                    
                    # 更新对话
                    chat_update = ChatUpdate(messages=new_messages)
                    updated_chat = await chat_crud.update_chat(db, chat, chat_update)
                    
                    # 打印调试信息
                    print("Updated chat messages:", updated_chat.messages)
                    
            except Exception as e:
                print(f"Error in chat processing: {str(e)}")
                await websocket.send_text(f"抱歉，出现了一些问题：{str(e)}")
                
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for session {session_id}")

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Any:
    """删除对话会话"""
    # 获取对话
    chat = await chat_crud.get_chat_by_session(db, current_user, session_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # 删除对话
    await chat_crud.delete_chat(db, current_user, chat.id)
    return {"status": "success", "message": "Chat session deleted"} 