import pytest
from app.graph.conversation import build_graph
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext
from tests.support.orchestration_llm import OrchestrationLLM


class StubMemoryService:
    async def load_prompt_context(self, **kwargs):
        return PromptContext()


@pytest.fixture
def app_graph():
    from langgraph.checkpoint.memory import InMemorySaver

    return build_graph(
        OrchestrationLLM(stream_parts=["Ciao", " ", "mondo"]),
        checkpointer=InMemorySaver(),
        memory_service=StubMemoryService(),
    )


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
