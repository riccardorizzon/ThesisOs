"""Cross-thesis isolation suite (ADR-0047 INV-MTW-2).

Every domain gets a test proving thesis B cannot see thesis A's data and that
requests without an explicit project keep today's Default Thesis behaviour
(INV-MTW-1).
"""

import pytest

from app.schemas.document import DocumentListFilters, DocumentUploadMetadata
from app.services.document import DocumentService
from app.services.document.storage import LocalStorageAdapter


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
