def test_all_tables_registered():
    from app.db.base import Base
    import app.db.models  # noqa: F401
    names = set(Base.metadata.tables.keys())
    expected = {
        "documents","document_versions","chunks","embeddings","sources","citations","chapters",
        "notes","memories","memory_versions","conversations","messages","tasks","events",
        "agent_runs","agent_steps",
    }
    assert expected.issubset(names), expected - names
