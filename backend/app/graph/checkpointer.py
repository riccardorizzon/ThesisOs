from contextlib import asynccontextmanager
from urllib.parse import quote

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings

LANGGRAPH_SCHEMA = "langgraph"


def _psycopg_conn_string(database_url: str) -> str:
    """Translate the SQLAlchemy DSN to a psycopg DSN and pin search_path to the
    langgraph schema (ADR-0012: tool-owned infra schema, separate from the domain)."""
    dsn = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    sep = "&" if "?" in dsn else "?"
    opts = quote(f"-csearch_path={LANGGRAPH_SCHEMA},public")
    return f"{dsn}{sep}options={opts}"


@asynccontextmanager
async def open_checkpointer():
    """Yield an AsyncPostgresSaver bound to the langgraph schema, tables ensured via setup()."""
    conn_string = _psycopg_conn_string(settings.database_url)
    async with AsyncPostgresSaver.from_conn_string(conn_string) as saver:
        yield saver


async def ensure_langgraph_schema() -> None:
    """Create the langgraph schema then run PostgresSaver.setup() (idempotent)."""
    from sqlalchemy import text
    from app.db.session_async import async_engine

    async with async_engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {LANGGRAPH_SCHEMA}"))
    async with open_checkpointer() as saver:
        await saver.setup()
