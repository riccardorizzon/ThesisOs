"""Workflow runtime — State→Planner→Scheduler→Executor→Validator→StateUpdate."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from builder_engine.checks import run_packet_checks
from builder_engine.executor import build_dispatch_entry
from builder_engine.graph import BuilderGraph
from builder_engine.planner import next_wave_from_raw, plan_ready, wave_complete_raw
from builder_engine.scheduler import file_locks_for_packet, in_flight_packets
from builder_engine.state_io import load_raw_state, save_raw_state
from builder_engine.state_machine import (
    execution_from_yaml_status,
    transition,
    yaml_status_from_execution,
)
from builder_engine.validate import validate_graph


class WorkflowRuntimeError(Exception):
    """Runtime orchestration failure."""


@dataclass
class ScheduleResult:
    manifest_path: Path
    entries: list[dict[str, Any]]
    packet_ids: list[str]


@dataclass
class SyncResult:
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    advanced_to_wave: int | None = None


class WorkflowRuntime:
    """Deterministic build workflow engine core (ADR-0025)."""

    def __init__(self, repo_root: Path, state_path: Path | None = None):
        self.repo_root = repo_root.resolve()
        self.state_path = (state_path or self.repo_root / "plans" / "builder" / "STATE.yaml").resolve()
        self.engine_dir = self.repo_root / ".builder-engine"

    def load_graph(self) -> BuilderGraph:
        return BuilderGraph.load(self.state_path)

    def _require_valid_graph(self, graph: BuilderGraph) -> None:
        result = validate_graph(graph)
        if not result.ok:
            raise WorkflowRuntimeError(f"graph invalid: {'; '.join(result.errors)}")

    def _load_raw(self) -> dict[str, Any]:
        return load_raw_state(self.state_path)

    def schedule(self, *, packet_ids: list[str] | None = None) -> ScheduleResult:
        """Claim ready packets, set locks, emit dispatch manifest (no worktrees)."""
        graph = self.load_graph()
        self._require_valid_graph(graph)

        ready = plan_ready(graph)
        if packet_ids:
            allowed = set(packet_ids)
            ready = [p for p in ready if p.id in allowed]
        if not ready:
            raise WorkflowRuntimeError("no ready packets to schedule")

        in_flight = in_flight_packets(graph)
        if in_flight:
            ids = ", ".join(p.id for p in in_flight)
            raise WorkflowRuntimeError(f"packets already in progress: {ids}")

        raw = self._load_raw()
        locks: dict[str, str] = dict(raw.get("file_locks") or {})
        entries: list[dict[str, Any]] = []
        scheduled_ids: list[str] = []

        for packet in ready:
            if packet.agent_type == "implementer" and not packet.checks:
                raise WorkflowRuntimeError(
                    f"{packet.id}: implementer packet requires checks before schedule"
                )

            state = execution_from_yaml_status(packet.status)
            state = transition(state, "claim")
            state = transition(state, "start")

            locks.update(file_locks_for_packet(packet))

            raw["packets"][packet.id]["status"] = yaml_status_from_execution(state)
            scheduled_ids.append(packet.id)

            entry = build_dispatch_entry(graph, packet, self.repo_root)
            entries.append(entry.to_dict())

        raw["file_locks"] = locks
        save_raw_state(self.state_path, raw)

        self.engine_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.engine_dir / "last-dispatch-manifest.json"
        manifest_path.write_text(
            json.dumps({"epic": graph.epic, "wave": graph.wave, "entries": entries}, indent=2),
            encoding="utf-8",
        )
        return ScheduleResult(manifest_path=manifest_path, entries=entries, packet_ids=scheduled_ids)

    def sync(self, *, dry_run: bool = False) -> SyncResult:
        """Validate in-progress packets; mark done or blocked; advance wave."""
        graph = self.load_graph()
        self._require_valid_graph(graph)

        in_progress = [p for p in graph.packets.values() if p.status == "in_progress"]
        if not in_progress:
            raise WorkflowRuntimeError("no in_progress packets to sync")

        raw = self._load_raw()
        result = SyncResult()

        for packet in in_progress:
            exec_state = execution_from_yaml_status(packet.status)
            exec_state = transition(exec_state, "validate")
            check_results = run_packet_checks(packet.checks, self.repo_root) if packet.checks else []

            if packet.checks and not all(r.ok for r in check_results):
                exec_state = transition(exec_state, "fail")
                raw["packets"][packet.id]["status"] = yaml_status_from_execution(exec_state)
                failed_checks = [r.command for r in check_results if not r.ok]
                raw["packets"][packet.id]["integration_notes"] = (
                    f"checks failed: {', '.join(failed_checks)}"
                )
                result.failed.append(packet.id)
                continue

            exec_state = transition(exec_state, "pass")
            exec_state = transition(exec_state, "complete")
            raw["packets"][packet.id]["status"] = yaml_status_from_execution(exec_state)
            result.completed.append(packet.id)

            for path, owner in list(raw.get("file_locks", {}).items()):
                if owner == packet.id:
                    del raw["file_locks"][path]

        if wave_complete_raw(raw):
            nxt = next_wave_from_raw(raw)
            if nxt is not None:
                raw["wave"] = nxt
                result.advanced_to_wave = nxt
            raw["file_locks"] = {}

        if not dry_run:
            save_raw_state(self.state_path, raw)

        return result
