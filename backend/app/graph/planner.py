"""Planner LangGraph node — refined plan + TaskRef (M5, ADR-0027)."""

from __future__ import annotations

import uuid

from app.graph.orchestration.llm import extract_json_object, request_json
from app.graph.orchestration.messages import build_orchestration_user_block
from app.graph.orchestration.prompts import PLANNER_SYSTEM
from app.llm.base import LLMClient
from app.schemas.graph_state import AgentError, GraphState, Plan, TaskRef


def _parse_planner_payload(data: dict, *, existing_task: TaskRef | None) -> tuple[Plan, TaskRef | None, bool, str | None]:
    """Return (plan, task, unplannable, error_message)."""
    unplannable = bool(data.get("unplannable"))
    if unplannable:
        return Plan(steps=[]), None, True, "unplannable"

    raw_steps = data.get("plan_steps")
    steps: list[str] = []
    if isinstance(raw_steps, list):
        steps = [str(s).strip() for s in raw_steps if str(s).strip()]

    if not steps:
        return Plan(steps=[]), None, True, "unplannable"

    title = str(data.get("task_title", "")).strip()
    if not title:
        return Plan(steps=steps), None, True, "unplannable"

    task_id = existing_task.id if existing_task is not None else str(uuid.uuid4())
    return Plan(steps=steps), TaskRef(id=task_id, title=title), False, None


def make_planner_node(llm: LLMClient):
    async def planner_node(state: GraphState) -> dict:
        errors = list(state.errors)
        user_block = build_orchestration_user_block(state, include_plan=True)
        raw = await request_json(llm, system=PLANNER_SYSTEM, user=user_block)
        data = extract_json_object(raw)

        if data is None:
            errors.append(AgentError(agent="planner", message="unplannable"))
            return {"plan": state.plan or Plan(steps=[]), "task": None, "errors": errors}

        plan, task, unplannable, err = _parse_planner_payload(data, existing_task=state.task)
        if unplannable or err:
            errors.append(AgentError(agent="planner", message=err or "unplannable"))
            return {"plan": plan, "task": None, "errors": errors}

        return {"plan": plan, "task": task, "errors": errors}

    return planner_node
