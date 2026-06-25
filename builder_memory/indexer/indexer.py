"""Corpus indexer — walks allowlist, chunks, stores in SQLite FTS5."""

from __future__ import annotations

import hashlib
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path

from builder_memory.config import kind_for_path, should_index
from builder_memory.indexer.chunking import chunk_file
from builder_memory.manifest import Manifest
from builder_memory.paths import index_db_path, manifest_path


@dataclass(frozen=True)
class IndexStats:
    file_count: int
    chunk_count: int
    commit_sha: str
    skipped: int


def git_head(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            sha256 TEXT NOT NULL,
            mtime_ns INTEGER NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            content,
            source_path UNINDEXED,
            kind UNINDEXED,
            title UNINDEXED,
            heading_path UNINDEXED,
            chunk_id UNINDEXED,
            tokenize='porter unicode61'
        );
        """
    )


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunk_id(source_path: str, heading_path: str, offset: int) -> str:
    raw = f"{source_path}:{heading_path}:{offset}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _iter_corpus_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if should_index(rel):
            files.append(path)
    return files


def _remove_file_chunks(conn: sqlite3.Connection, rel_path: str) -> None:
    conn.execute(
        "DELETE FROM chunks_fts WHERE source_path = ?",
        (rel_path,),
    )


def _index_file(conn: sqlite3.Connection, repo_root: Path, file_path: Path) -> int:
    rel = file_path.relative_to(repo_root).as_posix()
    text = file_path.read_text(encoding="utf-8", errors="replace")
    kind = kind_for_path(rel)
    drafts = chunk_file(rel, text)
    _remove_file_chunks(conn, rel)
    count = 0
    for offset, draft in enumerate(drafts):
        cid = _chunk_id(rel, draft.heading_path, offset)
        conn.execute(
            """
            INSERT INTO chunks_fts (content, source_path, kind, title, heading_path, chunk_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (draft.content, rel, kind, draft.title, draft.heading_path, cid),
        )
        count += 1
    stat = file_path.stat()
    conn.execute(
        """
        INSERT INTO files (path, sha256, mtime_ns) VALUES (?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET sha256=excluded.sha256, mtime_ns=excluded.mtime_ns
        """,
        (rel, _file_hash(file_path), stat.st_mtime_ns),
    )
    return count


class CorpusIndexer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.db_path = index_db_path(repo_root)

    def index(self, *, incremental: bool = False) -> IndexStats:
        conn = _connect(self.db_path)
        try:
            _init_schema(conn)
            commit_sha = git_head(self.repo_root)
            total_chunks = 0
            indexed_files = 0
            skipped = 0

            for file_path in _iter_corpus_files(self.repo_root):
                rel = file_path.relative_to(self.repo_root).as_posix()
                stat = file_path.stat()
                sha = _file_hash(file_path)

                if incremental:
                    row = conn.execute(
                        "SELECT sha256, mtime_ns FROM files WHERE path = ?",
                        (rel,),
                    ).fetchone()
                    if row and row["sha256"] == sha and row["mtime_ns"] == stat.st_mtime_ns:
                        skipped += 1
                        continue

                total_chunks += _index_file(conn, self.repo_root, file_path)
                indexed_files += 1

            conn.commit()
            chunk_total = self._count_chunks(conn)
            manifest = Manifest.now(
                commit_sha=commit_sha,
                file_count=len(_iter_corpus_files(self.repo_root)),
                chunk_count=chunk_total,
            )
            manifest.save(manifest_path(self.repo_root))
            return IndexStats(
                file_count=manifest.file_count,
                chunk_count=manifest.chunk_count,
                commit_sha=commit_sha,
                skipped=skipped,
            )
        finally:
            conn.close()

    @staticmethod
    def _count_chunks(conn: sqlite3.Connection) -> int:
        row = conn.execute("SELECT COUNT(*) AS c FROM chunks_fts").fetchone()
        return int(row["c"]) if row else 0
