"""Supervisor LangGraph node — coarse plan + route hint (M5, ADR-0027)."""

from __future__ import annotations

from app.graph.companion.protocol import is_companion_open
from app.graph.orchestration.constants import DEFAULT_ROUTE, GROUNDED_ROUTE, WIRED_ROUTES
from app.graph.orchestration.llm import extract_json_object, request_json
from app.graph.orchestration.messages import build_orchestration_user_block, last_user_message
from app.graph.orchestration.prompts import SUPERVISOR_SYSTEM
from app.llm.base import LLMClient
from app.schemas.graph_state import AgentError, GraphState, Plan


def _parse_supervisor_payload(data: dict) -> tuple[Plan, str, bool, str | None]:
    """Return (plan, route_hint, no_objective, error_message)."""
    no_objective = bool(data.get("no_objective"))
    if no_objective:
        return Plan(steps=[]), DEFAULT_ROUTE, True, "no_objective"

    raw_steps = data.get("plan_steps")
    steps: list[str] = []
    if isinstance(raw_steps, list):
        steps = [str(s).strip() for s in raw_steps if str(s).strip()]

    if not steps:
        return Plan(steps=[]), DEFAULT_ROUTE, True, "no_objective"

    route_hint = str(data.get("route_hint", DEFAULT_ROUTE)).strip().lower()
    if route_hint not in WIRED_ROUTES:
        route_hint = GROUNDED_ROUTE if route_hint == "grounded" else DEFAULT_ROUTE

    return Plan(steps=steps), route_hint, False, None


def make_supervisor_node(llm: LLMClient):
    async def supervisor_node(state: GraphState) -> dict:
        errors = list(state.errors)

        if last_user_message(state.messages) is None:
            errors.append(AgentError(agent="supervisor", message="no_objective"))
            return {"plan": Plan(steps=[]), "route": DEFAULT_ROUTE, "errors": errors}

        if is_companion_open(last_user_message(state.messages)):
            return {
                "plan": Plan(steps=["Resume the current thesis focus"]),
                "route": DEFAULT_ROUTE,
                "errors": errors,
            }

        user_block = build_orchestration_user_block(state, include_task=True)
        raw = await request_json(llm, system=SUPERVISOR_SYSTEM, user=user_block)
        data = extract_json_object(raw)

        if data is None:
            errors.append(AgentError(agent="supervisor", message="no_objective"))
            return {"plan": Plan(steps=[]), "route": DEFAULT_ROUTE, "errors": errors}

        plan, route_hint, no_objective, err = _parse_supervisor_payload(data)
        if no_objective or err:
            errors.append(AgentError(agent="supervisor", message=err or "no_objective"))
            return {"plan": Plan(steps=[]), "route": DEFAULT_ROUTE, "errors": errors}

        return {"plan": plan, "route": route_hint, "errors": errors}

    return supervisor_node
