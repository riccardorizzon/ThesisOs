from __future__ import annotations

from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from sqlalchemy import select

from app.db import models
from app.graph.conversation import build_graph
from app.runtime.events import EventType
from app.schemas.companion_resume import CompanionResume
from app.schemas.graph_state import GraphState, Message
from app.schemas.run_context import RunContext
from app.schemas.workspace_snapshot import WorkspaceSnapshot
from app.services.conversation.service import ConversationService
from app.services.workspace.thesis_sor import THESIS_AGENT_PROJECT_ID
from tests.support.fake_memory import FakeMemoryService
from tests.support.orchestration_llm import OrchestrationLLM


class _FakeWorkspaceLoader:
    def __init__(self) -> None:
        self.project_ids: list[str | None] = []

    async def load(self, *, project_id=None, conversation_messages=0):
        self.project_ids.append(project_id)
        return WorkspaceSnapshot(
            project_id=project_id,
            conversation_turns=conversation_messages,
            companion=CompanionResume(
                focus_section="§3.6",
                focus_section_title="Sintesi e costruzione di significato",
                next_action="Rivedere la sintesi del paragrafo",
                key_decisions=["Mantenere il difetto come dispositivo critico"],
            ),
        )


class _FakeEmitter:
    def __init__(self) -> None:
        self.events = []

    async def emit(self, event) -> None:
        self.events.append(event)


class _ParamsSpyLLM(OrchestrationLLM):
    def __init__(self, *, stream_parts: list[str]) -> None:
        super().__init__(stream_parts=stream_parts)
        self.stream_params: list[dict | None] = []

    async def astream(self, messages, *, model=None, params=None):
        self.stream_params.append(params)
        async for chunk in super().astream(messages, model=model, params=params):
            yield chunk


async def _run_graph(
    *,
    project_id: str,
    loader: _FakeWorkspaceLoader,
    user_text: str = "Continuiamo da ieri",
    stream_parts: list[str] | None = None,
    response_llm: OrchestrationLLM | None = None,
    orchestration_llm: OrchestrationLLM | None = None,
    memory: FakeMemoryService | None = None,
    history: list[Message] | None = None,
):
    llm = response_llm or OrchestrationLLM(stream_parts=stream_parts or ["Va bene."])
    graph = build_graph(
        llm,
        orchestration_llm=orchestration_llm,
        checkpointer=InMemorySaver(),
        memory_service=memory or FakeMemoryService(),
        workspace_loader=loader,
    )
    config = {
        "configurable": {
            "thread_id": "conversation-1",
            "project_id": project_id,
        }
    }
    messages = [*(history or []), Message(role="user", content=user_text)]
    chunks = [
        chunk
        async for chunk in graph.astream(
            GraphState(messages=messages),
            config,
            stream_mode="custom",
        )
    ]
    return llm, chunks


@pytest.mark.asyncio
async def test_companion_open_skips_orchestration_llm_but_keeps_graph_context():
    loader = _FakeWorkspaceLoader()
    emitter = _FakeEmitter()
    run_context = RunContext(
        conversation_id="resume-fast-path",
        agent_run_id="resume-fast-path-run",
        trace_id="resume-fast-path-trace",
        request_id="resume-fast-path-request",
    )
    response = OrchestrationLLM(stream_parts=["Riprendiamo §3.6."])
    orchestration = OrchestrationLLM()
    graph = build_graph(
        response,
        orchestration_llm=orchestration,
        checkpointer=InMemorySaver(),
        memory_service=FakeMemoryService(),
        workspace_loader=loader,
        emitter=emitter,
        run_context=run_context,
    )
    config = {
        "configurable": {
            "thread_id": "resume-fast-path",
            "project_id": THESIS_AGENT_PROJECT_ID,
            "run_context": run_context.model_dump(),
        }
    }

    chunks = [
        chunk
        async for chunk in graph.astream(
            GraphState(
                messages=[Message(role="user", content="__companion_open__")]
            ),
            config,
            stream_mode="custom",
        )
    ]

    assert orchestration.generate_calls == 0
    assert {
        event.metadata.get("agent")
        for event in emitter.events
        if event.event_type == EventType.NODE_COMPLETED
    } == {
        "supervisor",
        "planner",
        "router",
        "workspace_context",
        "memory_context",
        "conversation",
    }
    assert loader.project_ids == [THESIS_AGENT_PROJECT_ID]
    assert response.last_stream_messages is not None
    assert any(chunk.get("type") == "token" for chunk in chunks)


