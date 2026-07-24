#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

DEMO_THESIS_ID = "demo-thesis"


def _database_url(explicit: str | None) -> str:
    value = explicit or os.environ.get("DATABASE_URL")
    if not value:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


async def _reset(database_url: str) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "backend"))

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.services.demo_seed import reset_demo_seed

    engine = create_async_engine(database_url)
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            try:
                await reset_demo_seed(session)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset only the protected ThesisOS demo workspace."
    )
    parser.add_argument("--database-url")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()

    if args.project_id != DEMO_THESIS_ID:
        parser.error("only demo-thesis can be reset")
    if args.confirm != DEMO_THESIS_ID:
        parser.error("confirmation must exactly equal demo-thesis")

    asyncio.run(_reset(_database_url(args.database_url)))


if __name__ == "__main__":
    main()
