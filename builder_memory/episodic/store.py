"""Append-only SQLite episodic store for builder session artifacts."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from builder_memory.episodic.policy import validate_entry_type
from builder_memory.paths import episodic_db_path


@dataclass(frozen=True)
class EpisodicEntry:
    id: int
    entry_type: str
    summary: str
    source_refs: list[str]
    packet_id: str | None
    created_at: str


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _init(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS episodic_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            source_refs TEXT NOT NULL DEFAULT '[]',
            packet_id TEXT,
            created_at TEXT NOT NULL
        )
        """
    )


class EpisodicStore:
    def __init__(self, repo_root: Path) -> None:
        self.db_path = episodic_db_path(repo_root)

    def append(
        self,
        *,
        entry_type: str,
        summary: str,
        source_refs: list[str] | None = None,
        packet_id: str | None = None,
    ) -> EpisodicEntry:
        validate_entry_type(entry_type)
        refs = source_refs or []
        if entry_type == "lesson_learned" and not refs:
            raise ValueError("lesson_learned entries require source_refs")

        conn = _connect(self.db_path)
        try:
            _init(conn)
            created = datetime.now(UTC).isoformat()
            cur = conn.execute(
                """
                INSERT INTO episodic_entries (entry_type, summary, source_refs, packet_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (entry_type, summary, json.dumps(refs), packet_id, created),
            )
            conn.commit()
            return EpisodicEntry(
                id=int(cur.lastrowid),
                entry_type=entry_type,
                summary=summary,
                source_refs=refs,
                packet_id=packet_id,
                created_at=created,
            )
        finally:
            conn.close()

    def recent(self, *, limit: int = 10) -> list[EpisodicEntry]:
        if not self.db_path.is_file():
            return []
        conn = _connect(self.db_path)
        try:
            _init(conn)
            rows = conn.execute(
                """
                SELECT id, entry_type, summary, source_refs, packet_id, created_at
                FROM episodic_entries
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                EpisodicEntry(
                    id=r["id"],
                    entry_type=r["entry_type"],
                    summary=r["summary"],
                    source_refs=json.loads(r["source_refs"]),
                    packet_id=r["packet_id"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]
        finally:
            conn.close()
