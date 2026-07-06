from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

import app.db.models  # noqa: F401
import app.models.knowledge  # noqa: F401  (PX-4 concept domain)
from app.db.base import Base

SCHEMA = Path(__file__).resolve().parents[2] / "contracts" / "db" / "schema.sql"


def _render() -> str:
    ddl = ["CREATE EXTENSION IF NOT EXISTS vector;\n"]
    for t in Base.metadata.sorted_tables:
        ddl.append(str(CreateTable(t).compile(dialect=postgresql.dialect())).strip() + ";\n")
    return "\n".join(ddl)


def test_schema_snapshot_matches_models():
    assert SCHEMA.read_text() == _render(), (
        "contracts/db/schema.sql is stale vs app/db/models.py — regenerate it."
    )
