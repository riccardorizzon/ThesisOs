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


def make_memory_context_node(memory_service: MemoryService | None = None):
    svc = memory_service or MemoryService()

    async def memory_context_node(state: GraphState, config: RunnableConfig) -> dict:
        thread_id = (config.get("configurable") or {}).get("thread_id")
        ctx = await svc.load_prompt_context(conversation_id=thread_id)
        text = render_prompt_context(ctx)
        if not text:
            return {}
        system = Message(role="system", content=text)
        return {"messages": [system, *state.messages]}

    return memory_context_node
