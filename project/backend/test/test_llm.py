# project/backend/test/test_llm.py

import pytest
from ..utils.llm import GLMInterface, DeepSeekInterface, ModelInterface

@pytest.mark.asyncio
async def test_glm_interface():
    """测试 GLM 模型接口"""
    glm = GLMInterface()
    response = await glm.get_response([
        {"role": "user", "content": "你好"}
    ])
    assert response is not None
    assert isinstance(response, str)

@pytest.mark.asyncio
async def test_deepseek_interface():
    """测试 DeepSeek 模型接口"""
    deepseek = DeepSeekInterface()
    response = await deepseek.get_response([
        {"role": "user", "content": "你好"}
    ])
    assert response is not None
    assert isinstance(response, str)

@pytest.mark.asyncio
async def test_model_interface():
    """测试统一模型接口"""
    # 测试 GLM
    model_glm = ModelInterface(model_type="glm")
    response_glm = await model_glm.get_response([
        {"role": "user", "content": "你好"}
    ])
    assert response_glm is not None

    # 测试 DeepSeek
    model_deepseek = ModelInterface(model_type="deepseek")
    response_deepseek = await model_deepseek.get_response([
        {"role": "user", "content": "你好"}
    ])
    assert response_deepseek is not None