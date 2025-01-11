# project/backend/test/test_database.py

import pytest
from ..models.models import User, ChatSession, Message
from datetime import datetime

def test_create_user(test_db):
    """测试用户创建"""
    user = User(
        username="testuser",
        email="test@example.com"
    )
    test_db.add(user)
    test_db.commit()
    
    db_user = test_db.query(User).filter(User.username == "testuser").first()
    assert db_user is not None
    assert db_user.email == "test@example.com"

def test_create_chat_session(test_db):
    """测试聊天会话创建"""
    # 创建用户
    user = User(username="testuser", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    
    # 创建聊天会话
    chat_session = ChatSession(
        user_id=user.id,
        title="Test Chat"
    )
    test_db.add(chat_session)
    test_db.commit()
    
    db_session = test_db.query(ChatSession).filter(
        ChatSession.user_id == user.id
    ).first()
    assert db_session is not None
    assert db_session.title == "Test Chat"
    assert db_session.title == "Test Chat"