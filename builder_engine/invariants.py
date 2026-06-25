"""L1 Class B invariant enforcement before Workflow state commits."""

from __future__ import annotations

from pathlib import Path

from builder_engine.graph import BuilderGraph
from builder_engine.validate import validate_graph


class InvariantViolation(Exception):
    """Fail-closed invariant breach (L1 §4)."""


def graph_from_state_dict(data: dict, path: Path) -> BuilderGraph:
    """Build BuilderGraph from in-memory STATE dict (pre-commit candidate)."""
    packets_raw = data.get("packets") or {}
    from builder_engine.graph import Packet

    packets = {pid: Packet.from_mapping(pid, pkt) for pid, pkt in packets_raw.items()}
    return BuilderGraph(
        path=path,
        epic=str(data.get("epic") or ""),
        chain=data.get("chain"),
        status=str(data.get("status") or "active"),
        wave=int(data.get("wave") or 1),
        decisions=list(data.get("decisions") or []),
        file_locks=dict(data.get("file_locks") or {}),
        blockers=dict(data.get("blockers") or {}),
        packets=packets,
    )


def check_invariants(graph: BuilderGraph) -> None:
    """Run Class B invariant pass; raise InvariantViolation on any error."""
    result = validate_graph(graph)
    if not result.ok:
        raise InvariantViolation("; ".join(result.errors))


def check_raw_state(data: dict, path: Path) -> None:
    """INV-B* pass on candidate STATE before atomic commit (INV-B8 hook)."""
    check_invariants(graph_from_state_dict(data, path))
