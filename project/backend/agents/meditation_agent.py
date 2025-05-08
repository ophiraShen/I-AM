#I-AM/project/backend/agents/meditation_agent.py
import sys
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))
import logging
import uuid

logging.getLogger().setLevel(logging.INFO)

# 设置关键库的日志级别
loggers_to_quiet = [
    'httpx',           # HTTP 客户端库
    'httpcore',        # HTTP 核心库
    'urllib3',         # HTTP 客户端库
    'requests',        # HTTP 客户端库
    'openai',          # OpenAI API 库
    'torch',           # PyTorch
    'transformers',    # Hugging Face Transformers
    'langchain',       # LangChain
    'langchain_core',  # LangChain Core
    'tqdm',           # 进度条库
    'numba',          # Numba
    'matplotlib',      # Matplotlib
]

for logger_name in loggers_to_quiet:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


import json
import yaml
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .llm import get_llm
from .models import OverallState
from .meditation_tts import CosyVoice2TTS


config_path = os.path.join(ROOT_DIR, 'backend', 'config', 'meditation.yaml')

#=======================================================================================
# def add_log(current_log, new_log: str) -> list[str]:
#     if current_log is None:
#         return [new_log]
#     elif isinstance(current_log, list):
#         return current_log + [new_log]
#     elif isinstance(current_log, str):
#         return [current_log, new_log]
#     else:
#         return [new_log]

# class OverallState(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     messages: List[AnyMessage] = Field(default_factory=list, title="对话列表")
#     route: Literal["diary", "meditation", "normal_chat"] = Field(default="normal_chat", title="当前路由")
#     log: List[str] = Field(default_factory=list, title="日志列表")

#     @field_validator('log', mode='before')
#     def validate_log(cls, v, info):
#         if v is None or (isinstance(v, list) and len(v) == 0):
#             return []
#         if 'log' in info.data:
#             return add_log(info.data['log'], v)
#         return [v] if isinstance(v ,str) else v
        

#     @field_validator('messages', mode='before')
#     def validate_messages(cls, v, info):
#         if 'messages' in info.data:
#             return add_messages(info.data['messages'], v)
#         else:
#             return v if isinstance(v, list) else [v]
#=======================================================================================

# 统一的结果状态类定义
class NodeResult(OverallState):
    success: bool = Field(default=True, title="执行状态")
    error: Optional[str] = Field(default=None, title="错误信息")

# Outline Structure
class UserContext(BaseModel):
    main_goal: str = Field(..., title="用户的主要目标或困扰")
    current_state: str = Field(..., title="当前的情绪状态")
    desired_outcome: str = Field(..., title="期望达到的效果")

class ScriptSegment(BaseModel):
    focus: str = Field(..., title="段落主题焦点")
    content_brief: str = Field(..., title="内容简要提示")

class MainGuidance(BaseModel):
    segments: List[ScriptSegment] = Field(..., title="主体引导的段落列表")

class ScriptStructure(BaseModel):
    opening: ScriptSegment = Field(..., title="开场部分")
    main_guidance: MainGuidance = Field(..., title="主体引导部分")
    closing: ScriptSegment = Field(..., title="结束部分")

class MeditationOutline(BaseModel):
    user_context: UserContext = Field(..., title="用户背景信息")
    script_structure: ScriptStructure = Field(..., title="脚本结构")

    @property
    def as_str(self) -> str:
        # 构建用户上下文字符串
        context = (
            f"# 用户背景\n\n"
            f"- 主要目标：{self.user_context.main_goal}\n"
            f"- 当前状态：{self.user_context.current_state}\n"
            f"- 期望效果：{self.user_context.desired_outcome}\n\n"
        )
        
        # 构建脚本结构字符串
        script = (
            f"# 冥想引导词大纲\n\n"
            f"## 开场部分\n"
            f"主题：{self.script_structure.opening.focus}\n"
            f"内容：{self.script_structure.opening.content_brief}\n\n"
            f"## 主体引导\n"
        )
        
        # 添加主体引导的每个段落
        for i, segment in enumerate(self.script_structure.main_guidance.segments, 1):
            script += f"### 第{i}段\n主题：{segment.focus}\n内容：{segment.content_brief}\n\n"
        
        # 添加结束部分
        script += (
            f"## 结束部分\n"
            f"主题：{self.script_structure.closing.focus}\n"
            f"内容：{self.script_structure.closing.content_brief}"
        )
        
        return context + script

