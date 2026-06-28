import pytest
from app.graph.conversation import build_graph
from app.llm.base import TokenChunk
from app.schemas.graph_state import GraphState, Message
from app.schemas.memory import PromptContext, PromptMemoryItem


class CapturingLLM:
    def __init__(self):
        self.last_messages: list[dict] | None = None

    async def astream(self, messages, *, model=None, params=None):
        self.last_messages = messages
        yield TokenChunk(text="ok")
        yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 1}})

    async def generate(self, *a, **k):
        return "ok"

    async def embed(self, *a, **k):
        raise NotImplementedError

    async def vision(self, *a, **k):
        raise NotImplementedError


class StubMemoryService:
    def __init__(self, ctx: PromptContext):
        self._ctx = ctx
        self.last_conversation_id: str | None = None

    async def load_prompt_context(self, *, conversation_id=None, **kwargs):
        self.last_conversation_id = conversation_id
        return self._ctx


@pytest.fixture
def in_memory_graph_factory():
    from langgraph.checkpoint.memory import InMemorySaver

    def _factory(llm, memory_service=None):
        return build_graph(llm, checkpointer=InMemorySaver(), memory_service=memory_service)

    return _factory


async def test_memory_context_prepends_system_message(in_memory_graph_factory):
    ctx = PromptContext(
        editable=[
            PromptMemoryItem(
                id="e1",
                kind="editable",
                title="Rules",
                content="Use APA7.",
                version=1,
                pinned=False,
            )
        ]
    )
    llm = CapturingLLM()
    graph = in_memory_graph_factory(llm, StubMemoryService(ctx))
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-42"}}

    async for _chunk in graph.astream(state, cfg, stream_mode="custom"):
        pass

    assert llm.last_messages is not None
    assert llm.last_messages[0]["role"] == "system"
    assert "[EDITABLE MEMORY]" in llm.last_messages[0]["content"]
    assert "Use APA7." in llm.last_messages[0]["content"]
    assert llm.last_messages[-1]["role"] == "user"


async def test_memory_context_skips_system_when_empty(in_memory_graph_factory):
    llm = CapturingLLM()
    graph = in_memory_graph_factory(llm, StubMemoryService(PromptContext()))
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-1"}}

    async for _chunk in graph.astream(state, cfg, stream_mode="custom"):
        pass

    assert llm.last_messages == [{"role": "user", "content": "hi"}]


async def test_memory_context_excludes_concept_from_prompt(in_memory_graph_factory):
    """Concept rows are CRUD-only in M2 — loader must not inject them."""
    llm = CapturingLLM()
    graph = in_memory_graph_factory(llm, StubMemoryService(PromptContext()))
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-1"}}

    async for _chunk in graph.astream(state, cfg, stream_mode="custom"):
        pass

    wire = llm.last_messages or []
    assert all("concept" not in (m.get("content") or "").lower() for m in wire)


async def test_graph_topology_still_streams_assistant(in_memory_graph_factory):
    class FakeLLM:
        async def astream(self, messages, *, model=None, params=None):
            for t in ["Ciao", " ", "mondo"]:
                yield TokenChunk(text=t)
            yield TokenChunk(text="", finish_reason="stop", metadata={"usage": {"total_tokens": 3}})

        async def generate(self, *a, **k):
            return "Ciao mondo"

        async def embed(self, *a, **k):
            raise NotImplementedError

        async def vision(self, *a, **k):
            raise NotImplementedError

    graph = in_memory_graph_factory(FakeLLM(), StubMemoryService(PromptContext()))
    state = GraphState(messages=[Message(role="user", content="hi")])
    cfg = {"configurable": {"thread_id": "conv-1"}}
    tokens = []
    async for chunk in graph.astream(state, cfg, stream_mode="custom"):
        tokens.append(chunk["text"])
    assert "".join(tokens) == "Ciao mondo"


async def test_memory_context_integration_with_db(in_memory_graph_factory, db_session):
    from app.schemas.memory import MemoryCreate
    from app.services.memory.service import MemoryService

    svc = MemoryService()
    await svc.create(
        MemoryCreate(kind="editable", content="Always-on thesis rules.", title="Rules"),
        session=db_session,
    )
    await db_session.commit()

    llm = CapturingLLM()
    graph = in_memory_graph_factory(llm, svc)
    state = GraphState(messages=[Message(role="user", content="hello")])
    cfg = {"configurable": {"thread_id": "conv-db-1"}}

    async for _chunk in graph.astream(state, cfg, stream_mode="custom"):
        pass

    assert llm.last_messages is not None
    assert llm.last_messages[0]["role"] == "system"
    assert "Always-on thesis rules." in llm.last_messages[0]["content"]
