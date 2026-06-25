"""Repository root resolution."""

from __future__ import annotations

import os
from pathlib import Path

MARKERS = ("knowledge", "contracts", "decisions", "plans")


def find_repo_root(start: Path | None = None) -> Path:
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


def default_state_path(repo_root: Path) -> Path:
    return repo_root / "plans" / "builder" / "STATE.yaml"
