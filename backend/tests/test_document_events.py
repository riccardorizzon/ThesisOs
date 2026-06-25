from __future__ import annotations

import pytest
from sqlalchemy import select, text

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.document import DocumentUploadMetadata
from app.services.document import DocumentService
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter
from app.services.events.bus import UnknownEventError, publish


class FakeParser:
    def __init__(self, name, *, result=None):
        self.name = name
        self._result = result

    def parse(self, data, source_type):
        return self._result


@pytest.fixture
async def db_session():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"async DB not reachable: {exc}")
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def svc(tmp_path) -> DocumentService:
    return DocumentService(storage=LocalStorageAdapter(tmp_path))


def _docling(chunks):
    return FakeParser(
        "docling",
        result=ParseResult(parser="docling", chunks=[ParsedChunk(content=c) for c in chunks]),
    )


async def _events_for_document(session, document_id: str) -> list[models.Event]:
    rows = (
        await session.execute(
            select(models.Event)
            .where(models.Event.payload["document_id"].astext == document_id)
            .order_by(models.Event.created_at)
        )
    ).scalars().all()
    uploaded = (
        await session.execute(
            select(models.Event).where(
                models.Event.type == "DocumentUploaded",
                models.Event.payload["document_id"].astext == document_id,
            )
        )
    ).scalar_one_or_none()
    if uploaded is not None and uploaded not in rows:
        rows = [uploaded, *rows]
    by_id = {e.id: e for e in rows}
    return list(by_id.values())


async def test_publish_rejects_unknown_event(db_session):
    with pytest.raises(UnknownEventError):
        await publish("NotInCatalog", {"x": 1}, session=db_session)


async def test_upload_emits_document_uploaded(svc, db_session):
    rec = await svc.upload(
        filename="paper.pdf",
        data=b"%PDF fake",
        meta=DocumentUploadMetadata(title="Paper"),
        session=db_session,
    )
    events = await _events_for_document(db_session, rec.id)
    uploaded = [e for e in events if e.type == "DocumentUploaded"]
    assert len(uploaded) == 1
    assert uploaded[0].payload == {"document_id": rec.id}
    assert uploaded[0].source == "document_service"


async def test_parse_emits_chunk_created_per_chunk(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"x", session=db_session)
    await svc.parse(rec.id, primary=_docling(["alpha", "beta"]), session=db_session)

    events = (
        await db_session.execute(
            select(models.Event)
            .where(models.Event.type == "ChunkCreated")
            .where(models.Event.payload["document_id"].astext == rec.id)
            .order_by(models.Event.payload["chunk_id"].astext)
        )
    ).scalars().all()
    assert len(events) == 2
    assert all(e.payload["document_id"] == rec.id for e in events)
    assert all(e.payload.get("chunk_hash") for e in events)
    assert len({e.payload["chunk_id"] for e in events}) == 2


async def test_parse_failure_emits_no_chunk_events(svc, db_session):
    from app.services.document import ParseError

    rec = await svc.upload(filename="a.docx", data=b"x", session=db_session)
    failing = FakeParser("docling")
    failing.parse = lambda data, source_type: (_ for _ in ()).throw(ParseError("bad"))
    await svc.parse(rec.id, primary=failing, session=db_session)

    chunk_events = (
        await db_session.execute(
            select(models.Event).where(
                models.Event.type == "ChunkCreated",
                models.Event.payload["document_id"].astext == rec.id,
            )
        )
    ).scalars().all()
    assert chunk_events == []


async def test_reparse_emits_fresh_chunk_events(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"x", session=db_session)
    parser = _docling(["alpha", "beta"])
    await svc.parse(rec.id, primary=parser, session=db_session)
    first_count = (
        await db_session.execute(
            select(models.Event).where(
                models.Event.type == "ChunkCreated",
                models.Event.payload["document_id"].astext == rec.id,
            )
        )
    ).scalars().all()
    assert len(first_count) == 2

    await svc.reparse(rec.id, primary=parser, session=db_session)
    all_chunk_events = (
        await db_session.execute(
            select(models.Event).where(
                models.Event.type == "ChunkCreated",
                models.Event.payload["document_id"].astext == rec.id,
            )
        )
    ).scalars().all()
    assert len(all_chunk_events) == 4
