import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    import app.api.chat as chat

    class FakeService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "Hi"}}
            yield {"event": "done", "data": {"conversation_id": "c1", "message_id": "m1", "usage": {}}}

    monkeypatch.setattr(chat, "_service", FakeService())
    from app.main import app
    return TestClient(app)


def test_chat_streams_sse(client):
    r = client.post("/chat", json={"message": "hello"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    body = r.text
    assert "event: token" in body and '"text": "Hi"' in body
    assert "event: done" in body


def test_chat_rejects_concurrent_run(client, monkeypatch):
    import app.services.conversation.locks as locks_mod
    locks_mod.conversation_locks.try_acquire("busy")
    r = client.post("/chat", json={"message": "x", "conversation_id": "busy"})
    assert r.status_code == 409
    assert r.json()["code"] == "conversation_busy"
    locks_mod.conversation_locks.release("busy")
