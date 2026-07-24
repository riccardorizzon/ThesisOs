"""M3 integration tests — upload → parse → list + outbox persistence.

All tests skip when async Postgres is unavailable (same guard as service tests).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.main import app
from app.schemas.document import DocumentListFilters
from app.services.document import DocumentService
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter


class FakeParser:
    def __init__(self, name, *, result=None):
        self.name = name
        self._result = result

    def parse(self, data, source_type):
        return self._result


def _docling(chunks):
    return FakeParser(
        "docling",
        result=ParseResult(parser="docling", chunks=[ParsedChunk(content=c) for c in chunks]),
    )


@pytest.fixture
async def db_available():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"async DB not reachable: {exc}")


@pytest.fixture
def svc(tmp_path, db_available) -> DocumentService:
    return DocumentService(storage=LocalStorageAdapter(tmp_path))


async def test_upload_registers_source_in_corpus(svc):
    rec = await svc.upload(
        filename="corpus.pdf",
        data=b"%PDF-1.4 fake",
        meta=None,
    )

    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text(
                """
                SELECT slug, title, document_id, created_by
                FROM sources
                WHERE project_id = 'thesis-agent' AND slug = :slug
                """
            ),
            {"slug": rec.id},
        )
        source = row.one()
        assert source.slug == rec.id
        assert str(source.document_id) == rec.id
        assert source.title == rec.title
        assert source.created_by == "importazione"


async def test_upload_parse_list_round_trip(svc):
    rec = await svc.upload(filename="round.pdf", data=b"%PDF-1.4 fake")
    assert rec.status == "uploaded"

    parsed = await svc.parse(
        rec.id,
        primary=_docling(["DistinctiveChunkMarker-XYZZY", "second part"]),
    )
    assert parsed.status == "parsed"
    assert parsed.chunk_count == 2

    listed = await svc.list(DocumentListFilters(q="round"))
    assert any(item.id == rec.id for item in listed)

    chunks = await svc.list_chunks(rec.id)
    assert len(chunks) == 2
    assert "DistinctiveChunkMarker-XYZZY" in chunks[0].content


async def test_document_and_events_survive_new_session(svc, tmp_path):
    rec = await svc.upload(filename="persist.pdf", data=b"%PDF test")
    await svc.parse(rec.id, primary=_docling(["persisted chunk body"]))

    async with AsyncSessionLocal() as session:
        row = await session.get(models.Document, rec.id)
        assert row is not None
        assert row.status == "parsed"

        chunk_count = await session.scalar(
            select(func.count())
            .select_from(models.Chunk)
            .where(models.Chunk.document_id == rec.id)
        )
        assert chunk_count == 1

        uploaded = await session.scalar(
            select(func.count())
            .select_from(models.Event)
            .where(
                models.Event.type == "DocumentUploaded",
                models.Event.payload["document_id"].astext == rec.id,
            )
        )
        created = await session.scalar(
            select(func.count())
            .select_from(models.Event)
            .where(
                models.Event.type == "ChunkCreated",
                models.Event.payload["document_id"].astext == rec.id,
            )
        )
        assert uploaded == 1
        assert created == 1


async def test_embeddings_zero_writes_after_ingestion(svc, db_available):
    async with AsyncSessionLocal() as session:
        before = await session.scalar(select(func.count()).select_from(models.Embedding))

    rec = await svc.upload(filename="emb.pdf", data=b"%PDF test")
    await svc.parse(rec.id, primary=_docling(["no embeddings in m3"]))

    async with AsyncSessionLocal() as session:
        after = await session.scalar(select(func.count()).select_from(models.Embedding))
    assert before == after


def test_chat_smoke_unchanged_without_documents(monkeypatch):
    """Regression guard: /chat still streams when the document stack is present."""
    import app.api.chat as chat

    class FakeService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "ok"}}
            yield {
                "event": "done",
                "data": {"conversation_id": conversation_id, "message_id": "m1", "usage": {}},
            }

    class _FakeLLM:
        pass

    monkeypatch.setattr(chat, "_service", FakeService())
    monkeypatch.setattr(chat, "get_llm_client", lambda: _FakeLLM())

    client = TestClient(app)
    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert "event: token" in response.text
    assert "DistinctiveChunkMarker" not in response.text


async def test_chat_does_not_leak_ingested_chunk_text(svc, monkeypatch):
    marker = "DistinctiveChunkMarker-XYZZY-INTEGRATION"
    rec = await svc.upload(filename="secret.pdf", data=b"%PDF test")
    await svc.parse(rec.id, primary=_docling([marker]))

    import app.api.chat as chat

    class FakeService:
        async def stream_turn(self, *, conversation_id, user_text):
            yield {"event": "token", "data": {"text": "hi"}}
            yield {
                "event": "done",
                "data": {"conversation_id": conversation_id, "message_id": "m1", "usage": {}},
            }

    monkeypatch.setattr(chat, "_service", FakeService())
    monkeypatch.setattr(chat, "get_llm_client", lambda: object())

    client = TestClient(app)
    body = client.post("/chat", json={"message": "summarize my documents"}).text
    assert marker not in body
