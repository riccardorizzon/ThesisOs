from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class Plan(BaseModel):
    steps: list[str] = []


class RetrievedChunk(BaseModel):
    chunk_id: str
    score: float
    content: str


class CitationRef(BaseModel):
    source_id: str
    locator: str | None = None


class MemoryOp(BaseModel):
    op: str          # upsert | delete
    kind: str        # user|thesis|concept|citation|decision|editable
    key: str
    content: str | None = None


class Critique(BaseModel):
    issues: list[str] = []
    passed: bool = False


class TaskRef(BaseModel):
    id: str
    title: str


class AgentError(BaseModel):
    agent: str
    message: str


class GraphState(BaseModel):
    messages: list[Message]
    plan: Plan | None = None
    route: str | None = None
    retrieved_context: list[RetrievedChunk] = Field(default_factory=list)
    draft: str | None = None
    citations: list[CitationRef] = Field(default_factory=list)
    memory_ops: list[MemoryOp] = Field(default_factory=list)
    critique: Critique | None = None
    task: TaskRef | None = None
    errors: list[AgentError] = Field(default_factory=list)
