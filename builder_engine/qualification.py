"""MB2 Qualification Plugin — SoR §8.2 qualification interface."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from builder_engine.events import BuildEventBus, event_now
from builder_engine.rules import ActionDescriptor
from builder_engine.yaml_loader import load_simple_yaml

logger = logging.getLogger(__name__)

SpawnOutcome = Literal["spawned", "blocked", "failed"]
EvidenceOutcome = Literal["collected", "not_spawned", "failed"]


@dataclass(frozen=True)
class QualificationReport:
    qwo_id: str | None
    last_outcome: SpawnOutcome | EvidenceOutcome | Literal["none"]
    reason: str
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin": "qualification",
            "qwo_id": self.qwo_id,
            "last_outcome": self.last_outcome,
            "reason": self.reason,
            "evidence_refs": list(self.evidence_refs),
        }


def _load_spawn_fixture(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = load_simple_yaml(path.read_text(encoding="utf-8"))
    spawns = data.get("qwo_spawns")
    return spawns if isinstance(spawns, dict) else {}


class QualificationPlugin:
    """MB2 Qualification Plugin — coverage-gated QWO spawn, event emission."""

    def __init__(
        self,
        *,
        program_id: str = "builder",
        bus: BuildEventBus | None = None,
        cycle_id: str | None = None,
        coverage_gate: str | None = None,
        spawn_fixture: Path | None = None,
    ) -> None:
        self.program_id = program_id
        self.bus = bus
        self.cycle_id = cycle_id
        self._coverage_gate = coverage_gate
        self._spawns = _load_spawn_fixture(spawn_fixture)
        self._active_qwo_id: str | None = None
        self._integration_context: dict[str, Any] = {}
        self._evidence_refs: tuple[str, ...] = ()
        self._last_report: QualificationReport | None = None

    def spawn(
        self,
        qwo_id: str,
        *,
        coverage_gate: str | None = None,
        integration_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Spawn QWO — emits QwoSpawned only when coverage gate passes (§7.3)."""
        ctx = dict(integration_context or {})
        self._integration_context = ctx
        fixture_key = str(ctx.get("integration_id") or qwo_id)
        fixture = self._spawns.get(fixture_key, self._spawns.get(qwo_id, {}))
        effective_coverage = (
            coverage_gate
            or self._coverage_gate
            or fixture.get("coverage_gate")
            or "passed"
        )
        if effective_coverage != "passed":
            report = QualificationReport(
                qwo_id=qwo_id,
                last_outcome="blocked",
                reason="coverage_gate not passed — QWO not spawned (§7.3)",
            )
            self._last_report = report
            return {"outcome": "blocked", "reason": report.reason}

        resolved_qwo_id = str(fixture.get("qwo_id") or qwo_id)
        spawn_outcome = fixture.get("spawn_outcome", "success")
        if spawn_outcome == "failed":
            reason = str(fixture.get("failure_reason") or "qualification spawn failed")
            self._emit_failed(resolved_qwo_id, reason)
            self._emit_escalated(resolved_qwo_id, reason)
            report = QualificationReport(
                qwo_id=resolved_qwo_id,
                last_outcome="failed",
                reason=reason,
            )
            self._last_report = report
            return {"outcome": "failed", "qwo_id": resolved_qwo_id, "reason": reason}

        self._active_qwo_id = resolved_qwo_id
        evidence_paths = fixture.get("evidence_paths") or []
        self._evidence_refs = tuple(str(p) for p in evidence_paths)
        self._emit_spawned(resolved_qwo_id)
        report = QualificationReport(
            qwo_id=resolved_qwo_id,
            last_outcome="spawned",
            reason="QWO spawned",
            evidence_refs=self._evidence_refs,
        )
        self._last_report = report
        return {"outcome": "spawned", "qwo_id": resolved_qwo_id}

    def collect_evidence(self) -> dict[str, Any]:
        """Collect evidence artifact refs — stub; no Ground Truth edits (§8.2)."""
        if self._active_qwo_id is None:
            report = QualificationReport(
                qwo_id=None,
                last_outcome="not_spawned",
                reason="no active QWO — call spawn() first",
            )
            self._last_report = report
            return {"outcome": "not_spawned", "reason": report.reason, "evidence_refs": []}

        qwo_id = self._active_qwo_id
        fixture_key = str(self._integration_context.get("integration_id") or qwo_id)
        fixture = self._spawns.get(fixture_key, self._spawns.get(qwo_id, {}))
        evidence_outcome = fixture.get("evidence_outcome", "collected")

        if evidence_outcome == "failed":
            reason = str(fixture.get("evidence_failure_reason") or "evidence collection failed")
            self._emit_failed(qwo_id, reason)
            self._emit_escalated(qwo_id, reason)
            report = QualificationReport(
                qwo_id=qwo_id,
                last_outcome="failed",
                reason=reason,
                evidence_refs=self._evidence_refs,
            )
            self._last_report = report
            return {
                "outcome": "failed",
                "qwo_id": qwo_id,
                "reason": reason,
                "evidence_refs": list(self._evidence_refs),
            }

        refs = self._evidence_refs or (
            f".asep/certificates/{qwo_id.lower()}-stub.yaml",
        )
        self._evidence_refs = tuple(refs)
        report = QualificationReport(
            qwo_id=qwo_id,
            last_outcome="collected",
            reason="evidence collected",
            evidence_refs=self._evidence_refs,
        )
        self._last_report = report
        return {
            "outcome": "collected",
            "qwo_id": qwo_id,
            "evidence_refs": list(self._evidence_refs),
        }

    def report(self) -> dict[str, Any]:
        """Return last execution summary per §8.2."""
        if self._last_report is None:
            return {
                "plugin": "qualification",
                "qwo_id": None,
                "last_outcome": "none",
                "reason": "no qualification executed yet",
                "evidence_refs": [],
            }
        return self._last_report.to_dict()

    def on_action(
        self,
        descriptor: ActionDescriptor,
        *,
        event_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Rule Engine hook — spawn QWO from IntegrationPassed payload."""
        payload = dict(event_payload or {})
        integration_id = str(
            payload.get("integration_id")
            or descriptor.params.get("integration_id")
            or "default-integration"
        )
        qwo_id = str(
            payload.get("qwo_id")
            or descriptor.params.get("qwo_id")
            or f"QWO-{integration_id}"
        )
        coverage_gate = payload.get("coverage_gate")
        integration_context = {
            "integration_id": integration_id,
            "merge_id": payload.get("merge_id"),
            "ewo_id": payload.get("ewo_id"),
            "program_id": payload.get("program_id") or self.program_id,
        }
        logger.info(
            "qualification on_action: rule_id=%s qwo_id=%s integration_id=%s",
            descriptor.rule_id,
            qwo_id,
            integration_id,
        )
        spawn_result = self.spawn(
            qwo_id,
            coverage_gate=str(coverage_gate) if coverage_gate is not None else None,
            integration_context=integration_context,
        )
        if spawn_result["outcome"] != "spawned":
            return spawn_result
        return self.collect_evidence()

    def _emit_spawned(self, qwo_id: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "QwoSpawned",
                {
                    "qwo_id": qwo_id,
                    "program_id": self._integration_context.get("program_id") or self.program_id,
                    "integration_id": self._integration_context.get("integration_id"),
                    "merge_id": self._integration_context.get("merge_id"),
                    "ewo_id": self._integration_context.get("ewo_id"),
                    "evidence_paths": list(self._evidence_refs),
                },
                program_id=str(self._integration_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )

    def _emit_failed(self, qwo_id: str, reason: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "QwoFailed",
                {
                    "qwo_id": qwo_id,
                    "program_id": self._integration_context.get("program_id") or self.program_id,
                    "integration_id": self._integration_context.get("integration_id"),
                    "reason": reason,
                },
                program_id=str(self._integration_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )

    def _emit_escalated(self, qwo_id: str, reason: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "RuntimeEscalated",
                {
                    "qwo_id": qwo_id,
                    "program_id": self._integration_context.get("program_id") or self.program_id,
                    "reason": reason,
                    "supervisor_action": "WAIT",
                },
                program_id=str(self._integration_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )


def register_qualification_plugin(registry: Any, plugin: QualificationPlugin) -> None:
    """Register QualificationPlugin factory on PluginRegistry as qualification interface."""
    registry.register("qualification", 1, "qualification", lambda: plugin)


def execute_qualification_action(
    registry: Any,
    descriptor: ActionDescriptor,
    *,
    event_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve qualification plugin from registry and execute rule action."""
    plugin = registry.resolve(descriptor)
    return plugin.on_action(descriptor, event_payload=event_payload)
