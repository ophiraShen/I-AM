#I-AM/project/backend/agents/chat_agent.py
#%%
import sys
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
print(ROOT_DIR)
sys.path.append(str(ROOT_DIR))
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / '.env')

# from utils.paths import ProjectPaths
#%%
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

from .affirmation_agent import AffirmationAgent
from .meditation_agent import MeditationAgent


# 设置日志级别
loggers_to_quiet = [
    'httpx', 'httpcore', 'urllib3', 'requests', 'openai',
    'torch', 'transformers', 'langchain', 'langchain_core',
    'tqdm', 'numba', 'matplotlib'
]

for logger_name in loggers_to_quiet:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logging.getLogger().setLevel(logging.WARNING)

#%%

config_path = ROOT_DIR / 'backend' / 'config' / 'chat.yaml'

def add_log(current_log, new_log: str) -> list[str]:
    if current_log is None:
        return [new_log] if isinstance(new_log, str) else new_log
    elif isinstance(current_log, list):
        return current_log + [new_log] if isinstance(new_log, str) else new_log
    elif isinstance(current_log, str):
        return [current_log, new_log] if isinstance(new_log, str) else new_log
    else:
        return [new_log] if isinstance(new_log, str) else new_log

class OverallState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list, title="对话列表")
    route: Literal["affirmation", "meditation", "normal_chat"] = Field(default="normal_chat", title="当前路由")
    log: Annotated[List[str], add_log] = Field(default_factory=list, title="日志列表")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('log', mode='before')
    def validate_log(cls, v, info):
        if v is None or (isinstance(v, list) and len(v) == 0):
            return []
        if 'log' in info.data:
            return add_log(info.data['log'], v)
        return [v] if isinstance(v, str) else v

    @field_validator('messages', mode='before')
    def validate_messages(cls, v, info):
        if 'messages' in info.data:
            return add_messages(info.data['messages'], v)
        else:
            return v if isinstance(v, list) else [v]

class Router(TypedDict):
    route: Literal["affirmation", "meditation", "normal_chat"]

class ChatAgent:
    def __init__(self):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base='https://api.deepseek.com'
        )
        
        # 加载提示词
        router_prompt_path = self.config['prompts']['router_prompt']
        chat_prompt_path = self.config['prompts']['chat_prompt']

        with open(router_prompt_path, 'r') as file:
            self.router_prompt = file.read().strip()
        with open(chat_prompt_path, 'r') as file:
            self.chat_prompt = file.read().strip()

        # 初始化子模块
        self.affirmation_agent = AffirmationAgent().create_graph()
        self.meditation_agent = MeditationAgent().create_graph()
        
        # 构建对话图
        self.dialogue_graph = self._build_graph()

    def _router_node(self, state: OverallState) -> OverallState:
        router_model = self.llm.with_structured_output(Router)
        messages = [SystemMessage(content=self.router_prompt)] + state.messages
        route = router_model.invoke(messages)
        return {"route": route["route"], "log": "路由已确定"}

    def _normal_chat_agent(self, state: OverallState) -> OverallState:
        prompt = ChatPromptTemplate([
            ("system", self.chat_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]).partial(route=state.route, log="\n".join(state.log))
        
        normal_llm = prompt | self.llm
        response = normal_llm.invoke(state.messages)
        
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
        
        return {"route": "normal_chat", "messages": [response], "log": "常规对话已生成"}

    def _user_feedback_agent(self, state: OverallState) -> OverallState:
        """处理用户反馈"""
        if state.route == "affirmation":
            # 添加确认消息到状态
            return {
                "messages": state.messages + [
                    AIMessage(content="需要生成肯定语吗？请回复 'yes' 或 'no'")
                ],
                "route": "affirmation",
                "log": "等待用户确认肯定语生成"
            }
        elif state.route == "meditation":
            # 添加确认消息到状态
            return {
                "messages": state.messages + [
                    AIMessage(content="需要打开冥想音频吗？请回复 'yes' 或 'no'")
                ],
                "route": "meditation",
                "log": "等待用户确认冥想音频"
            }

    def _build_graph(self):
        workflow = StateGraph(OverallState)
        
        # 添加节点
        workflow.add_node("router_node", self._router_node)
        workflow.add_node("user_feadback_agent", self._user_feedback_agent)
        workflow.add_node("normal_chat_agent", self._normal_chat_agent)
        workflow.add_node("affirmation_agent", self.affirmation_agent)
        workflow.add_node("meditation_agent", self.meditation_agent)

        # 添加边
        def router_condition_edge(state):
            if state.route in ["affirmation", "meditation"]:
                return "user_feadback_agent"
            return "normal_chat_agent"

        def user_feedback_condition_edge(state):
            if state.route == "affirmation":
                return "affirmation_agent"
            elif state.route == "meditation":
                return "meditation_agent"
            return "normal_chat_agent"

        workflow.add_conditional_edges(
            "router_node",
            router_condition_edge,
            {
                "user_feadback_agent": "user_feadback_agent",
                "normal_chat_agent": "normal_chat_agent"
            }
        )

        workflow.add_conditional_edges(
            "user_feadback_agent",
            user_feedback_condition_edge,
            {
                "affirmation_agent": "affirmation_agent",
                "meditation_agent": "meditation_agent",
                "normal_chat_agent": "normal_chat_agent"
            }
        )

        workflow.add_edge("affirmation_agent", "normal_chat_agent")
        workflow.add_edge("meditation_agent", "normal_chat_agent")
        workflow.add_edge(START, "router_node")
        workflow.add_edge("normal_chat_agent", END)

        return workflow.compile(checkpointer=MemorySaver())

    async def chat(self, message: str, thread_id: str):
        """
        处理用户输入并返回响应
        
        Args:
            message: 用户输入的消息
            thread_id: 对话线程ID，用于隔离不同对话
        
        Returns:
            生成的回复消息
        """
        try:
            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }
            
            inputs = {
                "messages": [HumanMessage(content=message)],
                "log": []
            }
            
            # last_response = None
            async for chunk in self._astream(self.dialogue_graph.stream(inputs, config=config, stream_mode="values")):
                if isinstance(chunk, dict) and "messages" in chunk and chunk["messages"]:
                    # 直接返回最后一条消息
                    msg = {"messages": [chunk["messages"][-1]]}
                    if isinstance(msg["messages"][0], AIMessage):
                        last_response = msg["messages"][0].content
                        yield msg
                else:
                    yield chunk
                await asyncio.sleep(0)
                
        except Exception as e:
            logging.error(f"Chat error: {str(e)}")
            raise

    async def _astream(self, generator):
        """将同步生成器转换为异步生成器"""
        for item in generator:
            yield item
            await asyncio.sleep(0)

# %%

if __name__ == "__main__":
    chat_agent = ChatAgent()
    for chunk in chat_agent.chat("你好", "default"):
        print(chunk)
# %%
