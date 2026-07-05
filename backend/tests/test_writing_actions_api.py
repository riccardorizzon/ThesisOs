"""POST /writing/actions — Writing panel AI actions (PX2-EWO-003)."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.draft import DraftResult
from app.schemas.graph_state import CitationRef


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
    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_action", lambda writer, **kw: writer.run_panel_action(**kw))

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