# Script Structure
class MeditationScript(BaseModel):
    sequences: List[str] = Field(..., title="引导词序列")

    @property
    def as_str(self) -> str:
        return "\n\n".join(f"text: {item}" for item in self.sequences)

    @property
    def as_yaml(self) -> str:
        return "sequences:\n" + "\n".join(
            f"id: {idx}\ntext: {item}"
            for idx, item in enumerate(self.sequences)
        )

# Tone Marking Structure
class MarkedSequence(BaseModel):
    original_text: str = Field(..., title="原始文本")
    marked_text: str = Field(..., title="带标记的文本")
    duration: int = Field(..., title="持续时间（秒）", ge=2, le=6)

class MarkedMeditationScript(BaseModel):
    sequences: List[MarkedSequence] = Field(..., title="带标记的引导词序列")

    @property
    def as_str(self) -> str:
        return "\n\n".join(
            f"id: {idx}\ntext: {item.marked_text}\nduration: {item.duration}"
            for idx, item in enumerate(self.sequences)
        )
    
    @property
    def as_yaml(self) -> str:
        return "sequences:\n" + "\n".join(
            f"id: {idx}\ntext: \"{item.marked_text}\"\nduration: {item.duration}"
            for idx, item in enumerate(self.sequences)
        )

    def to_yaml_dict(self) -> dict:
        return {
            "sequences": [
                {
                    "id": idx,
                    "text": item.marked_text,
                    "duration": item.duration
                }
                for idx, item in enumerate(self.sequences)
            ]
        }

