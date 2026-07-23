"""Cross-thesis isolation suite (ADR-0047 INV-MTW-2).

Every domain gets a test proving thesis B cannot see thesis A's data and that
requests without an explicit project keep today's Default Thesis behaviour
(INV-MTW-1).
"""

import pytest

from app.db.models import EMBEDDING_DIM
from app.schemas.document import DocumentListFilters, DocumentUploadMetadata
from app.schemas.retrieval import SearchFilters
from app.services.document import DocumentService
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter
from app.services.retrieval import RetrievalService


class _FakeParser:
    def __init__(self, chunks: list[str]):
        self.name = "docling"
        self._result = ParseResult(
            parser="docling", chunks=[ParsedChunk(content=c) for c in chunks]
        )

    def parse(self, data, source_type):
        return self._result


class _FakeLLM:
    async def embed(self, texts, *, model=None):
        return [[0.01] * EMBEDDING_DIM for _ in texts]


@pytest.fixture
def doc_svc(tmp_path) -> DocumentService:
    return DocumentService(storage=LocalStorageAdapter(tmp_path))


async def test_documents_default_to_thesis_agent(doc_svc, db_session):
    rec = await doc_svc.upload(filename="main.pdf", data=b"%PDF", session=db_session)
    assert rec.project_id == "thesis-agent"
    listed = await doc_svc.list(session=db_session)
    assert [d.id for d in listed] == [rec.id]


async def test_documents_isolated_per_project(doc_svc, db_session):
    main = await doc_svc.upload(filename="main.pdf", data=b"%PDF", session=db_session)
    other = await doc_svc.upload(
        filename="other.pdf",
        data=b"%PDF",
        meta=DocumentUploadMetadata(project_id="thesis-002"),
        session=db_session,
    )
    assert other.project_id == "thesis-002"

    default_list = await doc_svc.list(session=db_session)
    assert {d.id for d in default_list} == {main.id}

    other_list = await doc_svc.list(
        DocumentListFilters(project_id="thesis-002"), session=db_session
    )
    assert {d.id for d in other_list} == {other.id}

    empty = await doc_svc.list(
        DocumentListFilters(project_id="thesis-003"), session=db_session
    )
    assert empty == []


async def _indexed_document(doc_svc, db_session, *, project_id, chunks):
    retrieval = RetrievalService(llm=_FakeLLM(), documents=doc_svc)
    meta = DocumentUploadMetadata(project_id=project_id)
    rec = await doc_svc.upload(
        filename=f"{project_id or 'default'}.pdf", data=b"%PDF", meta=meta, session=db_session
    )
    await doc_svc.parse(rec.id, primary=_FakeParser(chunks), session=db_session)
    await retrieval.embed_document(rec.id, session=db_session)
    return rec.id


async def test_retrieval_isolated_per_project(doc_svc, db_session):
    retrieval = RetrievalService(llm=_FakeLLM(), documents=doc_svc)
    main_doc = await _indexed_document(
        doc_svc, db_session, project_id=None, chunks=["moda e processo creativo"]
    )
    other_doc = await _indexed_document(
        doc_svc, db_session, project_id="thesis-002", chunks=["storia del diritto romano"]
    )

    default_results, _ = await retrieval.search("processo", session=db_session)
    assert {r.document_id for r in default_results} == {main_doc}

    other_results, _ = await retrieval.search(
        "processo", filters=SearchFilters(project_id="thesis-002"), session=db_session
    )
    assert {r.document_id for r in other_results} == {other_doc}

    empty_results, _ = await retrieval.search(
        "processo", filters=SearchFilters(project_id="thesis-003"), session=db_session
    )
    assert empty_results == []


async def test_upload_registers_source_in_same_project(doc_svc, db_session):
    from sqlalchemy import text

    rec = await doc_svc.upload(
        filename="scoped.pdf",
        data=b"%PDF",
        meta=DocumentUploadMetadata(project_id="thesis-002"),
        session=db_session,
    )
    row = (
        await db_session.execute(
            text("SELECT project_id FROM sources WHERE slug = :slug"),
            {"slug": rec.id},
        )
    ).one()
    assert row.project_id == "thesis-002"