@pytest.mark.asyncio
async def test_thesis_agent_turn_receives_companion_resume_and_focus():
    loader = _FakeWorkspaceLoader()

    llm, chunks = await _run_graph(project_id=THESIS_AGENT_PROJECT_ID, loader=loader)

    assert loader.project_ids == [THESIS_AGENT_PROJECT_ID]
    assert any(chunk.get("type") == "token" for chunk in chunks)
    system = llm.last_stream_messages[0]["content"]
    assert "Thesis Companion" in system
    assert "[COMPANION RESUME]" in system
    assert "Focus: Capitolo 3 · §3.6" in system
    assert "Pillar: CONTINUE" in system


@pytest.mark.asyncio
async def test_non_academic_companion_turn_streams_each_chunk_directly():
    loader = _FakeWorkspaceLoader()
    response = _ParamsSpyLLM(stream_parts=["Primo ", "secondo."])

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        response_llm=response,
    )

    text_events = [
        (chunk["type"], chunk["text"])
        for chunk in chunks
        if chunk.get("type") in {"token", "replace"}
    ]
    assert text_events == [("token", "Primo "), ("token", "secondo.")]
    assert response.stream_params == [{"reasoning_effort": "minimal"}]


@pytest.mark.asyncio
async def test_companion_repair_emits_replace_without_duplicate_final_token():
    loader = _FakeWorkspaceLoader()

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        user_text="Basta per oggi",
        stream_parts=["Bozza non strutturata."],
    )

    text_events = [
        (chunk["type"], chunk["text"])
        for chunk in chunks
        if chunk.get("type") in {"token", "replace"}
    ]
    assert text_events[0] == ("token", "Bozza non strutturata.")
    assert text_events[-1][0] == "replace"
    assert "Oggi abbiamo deciso:" in text_events[-1][1]
    assert text_events.count(("token", text_events[-1][1])) == 0


@pytest.mark.asyncio
async def test_basta_per_oggi_writes_session_state_before_confirming():
    """PRESERVE = SESSION_STATE tier: the work-close must actually be written."""
    loader = _FakeWorkspaceLoader()
    memory = FakeMemoryService()

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        user_text="Basta per oggi",
        stream_parts=["Bozza non strutturata."],
        memory=memory,
    )

    row = memory.row("companion_session")
    assert row is not None
    assert "Punto di ripresa del lavoro" in row.content
    final = [c for c in chunks if c.get("type") in {"token", "replace"}][-1]
    assert "Oggi abbiamo deciso:" in final["text"]


@pytest.mark.asyncio
async def test_la_salvo_writes_work_artifact_from_prior_proposal():
    """SAVE = WORK_ARTIFACT tier: the approved proposal must actually be written."""
    loader = _FakeWorkspaceLoader()
    memory = FakeMemoryService()
    proposal = "La palette cromatica media tra norma e deviazione nel sistema di segni."

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        user_text="La salvo",
        stream_parts=["Salvata per continuità: riprendiamo domani da qui."],
        memory=memory,
        history=[
            Message(role="user", content="Proponi una frase per il paragrafo"),
            Message(role="assistant", content=f"Che ne dici di:\n\n> {proposal}"),
        ],
    )

    row = memory.row("companion_work_artifact")
    assert row is not None
    assert proposal in row.content
    final = [c for c in chunks if c.get("type") in {"token", "replace"}][-1]
    assert "Non sono riuscita" not in final["text"]


@pytest.mark.asyncio
async def test_failed_write_never_confirms_a_save():
    """NO WRITE = NO SAVE: when persistence fails, the reply must say so honestly."""
    loader = _FakeWorkspaceLoader()
    memory = FakeMemoryService(fail_writes=True)

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        user_text="La salvo",
        stream_parts=["Salvata per continuità: riprendiamo domani da qui."],
        memory=memory,
    )

    assert memory.rows == []
    final = [c for c in chunks if c.get("type") in {"token", "replace"}][-1]
    assert final["type"] == "replace"
    assert "Non sono riuscita a salvare" in final["text"]
    assert "NON è entrata" in final["text"]


