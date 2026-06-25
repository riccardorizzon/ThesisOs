"""RetrievalService unit tests (M4 Phase 2)."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select, text

from app.db import models
from app.db.models import EMBEDDING_DIM
from app.services.document import DocumentService
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter
from app.services.retrieval import EmbedFailedError, RetrievalService


class FakeParser:
    def __init__(self, chunks: list[str]):
        self.name = "docling"
        self._result = ParseResult(
            parser="docling",
            chunks=[ParsedChunk(content=c) for c in chunks],
        )

    def parse(self, data, source_type):
        return self._result


class FakeLLM:
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        return [[0.01] * EMBEDDING_DIM for _ in texts]


class FailingLLM:
    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        raise RuntimeError("vertex unavailable")


@pytest.fixture
async def db_session():
    from app.db.session_async import AsyncSessionLocal

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


@pytest.fixture
def retrieval(svc: DocumentService) -> RetrievalService:
    return RetrievalService(llm=FakeLLM(), documents=svc)


async def _parsed_document(svc: DocumentService, db_session) -> str:
    rec = await svc.upload(filename="a.pdf", data=b"x", session=db_session)
    parsed = await svc.parse(
        rec.id, primary=FakeParser(["alpha chunk", "beta chunk"]), session=db_session
    )
    assert parsed.status == "parsed"
    return rec.id


async def test_embed_document_writes_embeddings_and_marks_indexed(
    retrieval: RetrievalService, svc: DocumentService, db_session
):
    doc_id = await _parsed_document(svc, db_session)
    count = await retrieval.embed_document(doc_id, session=db_session)
    assert count == 2

    doc = await svc.get(doc_id, session=db_session)
    assert doc.status == "indexed"

    embed_count = (
        await db_session.execute(select(func.count()).select_from(models.Embedding))
    ).scalar_one()
    assert embed_count == 2


async def test_embed_document_is_idempotent(retrieval: RetrievalService, svc: DocumentService, db_session):
    doc_id = await _parsed_document(svc, db_session)
    first = await retrieval.embed_document(doc_id, session=db_session)
    second = await retrieval.embed_document(doc_id, session=db_session)
    assert first == 2
    assert second == 0

    embed_count = (
        await db_session.execute(select(func.count()).select_from(models.Embedding))
    ).scalar_one()
    assert embed_count == 2


async def test_embed_failed_surfaces_error(svc: DocumentService, db_session):
    doc_id = await _parsed_document(svc, db_session)
    retrieval = RetrievalService(llm=FailingLLM(), documents=svc)
    with pytest.raises(EmbedFailedError):
        await retrieval.embed_document(doc_id, session=db_session)

    doc = await svc.get(doc_id, session=db_session)
    assert doc.status == "parsed"


async def test_delete_document_removes_embeddings(
    retrieval: RetrievalService, svc: DocumentService, db_session
):
    doc_id = await _parsed_document(svc, db_session)
    await retrieval.embed_document(doc_id, session=db_session)
    await svc.delete(doc_id, session=db_session)

    embed_count = (
        await db_session.execute(select(func.count()).select_from(models.Embedding))
    ).scalar_one()
    assert embed_count == 0
