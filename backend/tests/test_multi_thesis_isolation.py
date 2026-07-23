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


async def test_memories_isolated_per_project(db_session):
    from app.schemas.memory import MemoryCreate, MemoryListFilters
    from app.services.memory import MemoryService

    svc = MemoryService()
    main = await svc.create(
        MemoryCreate(kind="user", content="ricercatore moda", pinned=True),
        session=db_session,
    )
    assert main.project_id == "thesis-agent"

    # Same singleton kind in another thesis must NOT collide (per-project singleton).
    other = await svc.create(
        MemoryCreate(project_id="thesis-002", kind="user", content="giurista", pinned=True),
        session=db_session,
    )
    assert other.project_id == "thesis-002"

    default_list = await svc.list(session=db_session)
    assert {m.id for m in default_list} == {main.id}

    other_list = await svc.list(
        MemoryListFilters(project_id="thesis-002"), session=db_session
    )
    assert {m.id for m in other_list} == {other.id}


async def test_prompt_context_isolated_per_project(db_session):
    from app.schemas.memory import MemoryCreate, PromptContextFilters
    from app.services.memory import MemoryService

    svc = MemoryService()
    await svc.create(
        MemoryCreate(kind="thesis", content="tesi sul fashion design", pinned=True),
        session=db_session,
    )
    filters = PromptContextFilters(include_pinned_thesis=True)

    default_ctx = await svc.load_prompt_context(filters=filters, session=db_session)
    assert len(default_ctx.thesis) == 1

    other_ctx = await svc.load_prompt_context(
        project_id="thesis-002", filters=filters, session=db_session
    )
    assert other_ctx.thesis == []


async def test_conversations_isolated_per_project(db_session):
    from app.services.conversation.exceptions import ConversationProjectMismatchError
    from app.services.conversation.service import ConversationService

    svc = ConversationService()
    main = await svc.create_conversation("thesis-agent", title="Sessione moda")
    other = await svc.create_conversation("thesis-002", title="Sessione diritto")
    assert main.project_id == "thesis-agent"
    assert other.project_id == "thesis-002"

    main_list = await svc.list_conversations("thesis-agent")
    assert {c.id for c in main_list.items} == {main.id}
    other_list = await svc.list_conversations("thesis-002")
    assert {c.id for c in other_list.items} == {other.id}

    # A thread can never migrate to another thesis (INV-MTW-2).
    from app.db.session_async import AsyncSessionLocal

    async with AsyncSessionLocal() as s:
        with pytest.raises(ConversationProjectMismatchError):
            await svc._get_or_create_conversation(s, main.id, project_id="thesis-002")


async def test_chapter_ownership_check_hides_foreign_chapters(db_session):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.schemas.chapter import ChapterCreate
    from app.services.chapter import ChapterService

    chapter = await ChapterService().create(
        ChapterCreate(title="Cap. moda", project_id="thesis-agent"), session=db_session
    )
    await db_session.commit()

    client = TestClient(app)
    own = client.get(f"/chapters/{chapter.id}", params={"project_id": "thesis-agent"})
    assert own.status_code == 200

    foreign = client.get(f"/chapters/{chapter.id}", params={"project_id": "thesis-002"})
    assert foreign.status_code == 404

    legacy = client.get(f"/chapters/{chapter.id}")
    assert legacy.status_code == 200  # INV-MTW-1


async def test_copy_demo_structure_targets_requested_project(db_session):
    from app.schemas.chapter import ChapterCreate, ChapterListFilters
    from app.services.chapter import ChapterService

    svc = ChapterService()
    await svc.create(
        ChapterCreate(title="Introduzione (dogfood M6)", project_id="demo-thesis"),
        session=db_session,
    )
    result = await svc.copy_demo_structure(project_id="thesis-002", session=db_session)
    assert len(result.created) == 1
    assert result.created[0].project_id == "thesis-002"

    target = await svc.list(
        ChapterListFilters(project_id="thesis-002"), session=db_session
    )
    assert {c.project_id for c in target} == {"thesis-002"}
    default_side = await svc.list(
        ChapterListFilters(project_id="thesis-agent"), session=db_session
    )
    assert default_side == []


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
