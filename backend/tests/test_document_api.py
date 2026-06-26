from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.schemas.document import (
    DocumentChunk,
    DocumentRecord,
    DocumentUpdate,
    DocumentVersionRecord,
)
from app.services.document import (
    DocumentNotFoundError,
    DocumentWriteConflictError,
    UnsupportedFormatError,
)


def _record(**kwargs) -> DocumentRecord:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id="doc-1",
        title="Doc",
        source_type="pdf",
        status="uploaded",
        version=1,
        metadata={},
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return DocumentRecord(**defaults)


class FakeDocumentService:
    def __init__(self):
        self.calls: list[tuple] = []

    async def upload(self, *, filename, data, source_type=None, meta=None, session=None):
        self.calls.append(("upload", filename))
        if filename.endswith(".xyz"):
            raise UnsupportedFormatError(filename)
        st = "markdown" if filename.endswith(".md") else "pdf"
        return _record(original_filename=filename, source_type=st, title=(meta.title if meta else None) or "Doc")

    async def list(self, filters, *, session=None):
        self.calls.append(("list", filters))
        return [_record()]

    async def get(self, document_id, *, session=None):
        self.calls.append(("get", document_id))
        if document_id == "missing":
            raise DocumentNotFoundError(document_id)
        return _record(id=document_id)

    async def update(self, document_id, data: DocumentUpdate, *, session=None):
        self.calls.append(("update", document_id, data))
        if document_id == "missing":
            raise DocumentNotFoundError(document_id)
        if document_id == "conflict":
            raise DocumentWriteConflictError(document_id, expected_version=1, actual_version=2)
        return _record(id=document_id, version=data.expected_version + 1, title=data.title or "Doc")

    async def delete(self, document_id, *, session=None):
        self.calls.append(("delete", document_id))
        if document_id == "missing":
            raise DocumentNotFoundError(document_id)

    async def parse(self, document_id, *, primary=None, fallback=None, session=None):
        self.calls.append(("parse", document_id))
        return _record(id=document_id, status="parsed")

    async def reparse(self, document_id, *, primary=None, fallback=None, session=None):
        self.calls.append(("reparse", document_id))
        return _record(id=document_id, status="parsed")

    async def list_chunks(self, document_id, *, session=None):
        self.calls.append(("list_chunks", document_id))
        if document_id == "missing":
            raise DocumentNotFoundError(document_id)
        return [
            DocumentChunk(
                id="c-1",
                document_id=document_id,
                chunk_index=0,
                chunk_hash="h",
                content="text",
                created_at=datetime.now(timezone.utc),
            )
        ]

    async def list_versions(self, document_id, *, session=None):
        self.calls.append(("list_versions", document_id))
        if document_id == "missing":
            raise DocumentNotFoundError(document_id)
        return [
            DocumentVersionRecord(
                document_id=document_id,
                version=1,
                title="Doc",
                source_type="pdf",
                change_reason="metadata",
                changed_at=datetime.now(timezone.utc),
            )
        ]


@pytest.fixture
def fake_service(monkeypatch):
    import app.api.documents as documents_api

    svc = FakeDocumentService()
    monkeypatch.setattr(documents_api, "_service", svc)
    from app.main import app

    return TestClient(app), svc


def test_api_has_no_direct_db_access():
    import app.api.documents as documents_api

    source = open(documents_api.__file__).read()
    assert "app.db.models" not in source
    assert "AsyncSessionLocal" not in source
    assert "select(" not in source


def test_upload_delegates_and_schedules_parse(fake_service):
    client, svc = fake_service
    r = client.post(
        "/upload",
        files={"file": ("paper.pdf", b"%PDF data", "application/pdf")},
        data={"title": "My Paper"},
    )
    assert r.status_code == 201
    assert r.json()["status"] == "uploaded"
    names = [c[0] for c in svc.calls]
    assert "upload" in names
    assert "parse" in names  # background parse ran


def test_upload_unsupported_format_returns_400(fake_service):
    client, _ = fake_service
    r = client.post("/upload", files={"file": ("notes.xyz", b"x", "application/octet-stream")})
    assert r.status_code == 400
    assert r.json()["code"] == "unsupported_format"


def test_list_delegates_with_filters(fake_service):
    client, svc = fake_service
    r = client.get("/documents?source_type=pdf&status=parsed&q=paper")
    assert r.status_code == 200
    assert len(r.json()) == 1
    _, filters = svc.calls[0]
    assert filters.source_type == "pdf"
    assert filters.status == "parsed"
    assert filters.q == "paper"


def test_get_200_and_404(fake_service):
    client, _ = fake_service
    assert client.get("/documents/doc-1").status_code == 200
    r = client.get("/documents/missing")
    assert r.status_code == 404
    assert r.json()["code"] == "document_not_found"


def test_patch_conflict_returns_409(fake_service):
    client, _ = fake_service
    r = client.patch("/documents/conflict", json={"expected_version": 1, "title": "x"})
    assert r.status_code == 409
    assert r.json()["code"] == "write_conflict"


def test_delete_204_and_404(fake_service):
    client, _ = fake_service
    assert client.delete("/documents/doc-1").status_code == 204
    assert client.delete("/documents/missing").status_code == 404


def test_chunks_200_and_404(fake_service):
    client, _ = fake_service
    r = client.get("/documents/doc-1/chunks")
    assert r.status_code == 200
    body = r.json()
    assert body[0]["chunk_index"] == 0
    assert "chunk_hash" in body[0]
    assert client.get("/documents/missing/chunks").status_code == 404


def test_versions_200(fake_service):
    client, svc = fake_service
    r = client.get("/documents/doc-1/versions")
    assert r.status_code == 200
    assert r.json()[0]["version"] == 1
    assert ("list_versions", "doc-1") in svc.calls


def test_reparse_202_and_404(fake_service):
    client, svc = fake_service
    r = client.post("/documents/doc-1/reparse")
    assert r.status_code == 202
    assert r.json()["status"] == "processing"
    assert "parse" in [c[0] for c in svc.calls]  # background parse scheduled
    assert client.post("/documents/missing/reparse").status_code == 404


def test_search_endpoint_exists_requires_body(fake_service):
    client, _ = fake_service
    # M4 — corpus search is POST /search with JSON body (not on /documents).
    assert client.post("/search").status_code == 422
    assert client.post("/search", json={"query": "x"}).status_code != 404


def test_openapi_has_no_document_search_route():
    from pathlib import Path

    openapi = Path(__file__).resolve().parents[2] / "contracts" / "openapi" / "openapi.yaml"
    if not openapi.exists():
        pytest.skip("openapi contract not available")
    text = openapi.read_text()
    assert "/documents/search" not in text
    assert "/search:" in text  # M4 hybrid search (not on /documents)
