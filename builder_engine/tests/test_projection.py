from __future__ import annotations

import ast
from pathlib import Path

import pytest

from builder_engine.events import BuildEvent, BuildEventBus, event_now
from builder_engine.projection import (
    ProjectionBuilder,
    ProjectionDocument,
    default_projection_path,
    load_projection,
    read_projection,
    write_projection,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
EVENT_SEQUENCE = FIXTURES / "projection_event_sequence.jsonl"
SCHEMA_FIXTURE = FIXTURES / "projection_schema_v1.yaml"

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


def test_schema_v1_required_keys():
    doc = ProjectionDocument()
    data = doc.to_dict()
    assert REQUIRED_TOP_LEVEL_KEYS <= set(data.keys())
    assert data["schema_version"] == 1
    assert data["supervisor"]["state"] == "unknown"
    assert data["gates"]["ci"] == "unknown"
    assert data["gates"]["coverage"] == "unknown"


def test_rebuild_deterministic():
    events = _load_fixture_events()
    first = ProjectionBuilder().rebuild(events)
    second = ProjectionBuilder().rebuild(events)
    builder_a = ProjectionBuilder()
    builder_b = ProjectionBuilder()
    builder_a.rebuild(events)
    builder_b.rebuild(events)
    assert builder_a.content_hash() == builder_b.content_hash()
    assert first.to_dict() == second.to_dict()


def test_job_ready_updates_projection():
    builder = ProjectionBuilder()
    builder.apply(
        event_now(
            "JobReady",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "state": "ready",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
            cycle_id="cycle-1",
        )
    )
    doc = builder.document
    assert doc.jobs["job-1"]["status"] == "ready"
    assert doc.jobs["job-1"]["ewo_id"] == "EWO-001"
    assert doc.queue["pending"] == 1
    assert doc.queue["in_flight"] == 0
    assert doc.waves["wave-a"]["status"] == "ready"


def test_job_claimed_updates_projection():
    builder = ProjectionBuilder()
    builder.apply(
        event_now(
            "JobReady",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "state": "ready",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
        )
    )
    builder.apply(
        event_now(
            "JobClaimed",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "state": "claimed",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
        )
    )
    doc = builder.document
    assert doc.jobs["job-1"]["status"] == "running"
    assert doc.queue["pending"] == 0
    assert doc.queue["in_flight"] == 1
    assert doc.waves["wave-a"]["status"] == "running"


def test_execution_graph_derived_metadata():
    builder = ProjectionBuilder()
    builder.apply(
        event_now(
            "ExecutionGraphDerived",
            {
                "program_id": "px-exec",
                "graph_hash": "abc123def456",
                "ready_count": 1,
                "node_ids": ["EWO-001", "EWO-002"],
            },
            program_id="px-exec",
            cycle_id="cycle-1",
        )
    )
    assert builder.graph_hash == "abc123def456"
    doc = builder.document
    assert doc.program_id == "px-exec"
    assert doc.jobs["EWO-001"]["status"] == "waiting"
    assert doc.jobs["EWO-002"]["status"] == "waiting"


def test_projection_updated_emitted(tmp_path: Path):
    bus = BuildEventBus(tmp_path)
    seen: list[str] = []
    bus.subscribe(lambda event: seen.append(event.type))
    builder = ProjectionBuilder(repo_root=tmp_path, bus=bus)
    builder.rebuild(_load_fixture_events())
    assert "ProjectionUpdated" in seen
    emitted = next(event for event in bus.replay() if event.type == "ProjectionUpdated")
    assert emitted.payload["content_hash"]
    assert emitted.payload["path"].endswith("projection.yaml")


def test_no_scheduler_import():
    source = Path(__file__).resolve().parents[1] / "projection.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    assert "builder_engine.scheduler" not in imported_modules
    assert "scheduler" not in imported_modules
    joined = " ".join(imported_modules)
    assert "compute_ready" not in joined


def test_persistence_round_trip(tmp_path: Path):
    events = _load_fixture_events()
    builder = ProjectionBuilder(repo_root=tmp_path)
    original = builder.rebuild(events)
    path = default_projection_path(tmp_path)
    assert path.is_file()
    restored = read_projection(path)
    assert restored.to_dict() == original.to_dict()
    assert load_projection(tmp_path) == restored


def test_era_events_noop_stable():
    events = [
        event_now("CycleStarted", {"wave": 1}, program_id="px-exec", cycle_id="cycle-era"),
        event_now("StateObserved", {"packets": 0}, program_id="px-exec", cycle_id="cycle-era"),
        event_now(
            "JobReady",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "state": "ready",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
            cycle_id="cycle-era",
        ),
    ]
    with_cycle = ProjectionBuilder().rebuild(events)
    without_cycle = ProjectionBuilder().rebuild(events[2:])
    assert with_cycle.jobs == without_cycle.jobs
    assert with_cycle.queue == without_cycle.queue


def test_projection_updated_ignored_on_input():
    builder = ProjectionBuilder()
    builder.apply(event_now("JobReady", {"job_id": "j1", "ewo_id": "EWO-001", "state": "ready"}))
    before = builder.document.to_dict()
    builder.apply(
        event_now(
            "ProjectionUpdated",
            {"path": "projection.yaml", "content_hash": "deadbeef"},
            program_id="px-exec",
        )
    )
    after = builder.document.to_dict()
    assert after["jobs"] == before["jobs"]
    assert after["queue"] == before["queue"]


def test_runtime_escalated_updates_supervisor_and_job():
    builder = ProjectionBuilder()
    builder.apply(
        event_now(
            "JobReady",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "state": "ready",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
        )
    )
    builder.apply(
        event_now(
            "RuntimeEscalated",
            {
                "job_id": "job-1",
                "ewo_id": "EWO-001",
                "reason": "illegal transition",
            },
            program_id="px-exec",
        )
    )
    doc = builder.document
    assert doc.supervisor["state"] == "WAIT"
    assert doc.supervisor["reason"] == "illegal transition"
    assert doc.jobs["job-1"]["status"] == "fail"
    assert doc.queue["failed"] == 1


def test_ewo_completed_marks_pass():
    builder = ProjectionBuilder()
    builder.apply(
        event_now(
            "JobClaimed",
            {
                "job_id": "EWO-001",
                "ewo_id": "EWO-001",
                "state": "claimed",
                "wave_id": "wave-a",
            },
            program_id="px-exec",
        )
    )
    builder.apply(
        event_now(
            "EwoCompleted",
            {"ewo_id": "EWO-001", "job_id": "EWO-001"},
            program_id="px-exec",
        )
    )
    doc = builder.document
    assert doc.jobs["EWO-001"]["status"] == "pass"
    assert doc.waves["wave-a"]["status"] == "pass"
    assert doc.queue["in_flight"] == 0


def test_schema_fixture_matches_rebuild():
    events = _load_fixture_events()
    doc = ProjectionBuilder().rebuild(events)
    expected = read_projection(SCHEMA_FIXTURE)
    assert doc.to_dict() == expected.to_dict()


def test_write_projection_direct(tmp_path: Path):
    doc = ProjectionDocument(
        program_id="px-exec",
        derived_at="2026-07-06T10:00:00+00:00",
        cycle_id="cycle-1",
    )
    path = tmp_path / "projection.yaml"
    write_projection(path, doc)
    restored = read_projection(path)
    assert restored.program_id == "px-exec"
    assert restored.cycle_id == "cycle-1"
