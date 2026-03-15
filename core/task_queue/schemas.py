from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
import uuid


class TaskPayload(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str
    priority: int = 5
    status: str = "pending"
    retry_count: int = 0
    project_id: str
    input_data: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    task_id: str
    agent_type: str
    project_id: str
    status: str = "completed"
    output: dict[str, Any] = Field(default_factory=dict)
    tokens_used: int = 0
    error: str | None = None
    fallback_prompt: str | None = None
