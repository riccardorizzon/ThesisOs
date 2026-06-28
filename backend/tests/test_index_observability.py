"""Background indexing observability tests (M4 recovery, bug-4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import func, select, text

from app.api.documents import _parse_in_background
from app.db import models
from app.services.document import DocumentService
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter
from app.services.retrieval import EmbedFailedError, RetrievalService


class FakeParser:
    name = "docling"

    def parse(self, data, source_type):
        return ParseResult(parser="docling", chunks=[ParsedChunk(content="chunk")])


@pytest.fixture
def svc(tmp_path) -> DocumentService:
    return DocumentService(storage=LocalStorageAdapter(tmp_path))


async def test_record_index_error_sets_message(svc: DocumentService, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"x", session=db_session)
    await svc.parse(rec.id, primary=FakeParser(), session=db_session)
    updated = await svc.record_index_error(rec.id, "vertex token limit", session=db_session)
    assert updated.error_message.startswith("index_failed:")
    assert "vertex token limit" in updated.error_message
    row = await svc.get(rec.id, session=db_session)
    assert row.status == "parsed"


async def test_background_index_failure_records_error(svc: DocumentService):
    from app.db.session_async import AsyncSessionLocal

    async with AsyncSessionLocal() as s:
        rec = await svc.upload(filename="a.pdf", data=b"x", session=s)
        await svc.parse(rec.id, primary=FakeParser(), session=s)
        doc_id = rec.id
        await s.commit()

    parsed = await svc.get(doc_id)

    with patch("app.api.documents._service.parse", AsyncMock(return_value=parsed)):
        with patch.object(
            RetrievalService,
            "embed_document",
            AsyncMock(side_effect=EmbedFailedError("503 unavailable")),
        ):
            await _parse_in_background(doc_id)

    row = await svc.get(doc_id)
    assert row.status == "parsed"
    assert row.error_message is not None
    assert "503 unavailable" in row.error_message

    async with AsyncSessionLocal() as s:
        chunk_ids = (
            await s.execute(
                select(models.Chunk.id).where(models.Chunk.document_id == doc_id)
            )
        ).scalars().all()
        embed_count = (
            await s.execute(
                select(func.count())
                .select_from(models.Embedding)
                .where(
                    models.Embedding.owner_type == "chunk",
                    models.Embedding.owner_id.in_(chunk_ids),
                )
            )
        ).scalar_one()
    assert embed_count == 0
