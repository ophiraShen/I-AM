#I-AM/project/backend/agents/llm.py
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI


def get_llm(model_type: str = "qwen2.5", **kwargs):
    """直接获取 LLM 模型实例"""
    
    # 默认参数
    default_params = {
        "temperature": 0.9,
        "max_tokens": 4096
    }
    # 合并用户传入的参数
    params = {**default_params, **kwargs}
    
    if model_type == "deepseek":
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base='https://api.deepseek.com',
            **params
        )
    elif model_type == "qwen2.5":
        return ChatOpenAI(
            model="qwen2.5",
            api_key="EMPTY",
            base_url=os.getenv("QWEN2.5_API_BASE"),
        )
    elif model_type == "tongyi":
        return ChatOpenAI(
            model=os.getenv("TONGYI_MODEL"),
            api_key=os.getenv("TONGYI_API_KEY"),
            base_url=os.getenv("TONGYI_API_BASE"),
            streaming=True,
        )

    else:
        raise ValueError(f"不支持的模型类型: {model_type}")