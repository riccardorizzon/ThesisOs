"""Observe State — immutable read model for one engineering cycle (MB2 D1)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from builder_engine.graph import BuilderGraph, Packet
from builder_engine.paths import default_state_path
from builder_engine.scheduler import compute_ready, in_flight_packets
from builder_engine.validate import validate_graph


@dataclass(frozen=True)
class GitObservation:
    is_repo: bool
    branch: str | None = None
    dirty: bool | None = None
    uncommitted_count: int | None = None


@dataclass(frozen=True)
class PacketSummary:
    id: str
    wave: int
    status: str
    agent_type: str
    depends_on: tuple[str, ...]
    checks: tuple[str, ...] = ()


@dataclass(frozen=True)
class ObservedSnapshot:
    """Immutable derived read model for one Observe cycle (L3 §3.1, MB2 D1)."""

    observed_at: str
    state_path: str
    epic: str
    chain: str | None
    epic_status: str
    wave: int
    packet_count: int
    ready_count: int
    in_flight_count: int
    done_count: int
    blocked_count: int
    decisions_count: int
    file_locks: tuple[tuple[str, str], ...]
    blockers: tuple[tuple[str, str], ...]
    packets: tuple[PacketSummary, ...]
    git: GitObservation
    validation_ok: bool
    validation_errors: tuple[str, ...]
    validation_warnings: tuple[str, ...]
    staleness_reasons: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.staleness_reasons


def _observe_git(repo_root: Path) -> GitObservation:
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=repo_root,
            capture_output=True,
            check=True,
            timeout=5,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return GitObservation(is_repo=False)

    branch: str | None = None
    dirty: bool | None = None
    uncommitted_count: int | None = None

    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        branch = None

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout
        lines = [ln for ln in status.splitlines() if ln.strip()]
        uncommitted_count = len(lines)
        dirty = uncommitted_count > 0
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        dirty = None
        uncommitted_count = None

    return GitObservation(
        is_repo=True,
        branch=branch,
        dirty=dirty,
        uncommitted_count=uncommitted_count,
    )


def _packet_summary(pkt: Packet) -> PacketSummary:
    return PacketSummary(
        id=pkt.id,
        wave=pkt.wave,
        status=pkt.status,
        agent_type=pkt.agent_type,
        depends_on=pkt.depends_on,
        checks=pkt.checks,
    )


def _build_snapshot(
    graph: BuilderGraph,
    *,
    git: GitObservation,
    validation_ok: bool,
    validation_errors: tuple[str, ...],
    validation_warnings: tuple[str, ...],
    load_errors: tuple[str, ...] = (),
) -> ObservedSnapshot:
    ready = compute_ready(graph)
    in_flight = in_flight_packets(graph)
    statuses = [p.status for p in graph.packets.values()]

    staleness: list[str] = list(load_errors)
    if not validation_ok:
        staleness.append("graph validation failed")
        staleness.extend(validation_errors)
    if graph.blockers:
        staleness.append(f"{len(graph.blockers)} open blocker(s) in STATE")

    return ObservedSnapshot(
        observed_at=datetime.now(UTC).isoformat(),
        state_path=str(graph.path),
        epic=graph.epic,
        chain=graph.chain,
        epic_status=graph.status,
        wave=graph.wave,
        packet_count=len(graph.packets),
        ready_count=len(ready),
        in_flight_count=len(in_flight),
        done_count=sum(1 for s in statuses if s == "done"),
        blocked_count=sum(1 for s in statuses if s == "blocked"),
        decisions_count=len(graph.decisions),
        file_locks=tuple(sorted(graph.file_locks.items())),
        blockers=tuple(sorted(graph.blockers.items())),
        packets=tuple(_packet_summary(p) for p in sorted(graph.packets.values(), key=lambda x: x.id)),
        git=git,
        validation_ok=validation_ok,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings,
        staleness_reasons=tuple(staleness),
    )


class StateObserver:
    """Read-only aggregator for Observe State (runtime-model §3.1)."""

    def __init__(
        self,
        repo_root: Path,
        state_path: Path | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.state_path = (state_path or default_state_path(self.repo_root)).resolve()

    def observe(self) -> ObservedSnapshot:
        git = _observe_git(self.repo_root)

        if not self.state_path.is_file():
            return ObservedSnapshot(
                observed_at=datetime.now(UTC).isoformat(),
                state_path=str(self.state_path),
                epic="",
                chain=None,
                epic_status="",
                wave=0,
                packet_count=0,
                ready_count=0,
                in_flight_count=0,
                done_count=0,
                blocked_count=0,
                decisions_count=0,
                file_locks=(),
                blockers=(),
                packets=(),
                git=git,
                validation_ok=False,
                validation_errors=("STATE file not found",),
                validation_warnings=(),
                staleness_reasons=(f"STATE file not found: {self.state_path}",),
            )

        try:
            graph = BuilderGraph.load(self.state_path)
        except Exception as exc:
            return ObservedSnapshot(
                observed_at=datetime.now(UTC).isoformat(),
                state_path=str(self.state_path),
                epic="",
                chain=None,
                epic_status="",
                wave=0,
                packet_count=0,
                ready_count=0,
                in_flight_count=0,
                done_count=0,
                blocked_count=0,
                decisions_count=0,
                file_locks=(),
                blockers=(),
                packets=(),
                git=git,
                validation_ok=False,
                validation_errors=(f"failed to parse STATE: {exc}",),
                validation_warnings=(),
                staleness_reasons=(f"failed to parse STATE: {exc}",),
            )

        result = validate_graph(graph)
        return _build_snapshot(
            graph,
            git=git,
            validation_ok=result.ok,
            validation_errors=tuple(result.errors),
            validation_warnings=tuple(result.warnings),
        )
