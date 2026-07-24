import pytest

from app.schemas.document import DocumentListFilters, DocumentUpdate, DocumentUploadMetadata
from app.services.document import (
    DocumentNotFoundError,
    DocumentService,
    DocumentServiceError,
    DocumentWriteConflictError,
    ParseError,
    UnsupportedFormatError,
)
from app.services.document.parsers.base import ParsedChunk, ParseResult
from app.services.document.storage import LocalStorageAdapter


class FakeParser:
    def __init__(self, name, *, result=None, error=None):
        self.name = name
        self._result = result
        self._error = error

    def parse(self, data, source_type):
        if self._error is not None:
            raise self._error
        return self._result


@pytest.fixture
def svc(tmp_path) -> DocumentService:
    return DocumentService(storage=LocalStorageAdapter(tmp_path))


def _docling(chunks):
    return FakeParser(
        "docling",
        result=ParseResult(parser="docling", chunks=[ParsedChunk(content=c) for c in chunks]),
    )


async def test_upload_creates_uploaded_with_initial_version(svc, db_session):
    rec = await svc.upload(
        filename="paper.pdf",
        data=b"%PDF fake",
        meta=DocumentUploadMetadata(title="My Paper"),
        session=db_session,
    )
    assert rec.status == "uploaded"
    assert rec.source_type == "pdf"
    assert rec.version == 1
    assert rec.title == "My Paper"
    assert rec.gcs_uri.startswith("local://documents/")

    versions = await svc.list_versions(rec.id, session=db_session)
    assert [v.version for v in versions] == [1]
    assert versions[0].change_reason == "metadata"


async def test_upload_rejects_disguised_pdf_before_persistence(svc, db_session):
    with pytest.raises(DocumentServiceError, match="invalid_file_content"):
        await svc.upload(
            filename="fake.pdf",
            data=b"plain text pretending to be a pdf",
            session=db_session,
        )

    assert await svc.list(
        DocumentListFilters(project_id="thesis-agent"),
        session=db_session,
    ) == []


async def test_parse_success_creates_ordered_chunks(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"%PDF test", session=db_session)
    parsed = await svc.parse(rec.id, primary=_docling(["alpha", "beta"]), session=db_session)
    assert parsed.status == "parsed"
    assert parsed.parser == "docling"
    assert parsed.chunk_count == 2
    assert parsed.version == 2

    chunks = await svc.list_chunks(rec.id, session=db_session)
    assert [c.chunk_index for c in chunks] == [0, 1]
    assert all(c.chunk_hash for c in chunks)
    assert all(c.token_count for c in chunks)


async def test_reparse_keeps_hash_changes_ids(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"%PDF test", session=db_session)
    parser = _docling(["alpha", "beta"])
    await svc.parse(rec.id, primary=parser, session=db_session)
    first = await svc.list_chunks(rec.id, session=db_session)
    reparsed = await svc.reparse(rec.id, primary=parser, session=db_session)
    second = await svc.list_chunks(rec.id, session=db_session)

    assert [c.chunk_hash for c in first] == [c.chunk_hash for c in second]
    assert {c.id for c in first}.isdisjoint({c.id for c in second})
    assert reparsed.version == 3


async def test_parse_failure_marks_failed_with_zero_chunks(svc, db_session):
    rec = await svc.upload(filename="a.docx", data=b"x", session=db_session)
    failing = FakeParser("docling", error=ParseError("bad"))
    parsed = await svc.parse(rec.id, primary=failing, session=db_session)
    assert parsed.status == "failed"
    assert parsed.error_message
    assert await svc.list_chunks(rec.id, session=db_session) == []


async def test_update_optimistic_lock(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"%PDF test", session=db_session)
    updated = await svc.update(
        rec.id, DocumentUpdate(title="New Title", expected_version=1), session=db_session
    )
    assert updated.title == "New Title"
    assert updated.version == 2
    with pytest.raises(DocumentWriteConflictError):
        await svc.update(
            rec.id, DocumentUpdate(title="Stale", expected_version=1), session=db_session
        )


async def test_delete_cascades(svc, db_session):
    rec = await svc.upload(filename="a.pdf", data=b"%PDF test", session=db_session)
    await svc.parse(rec.id, primary=_docling(["alpha"]), session=db_session)
    await svc.delete(rec.id, session=db_session)
    with pytest.raises(DocumentNotFoundError):
        await svc.get(rec.id, session=db_session)


async def test_list_filters_by_type_and_title(svc, db_session):
    await svc.upload(
        filename="alpha.pdf",
        data=b"%PDF test",
        meta=DocumentUploadMetadata(title="Alpha"),
        session=db_session,
    )
    await svc.upload(
        filename="beta.docx", data=b"y", meta=DocumentUploadMetadata(title="Beta"),
        session=db_session,
    )
    pdfs = await svc.list(DocumentListFilters(source_type="pdf"), session=db_session)
    assert pdfs and all(d.source_type == "pdf" for d in pdfs)
    by_title = await svc.list(DocumentListFilters(q="Alpha"), session=db_session)
    assert any(d.title == "Alpha" for d in by_title)


async def test_upload_rejects_unsupported_format(svc, db_session):
    with pytest.raises(UnsupportedFormatError):
        await svc.upload(filename="notes.xyz", data=b"x", session=db_session)


async def test_upload_markdown_infers_source_type(svc, db_session):
    rec = await svc.upload(filename="chapter.md", data=b"# Intro\n\nBody text.", session=db_session)
    assert rec.status == "uploaded"
    assert rec.source_type == "markdown"


async def test_parse_markdown_uses_native_parser(svc, db_session):
    rec = await svc.upload(filename="chapter.md", data=b"# Intro\n\nBody text.", session=db_session)
    parsed = await svc.parse(rec.id, session=db_session)
    assert parsed.status == "parsed"
    assert parsed.parser == "markdown"
    assert parsed.chunk_count >= 1
    chunks = await svc.list_chunks(rec.id, session=db_session)
    assert any("Body text" in c.content for c in chunks)
