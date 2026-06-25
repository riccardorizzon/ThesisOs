"""BM25 retrieval over SQLite FTS5."""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from builder_memory.config import MANDATORY_PATHS, kind_for_path
from builder_memory.paths import index_db_path


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source_path: str
    kind: str
    title: str
    heading_path: str
    chunk_id: str
    score: float


def _tokenize_query(query: str) -> str:
    """Build FTS5 MATCH string from natural language query."""
    tokens = re.findall(r"[\w-]+", query.lower())
    if not tokens:
        return ""
    # OR match for broader recall on ADR IDs and contract terms.
    return " OR ".join(tokens)


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


class Retriever:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.db_path = index_db_path(repo_root)

    def is_indexed(self) -> bool:
        return self.db_path.is_file()

    def retrieve(
        self,
        query: str,
        *,
        agent_role: str = "architect",
        limit: int = 12,
    ) -> list[RetrievedChunk]:
        if not self.is_indexed():
            return []

        match = _tokenize_query(query)
        conn = _connect(self.db_path)
        try:
            if match:
                rows = conn.execute(
                    """
                    SELECT content, source_path, kind, title, heading_path, chunk_id,
                           bm25(chunks_fts) AS rank
                    FROM chunks_fts
                    WHERE chunks_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """,
                    (match, limit * 3),
                ).fetchall()
            else:
                rows = []

            results: list[RetrievedChunk] = []
            seen_paths: set[str] = set()
            for row in rows:
                score = float(-row["rank"])
                path = row["source_path"]
                if path in seen_paths:
                    continue
                seen_paths.add(path)
                results.append(
                    RetrievedChunk(
                        content=row["content"],
                        source_path=path,
                        kind=row["kind"],
                        title=row["title"],
                        heading_path=row["heading_path"],
                        chunk_id=row["chunk_id"],
                        score=score,
                    )
                )

            results.sort(key=lambda c: c.score, reverse=True)
            return results[:limit]
        finally:
            conn.close()

    def fetch_by_path(self, rel_path: str) -> list[RetrievedChunk]:
        if not self.is_indexed():
            return []
        conn = _connect(self.db_path)
        try:
            rows = conn.execute(
                """
                SELECT content, source_path, kind, title, heading_path, chunk_id
                FROM chunks_fts
                WHERE source_path = ?
                LIMIT 5
                """,
                (rel_path,),
            ).fetchall()
            return [
                RetrievedChunk(
                    content=r["content"],
                    source_path=r["source_path"],
                    kind=r["kind"],
                    title=r["title"],
                    heading_path=r["heading_path"],
                    chunk_id=r["chunk_id"],
                    score=100.0,
                )
                for r in rows
            ]
        finally:
            conn.close()

    def mandatory_chunks(self) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []
        for rel in MANDATORY_PATHS:
            full = self.repo_root / rel
            if full.is_file():
                indexed = self.fetch_by_path(rel)
                if indexed:
                    chunks.extend(indexed)
                else:
                    text = full.read_text(encoding="utf-8", errors="replace")
                    chunks.append(
                        RetrievedChunk(
                            content=text[:4000],
                            source_path=rel,
                            kind=kind_for_path(rel),
                            title=rel.rsplit("/", 1)[-1],
                            heading_path=rel,
                            chunk_id="filesystem",
                            score=1000.0,
                        )
                    )
        return chunks
