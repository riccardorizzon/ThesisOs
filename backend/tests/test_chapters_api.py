"""/chapters HTTP adapter tests (M6.4). Fake ChapterService — no DB needed."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chapter import (
    ChapterContentUpdate,
    ChapterMetadataUpdate,
    ChapterRecord,
    ChapterVersionRecord,
)
from app.services.chapter import (
    ChapterNotDeletableError,
    ChapterNotFoundError,
    ChapterWriteConflictError,
    InvalidChapterStatusError,
)


def _record(**kwargs) -> ChapterRecord:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id="ch-1", parent_id=None, order_index=0, title="Intro", status="draft",
        content_md=None, summary=None, word_count=0, version=1, created_at=now, updated_at=now,
    )
    defaults.update(kwargs)
    return ChapterRecord(**defaults)


class FakeChapterService:
    async def create(self, data, *, session=None):
        if data.status not in ("draft", "review", "approved", "published"):
            raise InvalidChapterStatusError(data.status)
        return _record(title=data.title, status=data.status, parent_id=data.parent_id, deletable=True)

    async def list(self, filters=None, *, session=None):
        return [_record()]

    async def get(self, chapter_id, *, session=None):
        if chapter_id == "missing":
            raise ChapterNotFoundError(chapter_id)
        if chapter_id == "protected":
            return _record(id=chapter_id, deletable=False)
        return _record(id=chapter_id, deletable=True)

    async def delete(self, chapter_id, *, session=None):
        if chapter_id == "missing":
            raise ChapterNotFoundError(chapter_id)
        if chapter_id == "protected":
            raise ChapterNotDeletableError(chapter_id)

    async def update_content(self, chapter_id, data: ChapterContentUpdate, *, session=None):
        if chapter_id == "missing":
            raise ChapterNotFoundError(chapter_id)
        if chapter_id == "conflict":
            raise ChapterWriteConflictError(chapter_id, expected_version=1, actual_version=2)
        return _record(id=chapter_id, content_md=data.content_md, word_count=len(data.content_md.split()), version=data.expected_version + 1)

    async def update_metadata(self, chapter_id, data: ChapterMetadataUpdate, *, session=None):
        if chapter_id == "missing":
            raise ChapterNotFoundError(chapter_id)
        if data.status is not None and data.status not in ("draft", "review", "approved", "published"):
            raise InvalidChapterStatusError(data.status)
        return _record(id=chapter_id, status=data.status or "draft", title=data.title or "Intro", version=data.expected_version + 1)

    async def list_versions(self, chapter_id, *, session=None):
        if chapter_id == "missing":
            raise ChapterNotFoundError(chapter_id)
        now = datetime.now(timezone.utc)
        return [
            ChapterVersionRecord(
                chapter_id=chapter_id, version=1, change_kind="WRITE", title="Intro",
                status="draft", content_md=None, summary=None, word_count=0, changed_at=now,
            )
        ]

    async def copy_demo_structure(self, *, session=None):
        return {"created": [_record(title="Capitolo demo")], "skipped_titles": []}


@pytest.fixture
def client(monkeypatch):
    import app.api.chapters as chapters_mod

    monkeypatch.setattr(chapters_mod, "_service", FakeChapterService())
    return TestClient(app)


def test_create_chapter_201(client):
    r = client.post("/chapters", json={"title": "Introduction"})
    assert r.status_code == 201
    assert r.json()["title"] == "Introduction"
    assert r.json()["status"] == "draft"


def test_create_invalid_status_422(client):
    r = client.post("/chapters", json={"title": "X", "status": "banana"})
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_status"


def test_list_chapters_requires_project_id(client):
    r = client.get("/chapters")
    assert r.status_code == 422


def test_list_chapters_rejects_blank_project_id(client):
    r = client.get("/chapters", params={"project_id": ""})
    assert r.status_code == 422


def test_list_chapters_scoped(client):
    r = client.get("/chapters", params={"project_id": "thesis-agent"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_chapter_404(client):
    r = client.get("/chapters/missing")
    assert r.status_code == 404
    assert r.json()["code"] == "chapter_not_found"


def test_patch_content(client):
    r = client.patch("/chapters/ch-9", json={"content_md": "one two three", "expected_version": 1})
    assert r.status_code == 200
    assert r.json()["word_count"] == 3
    assert r.json()["version"] == 2


def test_patch_metadata_status(client):
    r = client.patch("/chapters/ch-9", json={"status": "review", "expected_version": 1})
    assert r.status_code == 200
    assert r.json()["status"] == "review"


def test_patch_requires_expected_version(client):
    # FastAPI request validation (ChapterUpdate.expected_version required) → 422.
    r = client.patch("/chapters/ch-9", json={"content_md": "x"})
    assert r.status_code == 422


def test_patch_conflict_409(client):
    r = client.patch("/chapters/conflict", json={"content_md": "x", "expected_version": 1})
    assert r.status_code == 409
    assert r.json()["code"] == "write_conflict"


def test_list_versions(client):
    r = client.get("/chapters/ch-1/versions")
    assert r.status_code == 200
    assert r.json()[0]["change_kind"] == "WRITE"


def test_delete_chapter_204(client):
    r = client.delete("/chapters/ch-9")
    assert r.status_code == 204


def test_delete_chapter_404(client):
    r = client.delete("/chapters/missing")
    assert r.status_code == 404
    assert r.json()["code"] == "chapter_not_found"


def test_delete_protected_chapter_403(client):
    r = client.delete("/chapters/protected")
    assert r.status_code == 403
    assert r.json()["code"] == "chapter_not_deletable"


def test_copy_demo_structure_201(client):
    r = client.post("/chapters/copy-demo-structure")
    assert r.status_code == 201
    body = r.json()
    assert len(body["created"]) == 1
    assert body["created"][0]["title"] == "Capitolo demo"


def test_outline_not_wired_in_m6():
    """Outline management is M8 — M6 must not serve /outline."""
    r = TestClient(app).get("/outline")
    assert r.status_code == 404
