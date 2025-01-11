# project/backend/utils/llm.py

from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class DeepSeekInterface:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
    async def get_response(self, messages: List[Dict[str, str]], 
                          system_prompt: str = "You are a helpful assistant") -> str:
        try:
            # 添加系统提示
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=full_messages,
                max_tokens=1024,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in DeepSeek API call: {str(e)}")
            return None

class GLMInterface:
    def __init__(self):
        # 模型配置
        self.model_name = "/root/autodl-fs/modelscope/glm_4_9b_chat"
        self.max_model_len = 131072
        self.tp_size = 1
        
        # 初始化tokenizer和模型
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        )
        
        self.llm = LLM(
            model=self.model_name,
            tensor_parallel_size=self.tp_size,
            max_model_len=self.max_model_len,
            trust_remote_code=True,
            enforce_eager=True
        )
        
        # 配置生成参数
        self.stop_token_ids = [151329, 151336, 151338]
        self.sampling_params = SamplingParams(
            temperature=0.95,
            max_tokens=1024,
            stop_token_ids=self.stop_token_ids
        )
    
    async def get_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            # 使用tokenizer处理输入
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 生成响应
            outputs = self.llm.generate(
                prompts=inputs,
                sampling_params=self.sampling_params
            )
            
            # 返回生成的文本
            return outputs[0].outputs[0].text
            
        except Exception as e:
            print(f"Error in GLM local model call: {str(e)}")
            return None

# 统一的模型接口
class ModelInterface:
    def __init__(self, model_type: str = "deepseek"):
        self.model_type = model_type
        self.glm = GLMInterface() if model_type == "glm" else None
        self.deepseek = DeepSeekInterface() if model_type == "deepseek" else None
    
    async def get_response(self, messages: List[Dict[str, str]], 
                          system_prompt: str = "You are a helpful assistant") -> str:
        if self.model_type == "glm":
            return await self.glm.get_response(messages)
        elif self.model_type == "deepseek":
            return await self.deepseek.get_response(messages, system_prompt)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")