class MeditationAgent:
    def __init__(self, model_type: str="tongyi"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化 LLM
        self.model_type = model_type
        self.llm = get_llm(model_type=self.model_type)
        
        # Load prompts
        outline_prompt_path = self.config['prompts']['outline']
        script_prompt_path = self.config['prompts']['script']
        tone_prompt_path = self.config['prompts']['tone']

        with open(outline_prompt_path, 'r', encoding='utf-8') as f:  
            self.outline_prompt = f.read()
        with open(script_prompt_path, 'r', encoding='utf-8') as f:
            self.script_prompt = f.read()
        with open(tone_prompt_path, 'r', encoding='utf-8') as f:
            self.tone_prompt = f.read()
            
        # 初始化 TTS
        self.tts = CosyVoice2TTS(
            model_path=self.config['tts']['tts_model_path'],
            prompts_config_path=self.config['tts']['tts_resources_config']
        )

    async def create_meditation_outline(self, state: NodeResult, config) -> NodeResult:
        try:
            # 进度通过 log 字段传递
            log_msg = "冥想脚本生成中"
            conversation_content = ""
            for message in state.messages:
                if isinstance(message, HumanMessage):
                    conversation_content += f"user: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation_content += f"assistant: {message.content}\n"
                else:
                    continue
            meditation_outline_prompt = ChatPromptTemplate.from_messages([
                ("system", self.outline_prompt),
                ("user", "{conversation_content}")
            ])
            generate_meditation_outline = meditation_outline_prompt | self.llm.with_structured_output(MeditationOutline, method="function_calling")
            outline = await generate_meditation_outline.ainvoke({"conversation_content": conversation_content}, config)
            return NodeResult(route="meditation", data={"outline": outline.as_str}, log=log_msg)
        except Exception as e:
            return NodeResult(route="meditation", success=False, error=str(e), log="大纲生成失败。")

    async def create_meditation_script(self, state: NodeResult, config) -> NodeResult:
        try:
            log_msg = "冥想脚本生成中"
            script_prompt = ChatPromptTemplate.from_messages([
                ("system", self.script_prompt),
                ("user", """请根据以下冥想大纲生成详细的引导词：\n\n{outline}""")
            ])
            generate_meditation_script = script_prompt | self.llm.with_structured_output(MeditationScript, method="function_calling")
            script = await generate_meditation_script.ainvoke({"outline": state.data['outline']}, config)
            return NodeResult(route="meditation", data={"script": script.as_str}, log=log_msg)
        except Exception as e:
            return NodeResult(route="meditation", success=False, error=str(e), log="脚本生成失败。")

    async def create_marked_meditation_script(self, state: NodeResult, config) -> NodeResult:
        try:
            log_msg = "冥想脚本生成中"
            tone_marking_prompt = ChatPromptTemplate.from_messages([
                ("system", self.tone_prompt),
                ("user", "请为以下冥想引导词添加适当的语气标记：\n\n{script}")
            ])
            generate_marked_script = tone_marking_prompt | self.llm.with_structured_output(MarkedMeditationScript, method="function_calling")
            marked_script = await generate_marked_script.ainvoke({"script": state.data['script']}, config)
            marked_script_dict = marked_script.to_yaml_dict()
            return NodeResult(route="meditation", data=marked_script_dict, log=log_msg)
        except Exception as e:
            return NodeResult(route="meditation", success=False, error=str(e), log="带标记的脚本生成失败。")

    def create_tts(self, state: NodeResult, session_id=None) -> NodeResult:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        try:
            log_msg = "冥想音频生成中"
            if session_id is None:
                session_id = str(uuid.uuid4())
            output_filename = f"{session_id}_{timestamp}.wav"
            output_dir = os.path.join(ROOT_DIR, "backend", "static", "audio")
            output_path = os.path.join(output_dir, output_filename)
            
            self.tts.generate_audio(
                texts=state.data,
                voice_type="female1",
                background_music_type="bmusic_02",
                output_path=output_path
            )
            audio_url = f"/audio/{output_filename}"
            return NodeResult(route="meditation", data={"audio_url": audio_url}, log=log_msg)
        except Exception as e:
            return NodeResult(route="meditation", success=False, error=str(e), log="冥想音频生成失败。")

    def handle_error(self, state: NodeResult) -> NodeResult:
        error_msg = state.error
        print(f"处理错误: {error_msg}")
        return NodeResult(
            route="meditation",
            success=False,
            error=error_msg,
            log=f"处理错误: {error_msg}"
        )

    def check_success(self, state: NodeResult):
        if state.success:
            return "success_node"
        else:
            return "error_node"

    def create_graph(self) -> Any:
        """创建并返回工作流图"""
        workflow = StateGraph(NodeResult)
        
        # 添加节点
        workflow.add_node("outline_node", self.create_meditation_outline)
        workflow.add_node("script_node", self.create_meditation_script)
        workflow.add_node("tone_marking_node", self.create_marked_meditation_script) 
        workflow.add_node("tts_node", self.create_tts)
        workflow.add_node("error_node", self.handle_error)

        # 添加边
        workflow.add_conditional_edges(
            "outline_node",
            self.check_success,
            {
                "success_node": "script_node",
                "error_node": "error_node"
            }
        )

        workflow.add_conditional_edges(
            "script_node",
            self.check_success,
            {
                "success_node": "tone_marking_node",
                "error_node": "error_node"
            }
        )
        
        workflow.add_conditional_edges(
            "tone_marking_node",
            self.check_success,
            {
                "success_node": "tts_node",
                "error_node": "error_node"
            }
        )

        workflow.add_conditional_edges(
            "tts_node",
            self.check_success,
            {
                "success_node": END,
                "error_node": "error_node"
            }
        )

        workflow.add_edge(START, "outline_node")
        workflow.add_edge("error_node", END)

        return workflow.compile(checkpointer=MemorySaver())