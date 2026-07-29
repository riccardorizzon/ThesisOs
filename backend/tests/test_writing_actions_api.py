"""POST /writing/actions — Writing panel AI actions (PX2-EWO-003)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.draft import DraftResult
from app.schemas.graph_state import CitationRef, RetrievedChunk
from app.schemas.retrieval import SearchResultItem
from app.services.retrieval import EmbedFailedError
from app.services.writing.panel import (
    build_retrieval_query,
    fetch_panel_retrieved_context,
    search_results_to_chunks,
)


class FakeLLM:
    async def stream_chat(self, messages, *, emit=None):
        if emit:
            emit({"type": "token", "text": "Risposta "})
            emit({"type": "token", "text": "di prova."})
        return "Risposta di prova.", {"prompt_tokens": 1, "completion_tokens": 2}


class FakeWriter:
    async def run_panel_action(self, **kwargs):
        emit = kwargs.get("emit")
        if emit:
            emit({"type": "token", "text": "Bozza "})
            emit({"type": "token", "text": "panel."})
        return DraftResult(
            draft="Bozza panel.",
            citations=[CitationRef(source_id="src-1", locator="p.1")],
            metadata={"writing_panel_action": kwargs.get("action", "rewrite")},
        )


class FakeRetrievalService:
    def __init__(self, *, results=None, fail=False):
        self._results = results or []
        self._fail = fail
        self.last_query: str | None = None

    async def search(self, query, *, filters=None, limit=10, hybrid_alpha=0.5, session=None):
        self.last_query = query
        if self._fail:
            raise EmbedFailedError("embedding unavailable")
        return self._results, "fake-model"


def _search_result() -> SearchResultItem:
    return SearchResultItem(
        chunk_id="c1",
        document_id="d1",
        chunk_hash="h1",
        score=0.9,
        content="Craft is the disciplined pursuit of quality.",
        document_title="The Craftsman",
        page_from=10,
    )


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.api.writing_actions.get_llm_client", lambda: FakeLLM())
    return TestClient(app)


def test_writing_actions_rejects_unknown_action(client):
    r = client.post("/writing/actions", json={"action": "unknown"})
    assert r.status_code == 400
    assert r.json()["code"] == "invalid_action"


def test_writing_actions_streams_sse(client, monkeypatch):
    monkeypatch.setattr("app.api.writing_actions.LLMWriter", lambda _llm: FakeWriter())
    async def empty_context(**kwargs):
        return []

    monkeypatch.setattr(
        "app.api.writing_actions.fetch_panel_retrieved_context",
        empty_context,
    )
    monkeypatch.setattr(
        "app.api.writing_actions.run_writing_panel_action",
        lambda writer, **kw: writer.run_panel_action(**kw),
    )

    with client.stream(
        "POST",
        "/writing/actions",
        json={
            "action": "rewrite",
            "selection_text": "Passaggio",
            "chapter_content": "Capitolo",
            "context_summary": "Decisioni vincolanti",
        },
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert "event: token" in body
    assert "event: done" in body
    assert "Bozza panel." in body


def test_writing_actions_passes_retrieved_context(client, monkeypatch):
    captured: dict = {}

    async def capture_context(**kwargs):
        captured.update(kwargs)
        return [
            RetrievedChunk(
                chunk_id="c1",
                score=0.9,
                content="Grounded evidence.",
                document_id="d1",
                document_title="Doc",
            )
        ]

    async def run_panel(writer, **kwargs):
        captured["panel_kwargs"] = kwargs
        return await writer.run_panel_action(**kwargs)

    monkeypatch.setattr("app.api.writing_actions.LLMWriter", lambda _llm: FakeWriter())
    monkeypatch.setattr("app.api.writing_actions.fetch_panel_retrieved_context", capture_context)
    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_action", run_panel)

    with client.stream(
        "POST",
        "/writing/actions",
        json={
            "action": "rewrite",
            "selection_text": "Passaggio selezionato",
            "chapter_content": "Capitolo intero",
        },
    ) as response:
        assert response.status_code == 200
        "".join(response.iter_text())

    panel_kwargs = captured["panel_kwargs"]
    assert len(panel_kwargs["retrieved_context"]) == 1
    assert panel_kwargs["retrieved_context"][0].chunk_id == "c1"
    assert panel_kwargs["retrieved_context"][0].content == "Grounded evidence."


def test_writing_actions_embed_failed_returns_422(client, monkeypatch):
    async def fail_retrieval(**kwargs):
        from app.services.writing.panel import WritingPanelRetrievalError

        raise WritingPanelRetrievalError("embedding unavailable")

    monkeypatch.setattr("app.api.writing_actions.fetch_panel_retrieved_context", fail_retrieval)

    r = client.post(
        "/writing/actions",
        json={"action": "rewrite", "selection_text": "Passaggio"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "embed_failed"


@pytest.mark.asyncio
async def test_fetch_panel_retrieved_context_uses_search_results():
    service = FakeRetrievalService(results=[_search_result()])
    chunks = await fetch_panel_retrieved_context(
        action="rewrite",
        selection_text="craftsmanship",
        chapter_content="",
        retrieval_service=service,
    )
    assert service.last_query == "craftsmanship"
    assert len(chunks) == 1
    assert chunks[0].document_title == "The Craftsman"


@pytest.mark.asyncio
async def test_fetch_panel_retrieved_context_surfaces_embed_failure():
    service = FakeRetrievalService(fail=True)
    from app.services.writing.panel import WritingPanelRetrievalError

    with pytest.raises(WritingPanelRetrievalError, match="embedding unavailable"):
        await fetch_panel_retrieved_context(
            action="rewrite",
            selection_text="craftsmanship",
            chapter_content="",
            retrieval_service=service,
        )


def test_build_retrieval_query_prefers_selection():
    assert build_retrieval_query(
        action="rewrite",
        selection_text="Selected passage",
        chapter_content="Chapter body",
    ) == "Selected passage"


def test_build_retrieval_query_includes_chapter_for_find_sources():
    query = build_retrieval_query(
        action="find-sources",
        selection_text="Passage",
        chapter_content="Chapter body",
    )
    assert "Passage" in query
    assert "Chapter body" in query


def test_search_results_to_chunks_maps_metadata():
    chunks = search_results_to_chunks([_search_result()])
    assert chunks[0].chunk_id == "c1"
    assert chunks[0].document_id == "d1"
    assert chunks[0].page_from == 10


def test_compose_writing_panel_wire_includes_context():
    from app.graph.orchestration.writer_prompt import compose_writing_panel_wire

    wire = compose_writing_panel_wire(
        action="verify",
        selection_text="Test",
        chapter_content="Capitolo",
        context_summary="CORPUS-02 escluso",
        retrieved_context=[],
    )
    assert len(wire) == 2
    assert "verify" in wire[0].content
    assert "CORPUS-02" in wire[0].content
    assert "Test" in wire[0].content
