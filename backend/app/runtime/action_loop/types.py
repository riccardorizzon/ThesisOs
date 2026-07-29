from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionLoopContext:
    action: str
    project_id: str | None
    selection_text: str | None
    chapter_content: str
    context_summary: str | None


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AssistantTurn:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None


@dataclass(frozen=True)
class ToolCallRecord:
    name: str
    arguments: dict[str, Any]
    result_summary: str


@dataclass(frozen=True)
class LoopStep:
    label: str
    detail: str | None = None


@dataclass
class LoopResult:
    chunks: list  # RetrievedChunk — typed at integration
    steps: list[LoopStep]
    tool_calls: list[ToolCallRecord]
