"""MB2-Q5 — Projection qualification tests (normative test IDs).

SoR §13.2 MB2-Q5: rebuild deterministic; CLI read-only; MB2-Q-013…015.
Evidence on EWO-006 — no new implementation.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from builder_engine.events import BuildEvent
from builder_engine.projection import (
    ProjectionBuilder,
    ProjectionDocument,
    read_projection,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
EVENT_SEQUENCE = FIXTURES / "projection_event_sequence.jsonl"
SCHEMA_FIXTURE = FIXTURES / "projection_schema_v1.yaml"
PROJECTION_SOURCE = Path(__file__).resolve().parents[1] / "projection.py"
CLI_SOURCE = Path(__file__).resolve().parents[1] / "cli.py"

REQUIRED_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "program_id",
        "derived_at",
        "cycle_id",
        "supervisor",
        "waves",
        "integrations",
        "jobs",
        "queue",
        "qwo",
        "gates",
    }
)


def _load_fixture_events() -> list[BuildEvent]:
    lines = EVENT_SEQUENCE.read_text(encoding="utf-8").splitlines()
    return [BuildEvent.from_line(line) for line in lines if line.strip()]


def _content_hash_excluding_derived_at(builder: ProjectionBuilder) -> str:
    payload = builder.document.to_dict()
    payload["derived_at"] = ""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    import hashlib

    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def test_mb2_q_013_projection_rebuild_equals_original():
    """INV-R-11: same event log → same projection content (REQ-11)."""
    events = _load_fixture_events()
    first = ProjectionBuilder().rebuild(events)
    second = ProjectionBuilder().rebuild(events)

    assert first.to_dict() == second.to_dict()

    builder_a = ProjectionBuilder()
    builder_b = ProjectionBuilder()
    builder_a.rebuild(events)
    builder_b.rebuild(events)
    assert _content_hash_excluding_derived_at(builder_a) == _content_hash_excluding_derived_at(
        builder_b
    )

    golden = read_projection(SCHEMA_FIXTURE)
    rebuilt = ProjectionBuilder().rebuild(events)
    assert rebuilt.to_dict() == golden.to_dict()


def test_mb2_q_014_cli_does_not_compute_ready_set():
    """INV-R-12: projection path has no scheduler ready-set logic (REQ-20)."""
    projection_tree = ast.parse(PROJECTION_SOURCE.read_text(encoding="utf-8"))
    projection_imports: list[str] = []
    for node in ast.walk(projection_tree):
        if isinstance(node, ast.Import):
            projection_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            projection_imports.append(node.module)

    joined = " ".join(projection_imports)
    assert "builder_engine.scheduler" not in joined
    assert "compute_ready" not in joined

    cli_tree = ast.parse(CLI_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(cli_tree):
        if isinstance(node, ast.ImportFrom) and node.module == "builder_engine.projection":
            pytest.fail("cli.py must not import projection with scheduler coupling")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "compute_ready":
                for parent in ast.walk(cli_tree):
                    if isinstance(parent, ast.ImportFrom) and parent.module == "builder_engine.projection":
                        pytest.fail("compute_ready must not be used on projection path")


def test_mb2_q_015_schema_v1_valid():
    """§9.1: ProjectionDocument schema v1 all required keys present."""
    doc = ProjectionDocument()
    data = doc.to_dict()
    assert REQUIRED_TOP_LEVEL_KEYS <= set(data.keys())
    assert data["schema_version"] == 1
    assert isinstance(data["supervisor"], dict)
    assert isinstance(data["queue"], dict)
    assert set(data["queue"]) == {"pending", "in_flight", "failed"}
    assert set(data["gates"]) == {"ci", "coverage"}

    golden = read_projection(SCHEMA_FIXTURE)
    assert golden.schema_version == 1
    assert REQUIRED_TOP_LEVEL_KEYS <= set(golden.to_dict().keys())
