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
os.environ.setdefault("THESISOS_DEV_CATALOG", "1")

import pytest
from sqlalchemy import text


def _run_ensure_test_db() -> None:
    script = _ROOT / "bin" / "ensure-test-db.sh"
    subprocess.run([str(script)], check=False, cwd=_ROOT)


# Session-scoped advisory lock: two pytest processes sharing thesisos_test would
# truncate each other's rows mid-test (silent cross-process corruption). Fail fast
# instead of producing flaky, misleading failures.
_TEST_DB_LOCK_KEY = 72720529


def _try_acquire_test_db_lock():
    """Hold a Postgres advisory lock for the whole pytest session; None if DB down."""
    try:
        import psycopg

        dsn = os.environ["DATABASE_URL"].replace("+psycopg", "")
        conn = psycopg.connect(dsn, autocommit=True)
    except Exception:
        return None  # DB unreachable — db_session will skip
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s)", (_TEST_DB_LOCK_KEY,))
        acquired = cur.fetchone()[0]
    if not acquired:
        conn.close()
        pytest.exit(
            "another pytest run is using thesisos_test — re-run when it finishes",
            returncode=3,
        )
    return conn


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
    lock_conn = _try_acquire_test_db_lock()
    yield
    if lock_conn is not None:
        try:
            with lock_conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s)", (_TEST_DB_LOCK_KEY,))
            lock_conn.close()
        except Exception:
            pass


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
