# I-AM/project/backend/agents/affirmation_agent.py
import sys
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / '.env')

import yaml
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field, ConfigDict, field_validator


config_path = ROOT_DIR / 'backend' / 'config' / 'affirmation.yaml'

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
    route: Literal["affirmation", "meditation", "normal_chat"] = Field(default="normal_chat", title="当前路由")
    log: List[str] = Field(default_factory=list, title="日志列表")

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

class NodeResult(OverallState):
    local_route: Literal["insight_node", "generator_node", "error_node"] = Field(default="insight_node", title="本地路由")
    success: bool = Field(default=True, title="节点执行是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, title="节点间传递的数据")
    error: Optional[str] = Field(default=None, title="错误信息")

class InsightAnalyzer(BaseModel):
    core_needs: str = Field(..., description="用户的核心需求")
    emotional_state: List[str] = Field(..., description="用户的情绪状态")
    key_issues: List[str] = Field(..., description="关键问题点")
    suggested_affirmation_count: int = Field(..., description="建议生成的肯定语条数")

    @property
    def as_str(self):
        emotional = ".".join(self.emotional_state)
        key_issues = ".".join(self.key_issues)
        return f"核心需求: {self.core_needs}\n情绪状态: {emotional}\n关键问题点: {key_issues}\n建议生成的肯定语条数: {self.suggested_affirmation_count}"

class Affirmations(BaseModel):
    affirmations: List[str] = Field(..., description="生成的肯定语")

    @property
    def as_str(self):
        return "\n".join(self.affirmations)

    @property
    def to_yaml_dict(self):
        return {
            "affirmations": self.affirmations
        }

class AffirmationAgent:
    def __init__(self):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="deepseek-chat", 
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"), 
            openai_api_base='https://api.deepseek.com'
        )
        
        # Load prompts
        insight_prompt_path = self.config['prompts']['insight']
        generator_prompt_path = self.config['prompts']['generator']
        with open(insight_prompt_path, 'r') as f:
            self.insight_prompt = f.read()
        with open(generator_prompt_path, 'r') as f:
            self.generator_prompt = f.read()
        
    def create_insight(self, state: NodeResult) -> NodeResult:
        try:
            conversation_content = ""
            for message in state.messages:
                if isinstance(message, HumanMessage):
                    conversation_content += f"user: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation_content += f"assistant: {message.content}\n"
                else:
                    continue
                    
            insight_prompt = ChatPromptTemplate([
                ("system", self.insight_prompt),
                ("human", "{conversation}")
            ])
            generate_insight_chain = insight_prompt | self.llm.with_structured_output(InsightAnalyzer)
            insight = generate_insight_chain.invoke({"conversation": conversation_content})
            
            # 保存分析结果
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = self.config['paths']['output_path'] / "insights" / f"{timestamp}.yaml"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump({"insight": insight.as_str}, f, allow_unicode=True)
                
            return NodeResult(
                local_route="insight_node", 
                route="affirmation", 
                data={"conversation": conversation_content, "insight": insight.as_str}, 
                log=f"对话分析成功，已保存至 {output_path}"
            )
        except Exception as e:
            return NodeResult(local_route="insight_node", route="affirmation", success=False, error=str(e), log="对话分析失败。")

    def create_affirmations(self, state: NodeResult) -> NodeResult:
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            user_message = "请基于以下信息生成个性化肯定语：\n\n对话内容：\n{conversation}\n对话分析：\n{insight}"
            generator_prompt = ChatPromptTemplate([
                ("system", self.generator_prompt),
                ("human", user_message)
            ])
            generate_affirmations_chain = generator_prompt | self.llm.with_structured_output(Affirmations)
            affirmations = generate_affirmations_chain.invoke(
                {
                    "conversation": state.data["conversation"],
                    "insight": state.data["insight"]
                }
            )
            
            # 保存生成的肯定语
            output_path = self.config['paths']['output_path'] / "affirmations" / f"{timestamp}.yaml"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(affirmations.to_yaml_dict, f, allow_unicode=True)

            return NodeResult(
                local_route="generator_node", 
                route="affirmation", 
                log=f"肯定语生成成功。path: {output_path}\n\n肯定语：{affirmations.as_str}"
            )
        except Exception as e:
            return NodeResult(local_route="generator_node", route="affirmation", success=False, error=str(e), log="肯定语生成失败")

    def handle_error(self, state: NodeResult) -> NodeResult:
        error_msg = state.error
        return NodeResult(
            route="affirmation",
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
        
        workflow.add_node("insight_node", self.create_insight)
        workflow.add_node("generator_node", self.create_affirmations)
        workflow.add_node("error_node", self.handle_error)

        workflow.add_conditional_edges(
            "insight_node",
            self.check_success,
            {
                "success_node": "generator_node",
                "error_node": "error_node"
            }
        )
        workflow.add_conditional_edges(
            "generator_node",
            self.check_success,
            {
                "success_node": END,
                "error_node": "error_node"
            }
        )

        workflow.add_edge(START, "insight_node")
        workflow.add_edge("error_node", END)

        return workflow.compile()