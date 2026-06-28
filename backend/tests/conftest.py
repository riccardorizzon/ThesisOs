"""Shared pytest configuration — isolated test database, no dev DB pollution."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_ROOT = _BACKEND.parent
_DEFAULT_TEST_DB = "postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos_test"

# Bind Settings + async engine to the test DB before any app import.
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", _DEFAULT_TEST_DB)
os.environ.setdefault("THESISOS_DISABLE_CONSOLE_TRACE", "1")

import pytest
from sqlalchemy import text


def _run_ensure_test_db() -> None:
    script = _ROOT / "bin" / "ensure-test-db.sh"
    subprocess.run([str(script)], check=False, cwd=_ROOT)


async def _truncate_public_tables(session) -> None:
    await session.execute(text("SET session_replication_role = 'replica'"))
    result = await session.execute(
        text(
            """
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename <> 'alembic_version'
            """
        )
    )
    for (table,) in result:
        await session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
    await session.execute(text("SET session_replication_role = 'origin'"))


@pytest.fixture(scope="session")
def _test_db_ready():
    _run_ensure_test_db()
    yield


@pytest.fixture
async def db_session(_test_db_ready):
    from app.db.session_async import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as probe:
            await probe.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"async DB not reachable: {exc}")

    async with AsyncSessionLocal() as session:
        await _truncate_public_tables(session)
        await session.commit()
        yield session
        await session.rollback()


@pytest.fixture
async def db_available(db_session):
    """Alias for migration/schema tests that only need a reachable, migrated DB."""
    return True
