"""Conversations API tests (M7 P-CHAT-PERSIST-BE)."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app.llm.base import NotConfiguredLLM
from tests.support.orchestration_llm import OrchestrationLLM

_PROJECT = "thesis-agent"
_MISSING_CONV_ID = "00000000-0000-0000-0000-000000000000"


class _FakeLLM:
    """Any object that is NOT NotConfiguredLLM => endpoint treats the runtime as configured."""


@pytest.fixture
def client(db_session, monkeypatch):
    import app.api.chat as chat

    monkeypatch.setattr(chat, "get_llm_client", lambda: _FakeLLM())
    from app.main import app

    return TestClient(app)


@pytest.fixture
def chat_client(db_session, monkeypatch):
    import app.api.chat as chat
    from app.graph.checkpointer import ensure_langgraph_schema

    import asyncio

    asyncio.get_event_loop().run_until_complete(ensure_langgraph_schema())

    llm = OrchestrationLLM(stream_parts=["Persisted", " reply"])
    monkeypatch.setattr("app.services.conversation.service.get_llm_client", lambda: llm)
    monkeypatch.setattr(
        "app.services.conversation.service.get_orchestration_llm_client",
        lambda: llm,
    )
    monkeypatch.setattr(chat, "get_llm_client", lambda: llm)
    from app.main import app

    return TestClient(app)


def test_list_conversations_empty(client):
    res = client.get("/conversations", params={"project_id": _PROJECT})
    assert res.status_code == 200
    assert res.json() == {"items": []}


def test_create_conversation(client):
    res = client.post("/conversations", json={"project_id": _PROJECT, "title": "Thesis chat"})
    assert res.status_code == 201
    body = res.json()
    assert body["project_id"] == _PROJECT
    assert body["title"] == "Thesis chat"
    assert body["id"]
    assert body["created_at"]


def test_list_conversations_after_create(client):
    created = client.post("/conversations", json={"project_id": _PROJECT, "title": "Thread A"}).json()
    res = client.get("/conversations", params={"project_id": _PROJECT})
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["title"] == "Thread A"


def test_list_conversations_scoped_by_project(client):
    client.post("/conversations", json={"project_id": _PROJECT, "title": "Scoped"})
    client.post("/conversations", json={"project_id": "other-project", "title": "Other"})
    res = client.get("/conversations", params={"project_id": _PROJECT})
    assert res.status_code == 200
    assert len(res.json()["items"]) == 1
    assert res.json()["items"][0]["project_id"] == _PROJECT


def test_get_messages_empty_conversation(client):
    created = client.post("/conversations", json={"project_id": _PROJECT}).json()
    res = client.get(f"/conversations/{created['id']}/messages")
    assert res.status_code == 200
    assert res.json() == {"items": []}


def test_get_messages_not_found(client):
    res = client.get(f"/conversations/{_MISSING_CONV_ID}/messages")
    assert res.status_code == 404
    assert res.json()["code"] == "conversation_not_found"


def test_chat_persists_messages_in_thread(chat_client):
    created = chat_client.post("/conversations", json={"project_id": _PROJECT, "title": "Chat thread"}).json()
    conv_id = created["id"]

    stream = chat_client.post(
        "/chat",
        json={"message": "hello", "conversation_id": conv_id, "project_id": _PROJECT},
    )
    assert stream.status_code == 200
    assert "event: done" in stream.text

    messages = chat_client.get(f"/conversations/{conv_id}/messages").json()["items"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Persisted reply"


def test_chat_appends_to_same_thread(chat_client):
    created = chat_client.post("/conversations", json={"project_id": _PROJECT}).json()
    conv_id = created["id"]

    first = chat_client.post(
        "/chat",
        json={"message": "first", "conversation_id": conv_id, "project_id": _PROJECT},
    )
    assert "event: done" in first.text
    second = chat_client.post(
        "/chat",
        json={"message": "second", "conversation_id": conv_id, "project_id": _PROJECT},
    )
    assert "event: done" in second.text

    messages = chat_client.get(f"/conversations/{conv_id}/messages").json()["items"]
    assert len(messages) == 4
    assert [m["content"] for m in messages if m["role"] == "user"] == ["first", "second"]


def test_chat_rejects_reusing_thread_under_another_project(chat_client):
    """A conversation is owned by one project; history must never cross that boundary."""
    created = chat_client.post(
        "/conversations",
        json={"project_id": _PROJECT, "title": "Private thesis thread"},
    ).json()
    conv_id = created["id"]
    first = chat_client.post(
        "/chat",
        json={
            "message": "private thesis detail",
            "conversation_id": conv_id,
            "project_id": _PROJECT,
        },
    )
    assert "event: done" in first.text

    crossed = chat_client.post(
        "/chat",
        json={
            "message": "what were we doing?",
            "conversation_id": conv_id,
            "project_id": "demo-thesis",
        },
    )

    # Use the existing SSE error contract so the frontend can display it.
    assert "event: error" in crossed.text
    assert '"code": "project_scope_mismatch"' in crossed.text
    assert "altro progetto" in crossed.text
    messages = chat_client.get(f"/conversations/{conv_id}/messages").json()["items"]
    assert [m["content"] for m in messages if m["role"] == "user"] == [
        "private thesis detail"
    ]
    assert all("what were we doing?" != m["content"] for m in messages)


def test_chat_lists_under_project_after_turn(chat_client):
    stream = chat_client.post(
        "/chat",
        json={"message": "bootstrap", "project_id": _PROJECT},
    )
    assert stream.status_code == 200
    assert "event: done" in stream.text
    done = next(
        json.loads(line.removeprefix("data: "))
        for line in stream.text.splitlines()
        if line.startswith("data:") and '"conversation_id"' in line
    )
    conv_id = done["conversation_id"]

    listed = chat_client.get("/conversations", params={"project_id": _PROJECT}).json()["items"]
    assert any(item["id"] == conv_id for item in listed)


def test_chat_returns_503_when_llm_not_configured(monkeypatch):
    import app.api.chat as chat

    monkeypatch.setattr(chat, "get_llm_client", lambda: NotConfiguredLLM())
    from app.main import app

    res = TestClient(app).post("/chat", json={"message": "hi"})
    assert res.status_code == 503
    assert res.json()["code"] == "llm_not_configured"
