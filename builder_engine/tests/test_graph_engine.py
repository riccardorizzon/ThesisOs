from __future__ import annotations

from pathlib import Path

import pytest

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.scheduler import compute_ready
from builder_engine.validate import validate_graph


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_load_state_example():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    assert graph.epic == "m1-conversation-system"
    assert len(graph.packets) == 7


def test_validate_state_example_passes():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    result = validate_graph(graph)
    assert result.ok, result.errors


def test_ready_wave1_example():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.example.yaml")
    ready = compute_ready(graph)
    assert {p.id for p in ready} == {"P1", "P2", "P3"}


def test_validate_current_state_closed_epic():
    graph = BuilderGraph.load(_repo_root() / "plans" / "builder" / "STATE.yaml")
    result = validate_graph(graph)
    assert result.ok, result.errors


def test_owned_files_overlap_within_wave():
    graph = BuilderGraph(
        path=Path("STATE.yaml"),
        epic="test",
        chain=None,
        status="active",
        wave=1,
        packets={
            "A": Packet(
                id="A",
                wave=1,
                agent_type="implementer",
                status="ready",
                depends_on=(),
                owned_files=("backend/app/",),
            ),
            "B": Packet(
                id="B",
                wave=1,
                agent_type="implementer",
                status="ready",
                depends_on=(),
                owned_files=("backend/app/services/",),
            ),
        },
    )
    result = validate_graph(graph)
    assert not result.ok
    assert any("owned_files overlap" in e for e in result.errors)


def test_lock_must_be_subset_of_owned():
    graph = BuilderGraph(
        path=Path("STATE.yaml"),
        epic="test",
        chain=None,
        status="active",
        wave=1,
        file_locks={"frontend/lib/": "A"},
        packets={
            "A": Packet(
                id="A",
                wave=1,
                agent_type="implementer",
                status="in_progress",
                depends_on=(),
                owned_files=("backend/app/",),
            ),
        },
    )
    result = validate_graph(graph)
    assert not result.ok
    assert any("outside owned_files" in e for e in result.errors)


def test_wave_coherence_warns_stale_ready_packet():
    graph = BuilderGraph(
        path=Path("STATE.yaml"),
        epic="test",
        chain=None,
        status="active",
        wave=2,
        packets={
            "P": Packet(
                id="P",
                wave=1,
                agent_type="implementer",
                status="ready",
                depends_on=(),
                owned_files=("backend/",),
            ),
        },
    )
    result = validate_graph(graph)
    assert result.ok
    assert any("still ready at wave 1" in w for w in result.warnings)


def test_wave_coherence_blocks_in_progress_wrong_wave():
    graph = BuilderGraph(
        path=Path("STATE.yaml"),
        epic="test",
        chain=None,
        status="active",
        wave=2,
        decisions=["x"],
        packets={
            "P": Packet(
                id="P",
                wave=1,
                agent_type="implementer",
                status="in_progress",
                depends_on=(),
                owned_files=("backend/",),
            ),
        },
    )
    result = validate_graph(graph)
    assert not result.ok
    assert any("in_progress at wave 1" in e for e in result.errors)
