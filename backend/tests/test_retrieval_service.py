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


class CountingLLM:
    """Records embed calls; optional permanent failure from call N onward."""

    def __init__(self, *, fail_from_call: int | None = None):
        self.calls: list[list[str]] = []
        self.fail_from_call = fail_from_call
        self.call_count = 0

    async def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        self.call_count += 1
        if self.fail_from_call is not None and self.call_count >= self.fail_from_call:
            raise RuntimeError("400 BadRequest: simulated permanent batch failure")
        self.calls.append(list(texts))
        return [[0.01] * EMBEDDING_DIM for _ in texts]


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


async def _embedding_count_for_document(db_session, document_id: str) -> int:
    chunk_ids = (
        await db_session.execute(
            select(models.Chunk.id).where(models.Chunk.document_id == document_id)
        )
    ).scalars().all()
    if not chunk_ids:
        return 0
    return (
        await db_session.execute(
            select(func.count())
            .select_from(models.Embedding)
            .where(
                models.Embedding.owner_type == "chunk",
                models.Embedding.owner_id.in_(chunk_ids),
            )
        )
    ).scalar_one()


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

    embed_count = await _embedding_count_for_document(db_session, doc_id)
    assert embed_count == 2


async def test_embed_document_is_idempotent(retrieval: RetrievalService, svc: DocumentService, db_session):
    doc_id = await _parsed_document(svc, db_session)
    first = await retrieval.embed_document(doc_id, session=db_session)
    second = await retrieval.embed_document(doc_id, session=db_session)
    assert first == 2
    assert second == 0

    embed_count = await _embedding_count_for_document(db_session, doc_id)
    assert embed_count == 2


async def test_embed_failed_surfaces_error(svc: DocumentService, db_session):
    doc_id = await _parsed_document(svc, db_session)
    retrieval = RetrievalService(llm=FailingLLM(), documents=svc)
    with pytest.raises(EmbedFailedError):
        await retrieval.embed_document(doc_id, session=db_session)

    doc = await svc.get(doc_id, session=db_session)
    assert doc.status == "parsed"


async def _parsed_document_with_chunks(
    svc: DocumentService, db_session, chunks: list[str]
) -> str:
    rec = await svc.upload(filename="a.pdf", data=b"x", session=db_session)
    parsed = await svc.parse(
        rec.id, primary=FakeParser(chunks), session=db_session
    )
    assert parsed.status == "parsed"
    return rec.id


async def test_embed_document_single_batch(svc: DocumentService, db_session):
    doc_id = await _parsed_document_with_chunks(svc, db_session, ["small one", "small two"])
    llm = CountingLLM()
    retrieval = RetrievalService(llm=llm, documents=svc)
    count = await retrieval.embed_document(doc_id, session=db_session)
    assert count == 2
    assert llm.call_count == 1
    assert len(llm.calls[0]) == 2


async def test_embed_document_multi_batch(svc: DocumentService, db_session):
    # 15 x 4000 chars => ~1000 tokens each => 2 batches under 14k default cap.
    chunks = ["a" * 4000] * 15
    doc_id = await _parsed_document_with_chunks(svc, db_session, chunks)
    llm = CountingLLM()
    retrieval = RetrievalService(llm=llm, documents=svc)
    count = await retrieval.embed_document(doc_id, session=db_session)
    assert count == 15
    assert llm.call_count == 2
    assert len(llm.calls[0]) == 14
    assert len(llm.calls[1]) == 1
    assert llm.calls[0] + llm.calls[1] == chunks


async def test_embed_document_batch_failure_no_partial_embeddings(
    svc: DocumentService, db_session
):
    chunks = ["a" * 4000] * 15
    doc_id = await _parsed_document_with_chunks(svc, db_session, chunks)
    llm = CountingLLM(fail_from_call=2)
    retrieval = RetrievalService(llm=llm, documents=svc)
    with pytest.raises(EmbedFailedError):
        await retrieval.embed_document(doc_id, session=db_session)

    doc = await svc.get(doc_id, session=db_session)
    assert doc.status == "parsed"
    embed_count = await _embedding_count_for_document(db_session, doc_id)
    assert embed_count == 0


async def test_delete_document_removes_embeddings(
    retrieval: RetrievalService, svc: DocumentService, db_session
):
    doc_id = await _parsed_document(svc, db_session)
    await retrieval.embed_document(doc_id, session=db_session)
    assert await _embedding_count_for_document(db_session, doc_id) == 2
    await svc.delete(doc_id, session=db_session)

    embed_count = await _embedding_count_for_document(db_session, doc_id)
    assert embed_count == 0
