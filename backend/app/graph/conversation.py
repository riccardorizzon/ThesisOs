from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.llm.base import LLMClient
from app.schemas.graph_state import GraphState, Message


def make_conversation_node(llm: LLMClient):
    async def conversation_node(state: GraphState) -> dict:
        writer = get_stream_writer()
        wire = [{"role": m.role, "content": m.content} for m in state.messages]
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
        # Replace semantics: the caller owns message history (DB is the
        # system of record), so no add_messages reducer is needed.
        return {
            "messages": [*state.messages, assistant],
            "draft": assistant.content,
            "errors": list(state.errors),
        }

    return conversation_node


def build_graph(llm: LLMClient, *, checkpointer):
    g = StateGraph(GraphState)
    g.add_node("conversation_node", make_conversation_node(llm))
    g.add_edge(START, "conversation_node")
    g.add_edge("conversation_node", END)
    return g.compile(checkpointer=checkpointer)
