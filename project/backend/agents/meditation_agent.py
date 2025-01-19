import logging

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

import sys
import os
import json
import yaml
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Literal

from meditation_tts import CosyVoice2TTS

# 环境设置
# sys.path.append('/root/autodl-tmp/I-AM/project/backend/agents')
load_dotenv()

# 加载配置
with open('/root/autodl-tmp/I-AM/project/backend/config/meditation.yaml', 'r') as f:
    config = yaml.safe_load(f)


#=======================================================================================
def add_log(current_log, new_log: str) -> list[str]:
    if current_log is None:
        return [new_log]
    elif isinstance(current_log, list):
        return current_log + [new_log]
    elif isinstance(current_log, str):
        return [current_log, new_log]
    else:
        return [new_log]

class OverallState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    messages: List[AnyMessage] = Field(default_factory=list, title="对话列表")
    route: Literal["diary", "meditation", "normal_chat"] = Field(default="normal_chat", title="当前路由")
    log: List[str] = Field(default_factory=list, title="日志列表")

    @field_validator('log', mode='before')
    def validate_log(cls, v, info):
        if v is None or (isinstance(v, list) and len(v) == 0):
            return []
        if 'log' in info.data:
            return add_log(info.data['log'], v)
        return [v] if isinstance(v ,str) else v
        

    @field_validator('messages', mode='before')
    def validate_messages(cls, v, info):
        if 'messages' in info.data:
            return add_messages(info.data['messages'], v)
        else:
            return v if isinstance(v, list) else [v]
#=======================================================================================

# 统一的结果状态类定义
class NodeResult(OverallState):
    success: bool = Field(default=True, title="执行状态")
    data: Optional[Dict[str, Any]] = Field(default=None, title="详细的传递数据")
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

# 初始化 LLM
llm = ChatOpenAI(
    model="deepseek-chat", 
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"), 
    openai_api_base='https://api.deepseek.com'
)

# 加载提示词
def load_prompt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

MEDITATION_OUTLINE_PROMPT = load_prompt(config['prompts']['outline'])
MEDITATION_SCRIPT_PROMPT = load_prompt(config['prompts']['script'])
MEDITATION_TONE_PROMPT = load_prompt(config['prompts']['tone'])

# 节点函数定义
def create_meditation_outline(state: NodeResult) -> NodeResult:
    try:
        conversation_content = ""
        for message in state.messages:
            if isinstance(message, HumanMessage):
                conversation_content += f"user: {message.content}\n"
            elif isinstance(message, AIMessage):
                conversation_content += f"assistant: {message.content}\n"
            else:
                continue
        meditation_outline_prompt = ChatPromptTemplate.from_messages([
            ("system", MEDITATION_OUTLINE_PROMPT),  # 使用你已有的提示词
            ("user", "{conversation_content}")
        ])
        generate_meditation_outline = meditation_outline_prompt | llm.with_structured_output(MeditationOutline)
        outline = generate_meditation_outline.invoke({"conversation_content": conversation_content})

        print("大纲已生成")
        
        return NodeResult(route="meditation", data={"outline": outline.as_str}, log="大纲已生成。")
    except Exception as e:
        return NodeResult(route="meditation", success=False, error=str(e), log="大纲生成失败。")

def create_meditation_script(state: NodeResult) -> NodeResult:
    try:
        script_prompt = ChatPromptTemplate.from_messages([
            ("system", MEDITATION_SCRIPT_PROMPT),
            ("user", """请根据以下冥想大纲生成详细的引导词：

        {outline}""")
        ])
        generate_meditation_script = script_prompt | llm.with_structured_output(MeditationScript)
        script = generate_meditation_script.invoke({"outline": state.data['outline']})

        print("脚本已生成")
        
        return NodeResult(route="meditation", data={"script": script.as_str}, log="脚本已生成。")
    except Exception as e:
        return NodeResult(route="meditation", success=False, error=str(e), log="脚本生成失败。")

