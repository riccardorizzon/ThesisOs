from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.graph.memory_context import make_memory_context_node
from app.graph.prompt_wire import compose_prompt_wire, format_grounding_sources
from app.graph.retriever import make_retriever_node
from app.llm.base import LLMClient
from app.schemas.graph_state import CitationRef, GraphState, Message
from app.services.memory.service import MemoryService
from app.services.retrieval.service import RetrievalService


def make_conversation_node(llm: LLMClient):
    async def conversation_node(state: GraphState) -> dict:
        writer = get_stream_writer()
        wire_messages = compose_prompt_wire(state)
        if state.retrieved_context:
            writer(
                {
                    "type": "sources",
                    "text": "",
                    "sources": format_grounding_sources(state.retrieved_context),
                }
            )
        wire = [{"role": m.role, "content": m.content} for m in wire_messages]
        parts: list[str] = []
        usage: dict = {}
        async for chunk in llm.astream(wire):
            if chunk.text:
                parts.append(chunk.text)
                writer({"type": "token", "text": chunk.text})
            if chunk.metadata.get("usage"):
                usage = chunk.metadata["usage"]
        assistant = Message(role="assistant", content="".join(parts))
        # Task 9 reads usage from the custom stream (not from GraphState),
        # which keeps GraphState frozen (ADR-0007) and avoids a Pydantic
        # unknown-key update error. "text" is included so every custom
        # chunk is shape-compatible with token chunks for stream consumers.
        if usage:
            writer({"type": "usage", "text": "", "usage": usage})
        citations = [
            CitationRef(
                source_id=c.document_id or c.chunk_id,
                locator=(f"p.{c.page_from}" if c.page_from else c.chunk_id),
            )
            for c in state.retrieved_context
        ]
        # Replace semantics: the caller owns message history (DB is the
        # system of record), so no add_messages reducer is needed.
        return {
            "messages": [*state.messages, assistant],
            "draft": assistant.content,
            "citations": citations,
            "errors": list(state.errors),
        }

    return conversation_node


def build_graph(
    llm: LLMClient,
    *,
    checkpointer,
    memory_service: MemoryService | None = None,
    retrieval_service: RetrievalService | None = None,
):
    g = StateGraph(GraphState)
    g.add_node("memory_context_node", make_memory_context_node(memory_service))
    g.add_node("retriever_node", make_retriever_node(retrieval_service))
    g.add_node("conversation_node", make_conversation_node(llm))
    g.add_edge(START, "memory_context_node")
    g.add_edge("memory_context_node", "retriever_node")
    g.add_edge("retriever_node", "conversation_node")
    g.add_edge("conversation_node", END)
    return g.compile(checkpointer=checkpointer)
