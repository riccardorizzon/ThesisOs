"""Repository root resolution and storage paths."""

from __future__ import annotations

import os
from pathlib import Path

MARKERS = ("knowledge", "contracts", "decisions", "plans")


def find_repo_root(start: Path | None = None) -> Path:
    """Walk parents until a ThesisOS repo root is found."""
    if env := os.environ.get("THESISOS_ROOT"):
        root = Path(env).resolve()
        if (root / "knowledge").is_dir():
            return root
        raise FileNotFoundError(f"THESISOS_ROOT={env} is not a ThesisOS repository")

    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if all((candidate / m).exists() for m in MARKERS[:2]):
            return candidate
    raise FileNotFoundError(
        "Could not locate ThesisOS repo root (set THESISOS_ROOT or run from the repository)"
    )


def storage_dir(repo_root: Path) -> Path:
    return repo_root / ".builder-memory"


def index_db_path(repo_root: Path) -> Path:
    return storage_dir(repo_root) / "index.sqlite"


def episodic_db_path(repo_root: Path) -> Path:
    return storage_dir(repo_root) / "episodic.sqlite"


def manifest_path(repo_root: Path) -> Path:
    return storage_dir(repo_root) / "manifest.json"


def snapshots_dir(repo_root: Path) -> Path:
    return repo_root / "knowledge" / "snapshots"
