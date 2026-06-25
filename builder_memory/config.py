"""Allowlist/denylist and kind tagging for corpus indexing."""

from __future__ import annotations

from pathlib import Path

# Path prefixes relative to repo root that may be indexed.
ALLOWLIST_PREFIXES: tuple[str, ...] = (
    "knowledge/",
    "contracts/",
    "decisions/",
    "plans/",
    "docs/",
)

# Never index implementation trees or artifacts.
DENYLIST_PREFIXES: tuple[str, ...] = (
    "backend/",
    "frontend/",
    "infra/",
    "node_modules/",
    "venv/",
    ".venv/",
    "dist/",
    "coverage/",
    ".builder-memory/",
    ".worktrees/",
    ".git/",
    "builder_memory/tests/fixtures/",
    "knowledge/snapshots/",  # milestone manifests — not corpus (ADR-0019)
)

DENYLIST_GLOBS: tuple[str, ...] = (
    "*.pyc",
    "package-lock.json",
    ".env",
    ".DS_Store",
)


def should_index(rel_path: str) -> bool:
    """Return True if a repo-relative path should enter the corpus index."""
    normalized = rel_path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]

    for prefix in DENYLIST_PREFIXES:
        if normalized.startswith(prefix) or normalized == prefix.rstrip("/"):
            return False

    for pattern in DENYLIST_GLOBS:
        if Path(normalized).match(pattern):
            return False

    for prefix in ALLOWLIST_PREFIXES:
        if normalized.startswith(prefix):
            return True
    return False


def kind_for_path(rel_path: str) -> str:
    """Assign a retrieval kind tag from the file path."""
    p = rel_path.replace("\\", "/")
    if p == "plans/builder/STATE.yaml":
        return "state"
    if p.startswith("decisions/ADR-"):
        return "adr"
    if p.startswith("decisions/"):
        return "decision"
    if p.startswith("contracts/"):
        return "contract"
    if p.startswith("plans/"):
        return "plan"
    if p.startswith("docs/superpowers/specs/"):
        return "spec"
    if p.startswith("docs/m") and "promotion" in p:
        return "promotion"
    if p.startswith("docs/research/"):
        return "research"
    if p.startswith("knowledge/snapshots/"):
        return "snapshot"
    if p.startswith("knowledge/"):
        return "knowledge"
    if p.startswith("docs/"):
        return "doc"
    return "doc"


# Role-based kind weight multipliers for retrieval ranking.
ROLE_KIND_WEIGHTS: dict[str, dict[str, float]] = {
    "architect": {"adr": 2.0, "spec": 2.0, "contract": 2.0, "decision": 1.5},
    "planner": {"plan": 2.0, "spec": 2.0, "state": 2.0, "promotion": 1.5},
    "backend": {"contract": 2.0, "spec": 1.8, "knowledge": 1.5, "adr": 1.5},
    "frontend": {"contract": 2.0, "spec": 1.8, "knowledge": 1.5},
    "qa": {"promotion": 2.0, "plan": 1.8, "knowledge": 1.5},
    "critic": {"adr": 2.0, "contract": 2.0, "promotion": 1.8, "spec": 1.5},
}

# Paths always injected when present (mandatory context).
MANDATORY_PATHS: tuple[str, ...] = (
    "knowledge/context/current-state.md",
    "plans/builder/STATE.yaml",
)
