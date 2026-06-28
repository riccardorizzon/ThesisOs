"""Message helpers for orchestration prompts."""

from __future__ import annotations

from app.schemas.graph_state import GraphState, Message, Plan, TaskRef


def last_user_message(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


def format_conversation_for_prompt(messages: list[Message], *, limit: int = 12) -> str:
    """Recent turns for orchestration LLM context (excludes leading system prefixes)."""
    convo = [m for m in messages if m.role in ("user", "assistant")]
    tail = convo[-limit:]
    lines: list[str] = []
    for m in tail:
        lines.append(f"{m.role.upper()}: {m.content.strip()}")
    return "\n".join(lines) if lines else "(no conversation yet)"


def format_plan_for_prompt(plan: Plan | None) -> str:
    if plan is None or not plan.steps:
        return "(no plan yet)"
    return "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan.steps))


def format_task_for_prompt(task: TaskRef | None) -> str:
    if task is None:
        return "(no active task)"
    return f"id={task.id} title={task.title}"


def build_orchestration_user_block(state: GraphState, *, include_plan: bool = False, include_task: bool = False) -> str:
    sections: list[str] = []
    if include_task:
        sections.append(f"Active task:\n{format_task_for_prompt(state.task)}")
    if include_plan:
        sections.append(f"Current plan:\n{format_plan_for_prompt(state.plan)}")
    sections.append(f"Conversation:\n{format_conversation_for_prompt(state.messages)}")
    latest = last_user_message(state.messages)
    if latest:
        sections.append(f"Latest user message:\n{latest}")
    return "\n\n".join(sections)
