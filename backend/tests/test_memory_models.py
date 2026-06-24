from app.db.models import Memory, MemoryVersion


def test_memory_has_title_column():
    assert "title" in Memory.__table__.columns


def test_memory_version_table():
    assert MemoryVersion.__tablename__ == "memory_versions"
    cols = {c.name for c in MemoryVersion.__table__.columns}
    assert cols == {"id", "memory_id", "version", "title", "content", "metadata", "source", "changed_at"}


def test_memory_version_fk_cascade():
    fks = list(MemoryVersion.__table__.foreign_keys)
    assert len(fks) == 1
    assert fks[0].column.table.name == "memories"
    assert fks[0].ondelete == "CASCADE"
