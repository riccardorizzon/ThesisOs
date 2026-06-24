import pytest
from app.llm.base import TokenChunk
from app.graph.conversation import build_graph
from app.schemas.graph_state import GraphState, Message


class FakeLLM:
    async def astream(self, messages, *, model=None, params=None):
        for t in ["Ciao", " ", "mondo"]:
            yield TokenChunk(text=t)
        yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 3}})
    async def generate(self, *a, **k): return "Ciao mondo"
    async def embed(self, *a, **k): raise NotImplementedError
    async def vision(self, *a, **k): raise NotImplementedError


@pytest.fixture
def app_graph():
    # InMemorySaver keeps this test free of Postgres
    from langgraph.checkpoint.memory import InMemorySaver
    return build_graph(FakeLLM(), checkpointer=InMemorySaver())


async def test_graph_streams_tokens_and_persists_assistant(app_graph):
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-1"}}
    tokens = []
    async for chunk in app_graph.astream(state, cfg, stream_mode="custom"):
        tokens.append(chunk["text"])
    assert "".join(tokens) == "Ciao mondo"
    snap = await app_graph.aget_state(cfg)
    assert snap.values["messages"][-1].role == "assistant"
    assert snap.values["messages"][-1].content == "Ciao mondo"
