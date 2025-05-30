#I-AM/project/backend/agents/chat_agent.py
#%%

import sys
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
print(ROOT_DIR)
sys.path.append(str(ROOT_DIR))
#%%

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / '.env')

import logging
import yaml
import asyncio

from typing import TypedDict, Annotated, Literal, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.types import interrupt, Command

from .affirmation_agent import AffirmationAgent
from .meditation_agent import MeditationAgent
from .llm import get_llm
from .models import OverallState

# 设置日志级别
loggers_to_quiet = [
    'httpx', 'httpcore', 'urllib3', 'requests', 'openai',
    'torch', 'transformers', 'langchain', 'langchain_core',
    'tqdm', 'numba', 'matplotlib'
]

for logger_name in loggers_to_quiet:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logging.getLogger().setLevel(logging.WARNING)

config_path = ROOT_DIR / 'backend' / 'config' / 'chat.yaml'

class Router(TypedDict):
    route: Literal["affirmation", "meditation", "normal_chat"]

class ChatAgent:
    def __init__(self, model_type: str = "tongyi"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化 LLM
        self.llm = get_llm(model_type=model_type)

        # print("================")
        # print(self.llm.invoke("你好"))
        # print("================")
        
        # 加载提示词
        router_prompt_path = ROOT_DIR / self.config['prompts']['router_prompt']
        chat_prompt_path = ROOT_DIR / self.config['prompts']['chat_prompt']

        with open(router_prompt_path, 'r', encoding='utf-8') as file:
            self.router_prompt = file.read().strip()
        with open(chat_prompt_path, 'r', encoding='utf-8') as file:
            self.chat_prompt = file.read().strip()

        # 初始化子模块
        self.affirmation_agent = AffirmationAgent(model_type=model_type).create_graph()
        self.meditation_agent = MeditationAgent(model_type=model_type).create_graph()
        
        # 构建对话图
        self.dialogue_graph = self._build_graph()

    async def _router_node(self, state: OverallState, config) -> Command[Literal["user_feadback_agent", "normal_chat_agent"]]:
        router_model = self.llm.with_structured_output(Router, method="function_calling")
        messages = [SystemMessage(content=self.router_prompt)] + state.messages
        route_result = await router_model.ainvoke(messages, config)
        
        if route_result['route'] in ["affirmation", "meditation"]:
            goto = "user_feadback_agent"
        else:
            goto = "normal_chat_agent"
            
        return Command(
            goto=goto,
            update={
                "route": route_result['route'],
                "log": "路由已确定"
            }
        )

    async def _normal_chat_agent(self, state: OverallState, config) -> OverallState:
        affirmations = state.data.get("affirmations", "生成失败")
        audio_url = state.data.get("audio_url", "生成失败")

        prompt = ChatPromptTemplate([
            ("system", self.chat_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]).partial(audio_url=audio_url, affirmations=affirmations)
        
        normal_llm = prompt | self.llm
        response = await normal_llm.ainvoke(state.messages, config)
        
        # # 保存对话记录
        # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # output_path = ProjectPaths.get_timestamp_path(ProjectPaths.CHAT_OUTPUT_DIR, timestamp, suffix=".txt")
        
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     for msg in state.messages + [response]:
        #         if isinstance(msg, HumanMessage):
        #             f.write(f"User: {msg.content}\n")
        #         elif isinstance(msg, AIMessage):
        #             f.write(f"Assistant: {msg.content}\n")
        #         f.write("\n")
        
        return {"route": "normal_chat", "messages": [response], "data": state.data, "log": "常规对话已生成"}

    async def _user_feadback_agent(self, state: OverallState) -> Command[Literal["affirmation_agent", "meditation_agent", "normal_chat_agent"]]:
        """使用interrupt处理用户反馈"""
        if state.route == "affirmation":
            user_approval = interrupt(
                {
                    "question": "是否需要为您提供个性化的肯定语？",
                    "options": ["yes", "no"],
                    "default": "no",
                }
            )
            if user_approval == "yes":
                return Command(goto="affirmation_agent")
            else:
                return Command(goto="normal_chat_agent")
        elif state.route == "meditation":
            user_approval = interrupt(
                {
                    "question": "是否进行冥想音频生成？音频生成大约需要1分钟，请耐心等待哦~~。",
                    "options": ["yes", "no"],
                    "default": "no",
                }
            )
            if user_approval == "yes":
                return Command(goto="meditation_agent")
            else:
                return Command(goto="normal_chat_agent")
        else:
            return Command(goto="normal_chat_agent")

    def _build_graph(self):
        workflow = StateGraph(OverallState)
        
        # 添加节点
        workflow.add_node("router_node", self._router_node)
        workflow.add_node("user_feadback_agent", self._user_feadback_agent)
        workflow.add_node("normal_chat_agent", self._normal_chat_agent)
        workflow.add_node("affirmation_agent", self.affirmation_agent)
        workflow.add_node("meditation_agent", self.meditation_agent)

        # 添加边
        workflow.add_edge("affirmation_agent", "normal_chat_agent")
        workflow.add_edge("meditation_agent", "normal_chat_agent")
        workflow.add_edge(START, "router_node")
        workflow.add_edge("normal_chat_agent", END)

        return workflow.compile(checkpointer=MemorySaver())

    async def chat(self, message: str, thread_id: str, websocket=None):
        """
        处理用户输入并返回响应
        
        Args:
            message: 用户输入的消息
            thread_id: 对话线程ID，用于隔离不同对话
        
        Returns:
            生成的回复消息
        """
        try:
            thread = {
                "configurable": {
                    "thread_id": thread_id
                },
                "websocket": websocket
            }
            inputs = {
                "messages": [HumanMessage(content=message)],
                "log": []
            }
            last_log = None
            logging.info(f"[ChatAgent] chat called, message={message}, thread_id={thread_id}")
            async for stream_mode, chunk in self.dialogue_graph.astream(inputs, config=thread, stream_mode=["messages", "updates"]):
                if stream_mode == "messages":
                    if hasattr(chunk[0], "content") and chunk[0].content:
                        logging.info(f"[ChatAgent] yield message: {chunk[0].content}")
                        yield {"type": "message", "content": chunk[0].content}
                    elif hasattr(chunk[0], "data") and chunk[0].data:
                        if "affirmations" in chunk[0].data:
                            logging.info(f"[ChatAgent] yield affirmation: {chunk[0].data['affirmations']}")
                            yield {"type": "affirmation", "content": chunk[0].data["affirmations"]}
                        if "audio_url" in chunk[0].data:
                            logging.info(f"[ChatAgent] yield audio_url: {chunk[0].data['audio_url']}")
                            yield {"type": "audio", "url": chunk[0].data["audio_url"]}
                    if hasattr(chunk[0], "log") and chunk[0].log and chunk[0].log != last_log:
                        last_log = chunk[0].log
                        logging.info(f"[ChatAgent] progress: {last_log}")
                        if "冥想脚本生成中" in last_log:
                            yield {"type": "progress", "stage": "冥想脚本生成中"}
                        elif "冥想音频生成中" in last_log:
                            yield {"type": "progress", "stage": "冥想音频生成中"}
                        elif "肯定语生成中" in last_log:
                            yield {"type": "progress", "stage": "肯定语生成中"}
                elif stream_mode == "updates":
                    if isinstance(chunk, tuple) and hasattr(chunk[0], "value"):
                        logging.info(f"[ChatAgent] interrupt: {chunk[0].value}")
                        yield {"type": "interrupt", **chunk[0].value}
                    elif isinstance(chunk, dict) and "__interrupt__" in chunk:
                        val = chunk["__interrupt__"]
                        logging.info(f"[ChatAgent] interrupt dict: {val}")
                        if isinstance(val, dict):
                            yield {"type": "interrupt", **val}
                        elif hasattr(val, "value"):
                            yield {"type": "interrupt", **val.value}
                        elif isinstance(val, tuple) and hasattr(val[0], "value"):
                            yield {"type": "interrupt", **val[0].value}
                        else:
                            yield {"type": "interrupt", "raw": str(val)}
                await asyncio.sleep(0)
        except Exception as e:
            logging.error(f"Chat error: {str(e)}")
            raise

    async def resume_chat(self, response: str, thread_id: str, websocket=None):
        """从用户中断处恢复对话流程
        
        Args:
            response: 用户对中断的响应
            thread_id: 对话线程ID
            
        Returns:
            继续的对话流程
        """
        try:
            config = {
                "configurable": {
                    "thread_id": thread_id
                },
                "websocket": websocket
            }
            last_log = None
            async for stream_mode, chunk in self.dialogue_graph.astream(Command(resume=response), config=config, stream_mode=["messages", "updates"]):
                if stream_mode == "messages":
                    if chunk[0].__class__.__name__ == "AIMessageChunk" and hasattr(chunk[0], "content") and chunk[0].content:
                        yield {"type": "message", "content": chunk[0].content}
                    elif hasattr(chunk[0], "data") and chunk[0].data:
                        if "affirmations" in chunk[0].data:
                            yield {"type": "affirmation", "content": chunk[0].data["affirmations"]}
                        if "audio_url" in chunk[0].data:
                            yield {"type": "audio", "url": chunk[0].data["audio_url"]}
                    if hasattr(chunk[0], "log") and chunk[0].log and chunk[0].log != last_log:
                        last_log = chunk[0].log
                        if "冥想脚本生成中" in last_log:
                            yield {"type": "progress", "stage": "冥想脚本生成中"}
                        elif "冥想音频生成中" in last_log:
                            yield {"type": "progress", "stage": "冥想音频生成中"}
                        elif "肯定语生成中" in last_log:
                            yield {"type": "progress", "stage": "肯定语生成中"}
                elif stream_mode == "updates":
                    if isinstance(chunk, tuple) and hasattr(chunk[0], "value"):
                        yield {"type": "interrupt", **chunk[0].value}
                    elif isinstance(chunk, dict) and "__interrupt__" in chunk:
                        val = chunk["__interrupt__"]
                        if isinstance(val, dict):
                            yield {"type": "interrupt", **val}
                        elif hasattr(val, "value"):
                            yield {"type": "interrupt", **val.value}
                        elif isinstance(val, tuple) and hasattr(val[0], "value"):
                            yield {"type": "interrupt", **val[0].value}
                        else:
                            yield {"type": "interrupt", "raw": str(val)}
                    elif isinstance(chunk, dict) and "normal_chat_agent" in chunk:
                        content = chunk["normal_chat_agent"]['data']
                        if "affirmations" in content:
                            yield {"type": "affirmation", "content": content['affirmations']}
                        if "audio_url" in content:
                            yield {"type": "audio", "url": content['audio_url']}
                await asyncio.sleep(0)
        except Exception as e:
            logging.error(f"Resume chat error: {str(e)}")
            raise

    async def _astream(self, generator):
        """将同步生成器转换为异步生成器"""
        for item in generator:
            yield item
            await asyncio.sleep(0)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        chat_agent = ChatAgent(model_type="deepseek")
        async for chunk in chat_agent.chat("你好", "123"):
            print(chunk['content'], end="|", flush=True)
        
        # # 示例：用户响应中断，选择"yes"
        # async for chunk in chat_agent.resume_chat("yes", "123"):
        #     print(chunk, end="|", flush=True)
    
    # 运行异步主函数
    asyncio.run(main())
