#IAM/project/backend/agents/models.py

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Annotated, List, Literal, Dict, Any
from langgraph.graph.message import AnyMessage, add_messages


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
    data: Dict[str, Any] = Field(default_factory=dict, title="数据")
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