"""Merge eligibility stub and MB2 Merge Plugin (SoR §8.2)."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from builder_engine.dependency import _merge_rank
from builder_engine.events import BuildEventBus, event_now
from builder_engine.program_graph import ProgramGraph
from builder_engine.rules import ActionDescriptor

logger = logging.getLogger(__name__)

MergeOutcome = Literal["deferred", "eligible", "rejected"]
ExecuteOutcome = Literal["completed", "failed", "rejected"]


@dataclass(frozen=True)
class MergeEligibility:
    outcome: MergeOutcome
    reason: str
    packet_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MergeContext:
    job_id: str
    program_id: str
    ewo_id: str
    packet_ids: tuple[str, ...]
    merge_order_index: int
    checkpoint: str | None = None


@dataclass(frozen=True)
class MergeResult:
    outcome: ExecuteOutcome
    reason: str
    merge_id: str | None = None
    manifest_path: str | None = None


@dataclass(frozen=True)
class MergeReport:
    last_outcome: ExecuteOutcome
    reason: str
    merge_id: str | None = None
    completed_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin": "merge",
            "last_outcome": self.last_outcome,
            "reason": self.reason,
            "merge_id": self.merge_id,
            "completed_count": self.completed_count,
        }


def merge_eligibility(
    *,
    validation_passed: bool,
    packet_ids: tuple[str, ...] = (),
) -> MergeEligibility:
    """Always deferred in MB2 — integrator worker performs git merge."""
    if not validation_passed:
        return MergeEligibility(
            outcome="rejected",
            reason="validation failed — merge not eligible",
            packet_ids=packet_ids,
        )
    return MergeEligibility(
        outcome="deferred",
        reason="external integrator required — runtime does not mutate git",
        packet_ids=packet_ids,
    )


class MergePlugin:
    """MB2 Merge Plugin — merge_order enforcement, event emission, external manifest."""

    def __init__(
        self,
        program: ProgramGraph,
        *,
        bus: BuildEventBus | None = None,
        cycle_id: str | None = None,
        completed_merges: set[str] | None = None,
    ) -> None:
        self.program = program
        self.bus = bus
        self.cycle_id = cycle_id
        self._completed: set[str] = set(completed_merges or ())
        self._last_report: MergeReport | None = None

    def eligible(self, job_id: str, *, graph: ProgramGraph | None = None) -> MergeEligibility:
        """Check merge_order (INV-R-03) and dependency readiness."""
        program = graph or self.program
        ewo_id = job_id

        if ewo_id not in program.workorders:
            return MergeEligibility(
                outcome="rejected",
                reason=f"unknown workorder {ewo_id!r}",
            )

        wave_rank, order_idx = _merge_rank(program, ewo_id)
        if wave_rank >= len(program.waves):
            return MergeEligibility(
                outcome="rejected",
                reason=f"{ewo_id} not in any wave merge_order",
            )

        wave = list(program.waves.values())[wave_rank]
        prior_ids = wave.merge_order[:order_idx]
        blocking = [pid for pid in prior_ids if pid not in self._completed]
        if blocking:
            return MergeEligibility(
                outcome="rejected",
                reason=f"merge_order violation — waiting for {blocking!r}",
                packet_ids=(ewo_id,),
            )

        return MergeEligibility(
            outcome="eligible",
            reason="merge_order satisfied — external integrator required",
            packet_ids=(ewo_id,),
        )

    def execute(self, context: MergeContext | dict[str, Any]) -> MergeResult:
        """Emit merge events and produce external-worker manifest (no git mutations)."""
        ctx = _coerce_context(context)
        eligibility = self.eligible(ctx.ewo_id)

        if eligibility.outcome == "rejected":
            result = MergeResult(
                outcome="rejected",
                reason=eligibility.reason,
            )
            self._emit_failed(ctx, result)
            self._record_report(result)
            return result

        merge_id = f"merge-{uuid.uuid4().hex[:12]}"
        manifest_path = self._write_manifest(ctx, merge_id)

        result = MergeResult(
            outcome="completed",
            reason="merge manifest produced for external integrator",
            merge_id=merge_id,
            manifest_path=str(manifest_path) if manifest_path else None,
        )
        self._completed.add(ctx.ewo_id)
        self._emit_completed(ctx, result)
        self._record_report(result)
        return result

    def report(self) -> dict[str, Any]:
        """Return last execution summary per §8.2."""
        if self._last_report is None:
            return {
                "plugin": "merge",
                "last_outcome": "none",
                "reason": "no merge executed yet",
                "completed_count": len(self._completed),
            }
        return self._last_report.to_dict()

    def on_action(
        self,
        descriptor: ActionDescriptor,
        *,
        event_payload: dict[str, Any] | None = None,
    ) -> MergeResult:
        """Rule Engine hook — build context from action descriptor and execute."""
        payload = dict(event_payload or {})
        ewo_id = str(payload.get("ewo_id") or descriptor.params.get("ewo_id") or "")
        if not ewo_id:
            result = MergeResult(
                outcome="failed",
                reason="merge action missing ewo_id in event payload",
            )
            self._emit_failed_raw(ewo_id or "unknown", result)
            self._record_report(result)
            return result

        _, order_idx = _merge_rank(self.program, ewo_id)
        ctx = MergeContext(
            job_id=ewo_id,
            program_id=self.program.program_id,
            ewo_id=ewo_id,
            packet_ids=(ewo_id,),
            merge_order_index=order_idx,
            checkpoint=descriptor.matched_event_id,
        )
        logger.info(
            "merge on_action: rule_id=%s ewo_id=%s",
            descriptor.rule_id,
            ewo_id,
        )
        return self.execute(ctx)

    def _write_manifest(self, ctx: MergeContext, merge_id: str) -> Path | None:
        if self.bus is None:
            return None
        manifest = {
            "merge_id": merge_id,
            "program_id": ctx.program_id,
            "ewo_id": ctx.ewo_id,
            "packet_ids": list(ctx.packet_ids),
            "merge_order_index": ctx.merge_order_index,
            "generated_at": datetime.now(UTC).isoformat(),
            "integrator": "external",
            "note": "Runtime does not mutate git — integrator worker performs merge",
        }
        path = self.bus.repo_root / ".builder-engine" / "last-merge-manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def _emit_completed(self, ctx: MergeContext, result: MergeResult) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "MergeCompleted",
                {
                    "merge_id": result.merge_id,
                    "job_id": ctx.job_id,
                    "ewo_id": ctx.ewo_id,
                    "program_id": ctx.program_id,
                    "packet_ids": list(ctx.packet_ids),
                    "manifest_path": result.manifest_path,
                },
                program_id=ctx.program_id,
                cycle_id=self.cycle_id,
            )
        )

    def _emit_failed(self, ctx: MergeContext, result: MergeResult) -> None:
        self._emit_failed_raw(ctx.ewo_id, result, program_id=ctx.program_id)

    def _emit_failed_raw(
        self,
        ewo_id: str,
        result: MergeResult,
        *,
        program_id: str | None = None,
    ) -> None:
        if self.bus is None:
            return
        pid = program_id or self.program.program_id
        self.bus.publish(
            event_now(
                "MergeFailed",
                {
                    "ewo_id": ewo_id,
                    "program_id": pid,
                    "reason": result.reason,
                    "outcome": result.outcome,
                },
                program_id=pid,
                cycle_id=self.cycle_id,
            )
        )

    def _record_report(self, result: MergeResult) -> None:
        self._last_report = MergeReport(
            last_outcome=result.outcome,
            reason=result.reason,
            merge_id=result.merge_id,
            completed_count=len(self._completed),
        )


def register_merge_plugin(registry: Any, plugin: MergePlugin) -> None:
    """Register MergePlugin factory on PluginRegistry as merge interface."""
    registry.register("merge", 1, "merge", lambda: plugin)


def execute_merge_action(
    registry: Any,
    descriptor: ActionDescriptor,
    *,
    event_payload: dict[str, Any] | None = None,
) -> MergeResult:
    """Resolve merge plugin from registry and execute rule action."""
    plugin = registry.resolve(descriptor)
    return plugin.on_action(descriptor, event_payload=event_payload)


def _coerce_context(context: MergeContext | dict[str, Any]) -> MergeContext:
    if isinstance(context, MergeContext):
        return context
    return MergeContext(
        job_id=str(context.get("job_id") or context.get("ewo_id") or ""),
        program_id=str(context.get("program_id") or ""),
        ewo_id=str(context.get("ewo_id") or context.get("job_id") or ""),
        packet_ids=tuple(context.get("packet_ids") or ()),
        merge_order_index=int(context.get("merge_order_index", 0)),
        checkpoint=context.get("checkpoint"),
    )
