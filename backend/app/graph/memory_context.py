"""Pre-turn memory loader — operational kinds only (M2 spec §9.2).

Loads editable, binding decisions, and pinned user/thesis from MemoryService, renders a system
prefix, and prepends it to wire messages for this turn. Transient only:
no GraphState fields added; ConversationService persists user/assistant only.
"""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig

from app.schemas.graph_state import GraphState, Message
from app.services.memory.render import render_prompt_context
from app.services.memory.service import MemoryService
from app.services.workspace.thesis_sor import THESIS_AGENT_PROJECT_ID


def make_memory_context_node(memory_service: MemoryService | None = None):
    svc = memory_service or MemoryService()

    async def memory_context_node(state: GraphState, config: RunnableConfig) -> dict:
        configurable = config.get("configurable") or {}
        # INV-COMP-6 (ADR-0045): memory rows all belong to the primary thesis
        # project today; never inject them into demo/other projects. Legacy
        # callers without a project_id keep the previous behavior.
        project_id = configurable.get("project_id")
        if project_id is not None and project_id != THESIS_AGENT_PROJECT_ID:
            return {}
        thread_id = configurable.get("thread_id")
        ctx = await svc.load_prompt_context(conversation_id=thread_id)
        text = render_prompt_context(ctx)
        if not text:
            return {}
        system = Message(role="system", content=text)
        return {"messages": [system, *state.messages]}

    return memory_context_node
