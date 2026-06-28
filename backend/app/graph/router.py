"""Router LangGraph node — final M5 route (M5, ADR-0027)."""

from __future__ import annotations

from app.graph.orchestration.coerce import coerce_m5_route
from app.graph.orchestration.constants import DEFAULT_ROUTE
from app.graph.orchestration.llm import extract_json_object, request_json
from app.graph.orchestration.messages import build_orchestration_user_block, last_user_message
from app.graph.orchestration.prompts import ROUTER_SYSTEM
from app.llm.base import LLMClient
from app.schemas.graph_state import AgentError, GraphState


def make_router_node(llm: LLMClient):
    async def router_node(state: GraphState) -> dict:
        errors = list(state.errors)
        user_message = last_user_message(state.messages) or ""
        user_block = build_orchestration_user_block(state, include_plan=True)
        raw = await request_json(llm, system=ROUTER_SYSTEM, user=user_block)
        data = extract_json_object(raw)

        if data is None:
            errors.append(AgentError(agent="router", message="no_route"))
            return {"route": DEFAULT_ROUTE, "errors": errors}

        raw_route = data.get("route")
        if raw_route is None:
            errors.append(AgentError(agent="router", message="no_route"))
            return {"route": DEFAULT_ROUTE, "errors": errors}

        final_route = coerce_m5_route(str(raw_route), user_message=user_message)
        return {"route": final_route, "errors": errors}

    return router_node
