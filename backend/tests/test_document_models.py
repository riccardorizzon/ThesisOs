from app.db.models import Chunk, Document, DocumentVersion


def test_document_has_m3_columns():
    cols = {c.name for c in Document.__table__.columns}
    assert {"version", "parser", "parsed_at", "chunk_count", "error_message"}.issubset(cols)


def test_document_default_status_is_uploaded():
    assert Document.__table__.columns["status"].default.arg == "uploaded"


def test_chunk_has_chunk_hash():
    assert "chunk_hash" in Chunk.__table__.columns


def test_chunk_unique_constraints():
    names = {c.name for c in Chunk.__table__.constraints if hasattr(c, "name") and c.name}
    assert "uq_chunks_document_id_chunk_index" in names
    assert "uq_chunks_document_id_chunk_hash" in names


def test_document_version_table():
    assert DocumentVersion.__tablename__ == "document_versions"
    cols = {c.name for c in DocumentVersion.__table__.columns}
    assert cols == {
        "id",
        "document_id",
        "version",
        "title",
        "author",
        "source_type",
        "page_count",
        "chunk_count",
        "parser",
        "metadata",
        "changed_at",
        "change_reason",
    }


def test_document_version_fk_cascade():
    fks = list(DocumentVersion.__table__.foreign_keys)
    assert len(fks) == 1
    assert fks[0].column.table.name == "documents"
    assert fks[0].ondelete == "CASCADE"


def test_document_version_unique_per_version():
    names = {c.name for c in DocumentVersion.__table__.constraints if hasattr(c, "name") and c.name}
    assert "uq_document_versions_document_id_version" in names
