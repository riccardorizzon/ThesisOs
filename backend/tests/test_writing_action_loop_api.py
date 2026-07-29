"""API integration tests for writing panel action loop routing."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.runtime.action_loop.types import LoopStep
from app.schemas.draft import DraftResult


class FakeLLM:
    async def stream_chat(self, messages, *, emit=None):
        return "unused", {}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr("app.api.writing_actions.get_llm_client", lambda: FakeLLM())
    return TestClient(app)


def test_verify_uses_action_loop(client, monkeypatch):
    seen: dict = {}

    async def fake_loop(**kwargs):
        seen["loop"] = True
        emit = kwargs.get("emit")
        if emit:
            emit({"type": "token", "text": "Verifica ok."})
        return DraftResult(
            draft="Verifica ok.",
            citations=[],
            metadata={"loop_action": True},
        )

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fake_loop)

    with client.stream(
        "POST",
        "/writing/actions",
        json={"action": "verify", "chapter_content": "Cap"},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())

    assert seen.get("loop") is True
    assert "Verifica ok." in body
    assert "event: done" in body


def test_rewrite_skips_action_loop(client, monkeypatch):
    async def fail_loop(**kwargs):
        raise AssertionError("loop should not run")

    class FakeWriter:
        async def run_panel_action(self, **kwargs):
            emit = kwargs.get("emit")
            if emit:
                emit({"type": "token", "text": "Legacy draft."})
            return DraftResult(draft="Legacy draft.", citations=[])

    async def empty_context(**kwargs):
        return []

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fail_loop)
    monkeypatch.setattr("app.api.writing_actions.LLMWriter", lambda _llm: FakeWriter())
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
        json={"action": "rewrite", "selection_text": "Passaggio", "chapter_content": "Cap"},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())

    assert "Legacy draft." in body
    assert "event: done" in body


def test_verify_stream_includes_step_events(client, monkeypatch):
    async def fake_loop(*, on_step=None, **kwargs):
        if on_step:
            on_step(LoopStep(label="Ricerca nel corpus", detail="craftsmanship"))
        return DraftResult(
            draft="Ok.",
            citations=[],
            metadata={"search_count": 2, "chunk_count": 5, "loop_action": True},
        )

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", fake_loop)

    with client.stream(
        "POST",
        "/writing/actions",
        json={"action": "verify", "chapter_content": "x"},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())

    assert "event: step" in body
    assert "Ricerca nel corpus" in body
    assert "craftsmanship" in body
    assert '"search_count": 2' in body
    assert '"chunk_count": 5' in body


def test_verify_unexpected_loop_error_yields_sse_error(client, monkeypatch):
    async def boom_loop(**kwargs):
        raise TypeError("'<' not supported between instances of 'int' and 'str'")

    monkeypatch.setattr("app.api.writing_actions.run_writing_panel_with_loop", boom_loop)

    with client.stream(
        "POST",
        "/writing/actions",
        json={"action": "verify", "chapter_content": "x"},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(resp.iter_text())

    assert "event: error" in body
    assert "action_loop_failed" in body
    assert "event: done" not in body