@pytest.mark.asyncio
async def test_failed_session_close_never_confirms_the_close():
    """NO WRITE = NO SAVE also for «basta per oggi» (SESSION_STATE)."""
    loader = _FakeWorkspaceLoader()
    memory = FakeMemoryService(fail_writes=True)

    _, chunks = await _run_graph(
        project_id=THESIS_AGENT_PROJECT_ID,
        loader=loader,
        user_text="Basta per oggi",
        stream_parts=["Bozza non strutturata."],
        memory=memory,
    )

    assert memory.rows == []
    final = [c for c in chunks if c.get("type") in {"token", "replace"}][-1]
    assert final["type"] == "replace"
    assert "NON è stata salvata" in final["text"]
    assert "Oggi abbiamo deciso:" not in final["text"]


@pytest.mark.asyncio
async def test_non_primary_project_does_not_receive_thesis_companion_context():
    loader = _FakeWorkspaceLoader()

    llm, _ = await _run_graph(project_id="another-project", loader=loader)

    assert loader.project_ids == []
    system = llm.last_stream_messages[0]["content"] if llm.last_stream_messages[0]["role"] == "system" else ""
    assert "Thesis Companion" not in system
    assert "[COMPANION RESUME]" not in system
    assert "§3.6" not in system


@pytest.mark.asyncio
async def test_conversation_service_passes_project_id_to_graph_config(
    db_session,
    monkeypatch,
):
    captured: dict = {}

    class _FakeGraph:
        async def astream(self, state, config, *, stream_mode):
            captured.update(config)
            yield {"type": "token", "text": "ok"}

        async def aget_state(self, config):
            return SimpleNamespace(values={})

    @asynccontextmanager
    async def _fake_checkpointer():
        yield object()

    monkeypatch.setattr(
        "app.services.conversation.service.open_checkpointer",
        _fake_checkpointer,
    )
    monkeypatch.setattr(
        "app.services.conversation.service.build_graph",
        lambda *args, **kwargs: _FakeGraph(),
    )
    llm = OrchestrationLLM()
    monkeypatch.setattr(
        "app.services.conversation.service.get_llm_client",
        lambda: llm,
    )
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )

    events = [
        event
        async for event in ConversationService().stream_turn(
            conversation_id=None,
            user_text="Continuiamo",
            project_id=THESIS_AGENT_PROJECT_ID,
        )
    ]

    assert any(event["event"] == "done" for event in events)
    assert captured["configurable"]["project_id"] == THESIS_AGENT_PROJECT_ID
    assert captured["configurable"]["thread_id"]
    assert captured["configurable"]["run_context"]


@pytest.mark.asyncio
async def test_conversation_service_replace_overwrites_persisted_buffer(
    db_session,
    monkeypatch,
):
    class _FakeGraph:
        async def astream(self, state, config, *, stream_mode):
            yield {"type": "token", "text": "bozza"}
            yield {
                "type": "sources",
                "text": "",
                "sources": [{"document_id": "source-1"}],
            }
            yield {"type": "replace", "text": "testo riparato"}

        async def aget_state(self, config):
            return SimpleNamespace(values={})

    @asynccontextmanager
    async def _fake_checkpointer():
        yield object()

    monkeypatch.setattr(
        "app.services.conversation.service.open_checkpointer",
        _fake_checkpointer,
    )
    monkeypatch.setattr(
        "app.services.conversation.service.build_graph",
        lambda *args, **kwargs: _FakeGraph(),
    )
    llm = OrchestrationLLM()
    monkeypatch.setattr(
        "app.services.conversation.service.get_llm_client",
        lambda: llm,
    )
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )

    events = [
        event
        async for event in ConversationService().stream_turn(
            conversation_id=None,
            user_text="Basta per oggi",
            project_id=THESIS_AGENT_PROJECT_ID,
        )
    ]

    assert [event["event"] for event in events] == [
        "token",
        "sources",
        "replace",
        "done",
    ]
    assert events[2]["data"] == {"text": "testo riparato"}
    db_session.expire_all()
    persisted = (
        await db_session.execute(
            select(models.Message).where(models.Message.role == "assistant")
        )
    ).scalar_one()
    assert persisted.content == "testo riparato"