def create_marked_meditation_script(state: NodeResult) -> NodeResult:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        tone_marking_prompt = ChatPromptTemplate.from_messages([
            ("system", MEDITATION_TONE_PROMPT),
            ("user", "请为以下冥想引导词添加适当的语气标记：\n\n{script}")
        ])
        generate_marked_script = tone_marking_prompt | llm.with_structured_output(MarkedMeditationScript)
        marked_script = generate_marked_script.invoke({"script": state.data['script']})
        marked_script_dict = marked_script.to_yaml_dict()
        output_path = f"{config['paths']['script_output_path']}/{timestamp}.yaml"
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(marked_script_dict, f, indent=2, allow_unicode=True, sort_keys=False)

        print("带标记的脚本已生成")
        
        return NodeResult(route="meditation", data=marked_script_dict, log=f"带标记的脚本已生成。path: {output_path}")
    except Exception as e:
        return NodeResult(route="meditation", success=False, error=str(e), log="带标记的脚本生成失败。")

def create_tts(state: NodeResult) -> NodeResult:
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"{config['tts']['tts_output_path']}/{timestamp}.wav"
        tts = CosyVoice2TTS(
            model_path=config['tts']['tts_model_path'],
            prompts_config_path=config['tts']['tts_resources_config']
        )
        tts.generate_audio(
            texts=state.data,
            voice_type="female1",
            background_music_type="bmusic_02",
            output_path=output_path
        )  

        print(f"音频已生成。path: {output_path}")
        
        return NodeResult(route="meditation", log=f"冥想音频已生成。path: {output_path}\n\n 冥想脚本：{state.data['script']}")
    except Exception as e:
        return NodeResult(route="meditation", success=False, error=str(e), log="冥想音频生成失败。")

# error node
def handle_error(state: NodeResult) -> NodeResult:  # 修改返回类型标注
    error_msg = state.error
    print(f"处理错误: {error_msg}")
    # 返回正确的 NodeResult 对象
    return NodeResult(
        route="meditation",
        success=False,
        error=error_msg,
        log=f"处理错误: {error_msg}"
    )

# condition function
def check_success(state: NodeResult):
    if state.success:
        return "success_node"
    else:
        return "error_node"


# 图定义
def create_meditation_graph():
    

    MeditationGraph = StateGraph(NodeResult)
    
    MeditationGraph.add_node("outline_node", create_meditation_outline)
    MeditationGraph.add_node("script_node", create_meditation_script)
    MeditationGraph.add_node("tone_marking_node", create_marked_meditation_script)
    MeditationGraph.add_node("tts_node", create_tts)
    MeditationGraph.add_node("error_node", handle_error)

    MeditationGraph.add_conditional_edges(
        "outline_node",
        check_success,
        {
            "success_node": "script_node",
            "error_node": "error_node"
        }
    )

    MeditationGraph.add_conditional_edges(
            "script_node",
            check_success,
            {
                "success_node": "tone_marking_node",
                "error_node": "error_node"
            }
        )
        
    MeditationGraph.add_conditional_edges(
        "tone_marking_node",
        check_success,
        {
            "success_node": "tts_node",
            "error_node": "error_node"
        }
    )

    MeditationGraph.add_conditional_edges(
        "tts_node",
        check_success,
        {
            "success_node": END,
            "error_node": "error_node"
        }
    )
    MeditationGraph.add_edge(START, "outline_node")
    MeditationGraph.add_edge("error_node", END)

    meditation_graph = MeditationGraph.compile()

    return meditation_graph

# 主函数
def main():
    meditation_graph = create_meditation_graph()

    # 读取对话数据
    with open('/root/autodl-tmp/I-AM/project/backend/agents/jupyter/conversations_data/meditation.json', 'r', encoding='utf-8') as f:
        conversation_json = json.load(f)

    conversation = ""
    for message in conversation_json['messages']:
        conversation += f"{message['role']}: {message['content']}\n"

    # 执行图
    meditation_graph.invoke(NodeResult(data={"conversation": conversation}))

if __name__ == "__main__":
    main()