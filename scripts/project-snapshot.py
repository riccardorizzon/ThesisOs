#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.services.project_snapshot import snapshot_project


def _database_url(explicit: str | None) -> str:
    value = explicit or os.environ.get("DATABASE_URL")
    if not value:
        raise SystemExit("DATABASE_URL or --database-url is required")
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


async def _run(args: argparse.Namespace) -> None:
    engine = create_async_engine(_database_url(args.database_url))
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as session:
            snapshot = await snapshot_project(session, args.project_id)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(f"{output.suffix}.tmp")
        temporary.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a deterministic snapshot of one ThesisOS project."
    )
    parser.add_argument("--database-url")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", required=True)
    asyncio.run(_run(parser.parse_args()))


if __name__ == "__main__":
    main()
