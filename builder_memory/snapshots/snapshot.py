"""Knowledge snapshots at milestone closure — file hashes for change detection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from builder_memory.config import should_index
from builder_memory.indexer.indexer import git_head
from builder_memory.paths import snapshots_dir


@dataclass
class MilestoneSnapshot:
    milestone: str
    commit_sha: str
    created_at: str
    files: dict[str, str]  # rel_path -> sha256

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> MilestoneSnapshot:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _collect_file_hashes(repo_root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if should_index(rel):
            files[rel] = _hash_file(path)
    return files


def diff_since_snapshot(repo_root: Path, snapshot: MilestoneSnapshot) -> list[str]:
    """Return indexed paths whose hash differs from the snapshot (added/changed)."""
    current = _collect_file_hashes(repo_root)
    changed: list[str] = []
    for rel, sha in current.items():
        if snapshot.files.get(rel) != sha:
            changed.append(rel)
    for rel in snapshot.files:
        if rel not in current:
            changed.append(rel)
    return sorted(changed)


class SnapshotStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.dir = snapshots_dir(repo_root)

    def create(self, milestone: str) -> MilestoneSnapshot:
        snap = MilestoneSnapshot(
            milestone=milestone,
            commit_sha=git_head(self.repo_root),
            created_at=datetime.now(UTC).isoformat(),
            files=_collect_file_hashes(self.repo_root),
        )
        snap.save(self.dir / f"{milestone}.json")
        return snap

    def list_snapshots(self) -> list[str]:
        if not self.dir.is_dir():
            return []
        return sorted(p.stem for p in self.dir.glob("*.json"))

    def load(self, milestone: str) -> MilestoneSnapshot | None:
        path = self.dir / f"{milestone}.json"
        if not path.is_file():
            return None
        return MilestoneSnapshot.load(path)

    def latest_snapshot(self) -> MilestoneSnapshot | None:
        names = self.list_snapshots()
        if not names:
            return None
        return self.load(names[-1])
