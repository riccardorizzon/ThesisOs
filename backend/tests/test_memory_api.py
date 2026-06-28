from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryRecord, MemoryUpdate, MemoryVersionRecord
from app.services.memory.exceptions import (
    CannotDeleteSingletonError,
    MemoryNotFoundError,
    WriteConflictError,
)


def _record(**kwargs) -> MemoryRecord:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id="mem-1",
        kind="concept",
        title="Test",
        content="body",
        metadata={},
        key="slug",
        pinned=False,
        source="user",
        version=1,
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return MemoryRecord(**defaults)


class FakeMemoryService:
    def __init__(self):
        self.calls: list[tuple] = []

    async def list(self, filters: MemoryListFilters, *, session=None):
        self.calls.append(("list", filters))
        return [_record()]

    async def create(self, data: MemoryCreate, *, session=None):
        self.calls.append(("create", data))
        return _record(kind=data.kind, content=data.content, title=data.title)

    async def get(self, memory_id: str, *, session=None):
        self.calls.append(("get", memory_id))
        if memory_id == "missing":
            raise MemoryNotFoundError(memory_id)
        return _record(id=memory_id)

    async def update(self, memory_id: str, data: MemoryUpdate, *, session=None):
        self.calls.append(("update", memory_id, data))
        if memory_id == "conflict":
            raise WriteConflictError("conflict", expected_version=1, actual_version=2)
        return _record(id=memory_id, version=data.expected_version + 1, content=data.content or "body")

    async def delete(self, memory_id: str, *, session=None):
        self.calls.append(("delete", memory_id))
        if memory_id == "singleton":
            raise CannotDeleteSingletonError("editable")

    async def list_versions(self, memory_id: str, *, session=None):
        self.calls.append(("list_versions", memory_id))
        now = datetime.now(timezone.utc)
        return [
            MemoryVersionRecord(
                memory_id=memory_id,
                version=1,
                title="T",
                content="v1",
                metadata={},
                source="user",
                changed_at=now,
            )
        ]


@pytest.fixture
def fake_service(monkeypatch):
    import app.api.memory as memory_api

    svc = FakeMemoryService()
    monkeypatch.setattr(memory_api, "_service", svc)
    from app.main import app

    return TestClient(app), svc


def test_api_has_no_direct_db_imports():
    import app.api.memory as memory_api

    source = open(memory_api.__file__).read()
    assert "app.db.models" not in source
    assert "AsyncSessionLocal" not in source
    assert "select(" not in source
    assert "load_prompt_context" not in source


def test_list_delegates_to_service(fake_service):
    client, svc = fake_service
    r = client.get("/memory?q=thesis&kind=concept")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert svc.calls[0][0] == "list"
    assert svc.calls[0][1].q == "thesis"
    assert svc.calls[0][1].kind == "concept"


def test_create_delegates_to_service(fake_service):
    client, svc = fake_service
    r = client.post("/memory", json={"kind": "concept", "content": "hello", "title": "Hi"})
    assert r.status_code == 201
    assert svc.calls[0][0] == "create"
    assert svc.calls[0][1].content == "hello"


def test_get_delegates_to_service(fake_service):
    client, svc = fake_service
    r = client.get("/memory/mem-1")
    assert r.status_code == 200
    assert svc.calls[0] == ("get", "mem-1")


def test_get_returns_404(fake_service):
    client, _ = fake_service
    r = client.get("/memory/missing")
    assert r.status_code == 404
    assert r.json()["code"] == "memory_not_found"


def test_update_conflict_returns_409_not_500(fake_service):
    client, _ = fake_service
    r = client.patch("/memory/conflict", json={"expected_version": 1, "content": "new"})
    assert r.status_code == 409
    assert r.json()["code"] == "write_conflict"


def test_delete_singleton_returns_400(fake_service):
    client, _ = fake_service
    r = client.delete("/memory/singleton")
    assert r.status_code == 400
    assert r.json()["code"] == "cannot_delete_singleton"


def test_versions_delegates_to_service(fake_service):
    client, svc = fake_service
    r = client.get("/memory/mem-1/versions")
    assert r.status_code == 200
    assert r.json()[0]["version"] == 1
    assert svc.calls[0] == ("list_versions", "mem-1")


def test_no_prompt_context_in_api_module():
    import app.api.memory as memory_api

    source = open(memory_api.__file__).read()
    assert "load_prompt_context" not in source
    assert "PromptContext" not in source
    assert "render_prompt_context" not in source


def test_openapi_has_no_context_or_search_routes():
    from pathlib import Path

    openapi = Path(__file__).resolve().parents[2].parent / "contracts" / "openapi" / "openapi.yaml"
    if not openapi.exists():
        pytest.skip("openapi contract not available in this environment")
    text = openapi.read_text()
    assert "/memory/context" not in text
    assert "/memory/search" not in text


# --- Integration (real MemoryService + Postgres) --------------------------------

@pytest.fixture
def integration_client(db_session):
    from app.main import app

    return TestClient(app)


async def test_integration_crud_and_query(integration_client, db_session):
    r = integration_client.post(
        "/memory",
        json={"kind": "concept", "title": "My thesis topic", "content": "Scope notes", "key": "thesis-topic"},
    )
    assert r.status_code == 201
    mem_id = r.json()["id"]

    r = integration_client.get("/memory?q=thesis")
    assert r.status_code == 200
    assert any(item["id"] == mem_id for item in r.json())

    r = integration_client.patch(
        f"/memory/{mem_id}",
        json={"expected_version": 1, "content": "Updated scope"},
    )
    assert r.status_code == 200
    assert r.json()["version"] == 2

    r = integration_client.get(f"/memory/{mem_id}/versions")
    assert r.status_code == 200
    assert [v["version"] for v in r.json()] == [1, 2]

    r = integration_client.delete(f"/memory/{mem_id}")
    assert r.status_code == 204


async def test_integration_write_conflict_returns_409(integration_client, db_session):
    r = integration_client.post("/memory", json={"kind": "concept", "content": "x"})
    assert r.status_code == 201
    mem_id = r.json()["id"]

    integration_client.patch(f"/memory/{mem_id}", json={"expected_version": 1, "content": "v2"})
    r = integration_client.patch(f"/memory/{mem_id}", json={"expected_version": 1, "content": "stale"})
    assert r.status_code == 409
    assert r.json()["code"] == "write_conflict"


async def test_integration_singleton_duplicate_returns_409(integration_client, db_session):
    r1 = integration_client.post("/memory", json={"kind": "editable", "content": "Rules"})
    assert r1.status_code == 201
    r2 = integration_client.post("/memory", json={"kind": "editable", "content": "Again"})
    assert r2.status_code == 409
    assert r2.json()["code"] == "singleton_exists"
