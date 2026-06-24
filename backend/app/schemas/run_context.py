from __future__ import annotations

from pydantic import BaseModel, Field


class RunContext(BaseModel):
    """Runtime-only execution metadata (ADR-0014). Never persisted into checkpoints
    and never merged into GraphState."""
    conversation_id: str
    agent_run_id: str
    trace_id: str
    request_id: str
    user_id: str | None = None
    metadata: dict = Field(default_factory=dict)
