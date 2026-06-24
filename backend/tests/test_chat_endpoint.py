import json
import re

import pytest
from fastapi.testclient import TestClient

from app.llm.base import NotConfiguredLLM


class _FakeLLM:
    """Any object that is NOT NotConfiguredLLM => endpoint treats the runtime as configured."""


@pytest.fixture
def client(monkeypatch):
    import app.api.chat as chat

    class FakeService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "Hi"}}
            yield {"event": "done",
                   "data": {"conversation_id": conversation_id, "message_id": "m1", "usage": {}}}

    monkeypatch.setattr(chat, "_service", FakeService())
    monkeypatch.setattr(chat, "get_llm_client", lambda: _FakeLLM())  # configured runtime
    from app.main import app
    return TestClient(app)


def test_chat_streams_sse(client):
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    body = r.text
    assert "event: token" in body and '"text": "Hi"' in body
    assert "event: done" in body


def test_chat_rejects_concurrent_run(client):
    import app.services.conversation.locks as locks_mod
    locks_mod.conversation_locks.try_acquire("busy")
    r = client.post("/chat", json={"message": "x", "conversation_id": "busy"})
    assert r.status_code == 409
    assert r.json()["code"] == "conversation_busy"
    locks_mod.conversation_locks.release("busy")


def test_chat_returns_503_when_llm_not_configured(monkeypatch):
    import app.api.chat as chat
    monkeypatch.setattr(chat, "get_llm_client", lambda: NotConfiguredLLM())
    from app.main import app
    r = TestClient(app).post("/chat", json={"message": "hi"})
    assert r.status_code == 503
    assert r.json()["code"] == "llm_not_configured"


def test_chat_rejects_empty_message(client):
    r = client.post("/chat", json={"message": ""})
    assert r.status_code == 422  # pydantic min_length


def test_chat_releases_lock_on_service_error(monkeypatch):
    import app.api.chat as chat
    import app.services.conversation.locks as locks_mod

    class BoomService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "x"}}
            raise RuntimeError("boom")

    monkeypatch.setattr(chat, "_service", BoomService())
    monkeypatch.setattr(chat, "get_llm_client", lambda: _FakeLLM())
    from app.main import app
    c = TestClient(app)
    try:
        c.post("/chat", json={"message": "hi", "conversation_id": "errconv"})
    except Exception:
        pass  # the streamed error may surface client-side; we only care about the lock
    # event_gen's finally must have released the lock even though the service raised
    assert locks_mod.conversation_locks.try_acquire("errconv") is True
    locks_mod.conversation_locks.release("errconv")


def test_chat_sse_body_is_crlf_framed_and_client_parseable(client):
    """Guards C1: sse-starlette emits CRLF frames; reproduce the frontend parser
    (frontend/lib/api.ts) over the real body and assert it reconstructs the events."""
    body = client.post("/chat", json={"message": "hello"}).text
    assert "\r\n\r\n" in body  # CRLF frame separator the frontend splits on

    events = []
    for frame in re.split(r"\r\n\r\n|\n\n|\r\r", body):
        ev, data = "message", ""
        for line in re.split(r"\r\n|\n|\r", frame):
            if line.startswith("event:"):
                ev = line[6:].strip()
            elif line.startswith("data:"):
                data += line[5:].strip()
        if data:
            events.append((ev, json.loads(data)))

    names = [e[0] for e in events]
    assert "token" in names and "done" in names
    token = next(d for n, d in events if n == "token")
    assert token["text"] == "Hi"
