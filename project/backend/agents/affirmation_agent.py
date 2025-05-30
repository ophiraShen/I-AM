# I-AM/project/backend/agents/affirmation_agent.py
#%%
import sys
import os
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))
#%%

import yaml
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal, Union
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .llm import get_llm
from .models import OverallState
config_path = os.path.join(ROOT_DIR, 'backend', 'config', 'affirmation.yaml')


class NodeResult(OverallState):
    local_route: Literal["insight_node", "generator_node", "error_node"] = Field(default="insight_node", title="本地路由")
    success: bool = Field(default=True, title="节点执行是否成功")
    error: Optional[str] = Field(default=None, title="错误信息")

class InsightAnalyzer(BaseModel):
    core_needs: Union[str, List[str]] = Field(..., description="用户的核心需求")
    emotional_state: Union[str, List[str]] = Field(..., description="用户的情绪状态")
    key_issues: Union[str, List[str]] = Field(..., description="关键问题点")
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
    def __init__(self, model_type: str = "tongyi"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize LLM
        self.llm = get_llm(model_type=model_type)
        
        # Load prompts
        insight_prompt_path = ROOT_DIR / self.config['prompts']['insight']
        generator_prompt_path = ROOT_DIR / self.config['prompts']['generator']
        with open(insight_prompt_path, 'r', encoding='utf-8') as f:
            self.insight_prompt = f.read()
        with open(generator_prompt_path, 'r', encoding='utf-8') as f:
            self.generator_prompt = f.read()
        
    async def create_insight(self, state: NodeResult, config) -> NodeResult:
        try:
            conversation_content = ""
            for message in state.messages:
                if isinstance(message, HumanMessage):
                    conversation_content += f"user: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation_content += f"assistant: {message.content}\n"
                else:
                    continue
            logging.info(f"[肯定语][分析] 对话内容: {conversation_content}")
                    
            insight_prompt = ChatPromptTemplate([
                ("system", self.insight_prompt),
                ("human", "{conversation}")
            ])
            generate_insight_chain = insight_prompt | self.llm.with_structured_output(InsightAnalyzer, method="function_calling")
            insight = await generate_insight_chain.ainvoke({"conversation": conversation_content}, config)
            logging.info(f"[肯定语][分析] insight: {insight.as_str}")
            
            # print("===========insight===========")
            # print(insight.as_str)
            # print(state.data)
            # print("===========insight===========")

            # 保存分析结果
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = ROOT_DIR / self.config['paths']['insight_output_path'] / f"{timestamp}.yaml"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump({"insight": insight.as_str}, f, allow_unicode=True)
            logging.info(f"[肯定语][分析] 分析结果已保存: {output_path}")
                
            return NodeResult(
                local_route="insight_node", 
                route="affirmation", 
                data={"conversation": conversation_content, "insight": insight.as_str}, 
                log=f"对话分析成功，已保存至 {output_path}"
            )
        except Exception as e:
            logging.error(f"[肯定语][分析] 失败: {str(e)}")
            return NodeResult(local_route="insight_node", route="affirmation", success=False, error=str(e), log="对话分析失败。")

    async def create_affirmations(self, state: NodeResult, config) -> NodeResult:
        try:
            # 进度通过 log 字段传递
            log_msg = "正在为您准备个性化肯定语"
            user_message = "请基于以下信息生成个性化肯定语：\n\n对话内容：\n{conversation}\n对话分析：\n{insight}"
            logging.info(f"[肯定语][生成] 输入: conversation={state.data['conversation']}, insight={state.data['insight']}")
            generator_prompt = ChatPromptTemplate([
                ("system", self.generator_prompt),
                ("human", user_message)
            ])
            generate_affirmations_chain = generator_prompt | self.llm.with_structured_output(Affirmations, method="function_calling")
            affirmations = await generate_affirmations_chain.ainvoke(
                {
                    "conversation": state.data["conversation"],
                    "insight": state.data["insight"]
                },
                config
            )
            logging.info(f"[肯定语][生成] 生成结果: {affirmations.as_str}")

            print("===========affirmations===========")
            print(affirmations.as_str)
            print(state.data)
            print("===========affirmations===========")

            # 保存肯定语
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = ROOT_DIR / self.config['paths']['affirmations_output_path'] / f"{timestamp}.yaml"
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump({"affirmations": affirmations.as_str}, f, allow_unicode=True)
            logging.info(f"[肯定语][生成] 肯定语已保存: {output_path}")

            return NodeResult(
                local_route="generator_node",
                route="affirmation", 
                data={"affirmations": affirmations.as_str},
                log="肯定语生成成功"
            )
        except Exception as e:
            logging.error(f"[肯定语][生成] 失败: {str(e)}")
            return NodeResult(route="affirmation", success=False, error=str(e), log="肯定语生成失败")

    def handle_error(self, state: NodeResult) -> NodeResult:
        error_msg = state.error
        logging.error(f"[肯定语][错误] {error_msg}")
        return NodeResult(
            local_route="error_node",
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

        return workflow.compile(checkpointer=MemorySaver())