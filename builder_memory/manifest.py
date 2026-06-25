"""Index manifest read/write."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class Manifest:
    commit_sha: str
    indexed_at: str
    file_count: int
    chunk_count: int
    bm25_only: bool = True

    @classmethod
    def now(cls, *, commit_sha: str, file_count: int, chunk_count: int) -> Manifest:
        return cls(
            commit_sha=commit_sha,
            indexed_at=datetime.now(UTC).isoformat(),
            file_count=file_count,
            chunk_count=chunk_count,
            bm25_only=True,
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> Manifest | None:
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def is_stale(self, current_commit: str) -> bool:
        return self.commit_sha != current_commit
