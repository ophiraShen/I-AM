# project/backend/test/test_api.py

from fastapi.testclient import TestClient
import pytest

def test_chat_endpoint(client):
    """测试聊天端点"""
    response = client.post(
        "/chat/",
        json={"content": "你好"}
    )
    assert response.status_code == 200
    assert "role" in response.json()
    assert "content" in response.json()
    assert response.json()["role"] == "assistant"

def test_chat_empty_message(client):
    """测试空消息"""
    response = client.post(
        "/chat/",
        json={"content": ""}
    )
    assert response.status_code == 422  # FastAPI 的验证错误

def test_chat_invalid_json(client):
    """测试无效的 JSON"""
    response = client.post(
        "/chat/",
        json={"wrong_field": "test"}
    )
    assert response.status_code == 422