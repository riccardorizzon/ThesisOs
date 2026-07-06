"""MB2 Integration Plugin — SoR §8.2 integration interface."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from builder_engine.events import BuildEventBus, event_now
from builder_engine.rules import ActionDescriptor
from builder_engine.yaml_loader import load_simple_yaml

logger = logging.getLogger(__name__)

StartOutcome = Literal["started", "blocked"]
CheckOutcome = Literal["passed", "failed", "not_started"]


@dataclass(frozen=True)
class IntegrationReport:
    integration_id: str | None
    last_outcome: CheckOutcome | StartOutcome | Literal["none"]
    reason: str
    checks_run: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin": "integration",
            "integration_id": self.integration_id,
            "last_outcome": self.last_outcome,
            "reason": self.reason,
            "checks_run": self.checks_run,
        }


def _load_checks_fixture(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    data = load_simple_yaml(path.read_text(encoding="utf-8"))
    integrations = data.get("integrations")
    return integrations if isinstance(integrations, dict) else {}


class IntegrationPlugin:
    """MB2 Integration Plugin — CI-gated checks after merge, event emission."""

    def __init__(
        self,
        *,
        program_id: str = "builder",
        bus: BuildEventBus | None = None,
        cycle_id: str | None = None,
        ci_status: str | None = None,
        checks_fixture: Path | None = None,
    ) -> None:
        self.program_id = program_id
        self.bus = bus
        self.cycle_id = cycle_id
        self._ci_status = ci_status
        self._checks = _load_checks_fixture(checks_fixture)
        self._active_id: str | None = None
        self._merge_context: dict[str, Any] = {}
        self._last_report: IntegrationReport | None = None

    def start(
        self,
        integration_id: str,
        *,
        ci_status: str | None = None,
        merge_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Begin integration — emits IntegrationStarted only when CI guard passes (§10.2)."""
        fixture = self._checks.get(integration_id, {})
        effective_ci = (
            ci_status
            or self._ci_status
            or fixture.get("ci_status")
            or "passed"
        )
        if effective_ci != "passed":
            report = IntegrationReport(
                integration_id=integration_id,
                last_outcome="blocked",
                reason="ci_status not passed — integration not started (§10.2)",
            )
            self._last_report = report
            return {"outcome": "blocked", "reason": report.reason}

        self._active_id = integration_id
        self._merge_context = dict(merge_context or {})
        self._emit_started(integration_id)
        report = IntegrationReport(
            integration_id=integration_id,
            last_outcome="started",
            reason="integration started",
        )
        self._last_report = report
        return {"outcome": "started", "integration_id": integration_id}

    def run_checks(self) -> dict[str, Any]:
        """Run integration checks — stub reads fixture; extension point for live CI."""
        if self._active_id is None:
            report = IntegrationReport(
                integration_id=None,
                last_outcome="not_started",
                reason="no active integration — call start() first",
            )
            self._last_report = report
            return {"outcome": "not_started", "reason": report.reason}

        integration_id = self._active_id
        fixture = self._checks.get(integration_id, {})
        checks_run = int(fixture.get("checks_count") or 0)
        check_outcome = fixture.get("check_outcome", "passed")

        if check_outcome == "failed":
            check_id = fixture.get("failed_check_id", "unknown")
            reason = f"check failed: {check_id}"
            self._emit_failed(integration_id, reason)
            report = IntegrationReport(
                integration_id=integration_id,
                last_outcome="failed",
                reason=reason,
                checks_run=max(checks_run, 1),
            )
            self._last_report = report
            return {
                "outcome": "failed",
                "integration_id": integration_id,
                "reason": reason,
                "checks_run": report.checks_run,
            }

        self._emit_passed(integration_id)
        report = IntegrationReport(
            integration_id=integration_id,
            last_outcome="passed",
            reason="all checks passed",
            checks_run=checks_run,
        )
        self._last_report = report
        return {
            "outcome": "passed",
            "integration_id": integration_id,
            "checks_run": checks_run,
        }

    def report(self) -> dict[str, Any]:
        """Return last execution summary per §8.2."""
        if self._last_report is None:
            return {
                "plugin": "integration",
                "integration_id": None,
                "last_outcome": "none",
                "reason": "no integration executed yet",
                "checks_run": 0,
            }
        return self._last_report.to_dict()

    def on_action(
        self,
        descriptor: ActionDescriptor,
        *,
        event_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Rule Engine hook — start integration from MergeCompleted payload."""
        payload = dict(event_payload or {})
        integration_id = str(
            payload.get("integration_id")
            or descriptor.params.get("integration_id")
            or payload.get("ewo_id")
            or "default-integration"
        )
        ci_status = payload.get("ci_status")
        merge_context = {
            "merge_id": payload.get("merge_id"),
            "ewo_id": payload.get("ewo_id"),
            "program_id": payload.get("program_id") or self.program_id,
        }
        logger.info(
            "integration on_action: rule_id=%s integration_id=%s",
            descriptor.rule_id,
            integration_id,
        )
        start_result = self.start(
            integration_id,
            ci_status=str(ci_status) if ci_status is not None else None,
            merge_context=merge_context,
        )
        if start_result["outcome"] != "started":
            return start_result
        return self.run_checks()

    def _emit_started(self, integration_id: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "IntegrationStarted",
                {
                    "integration_id": integration_id,
                    "program_id": self._merge_context.get("program_id") or self.program_id,
                    "merge_id": self._merge_context.get("merge_id"),
                    "ewo_id": self._merge_context.get("ewo_id"),
                },
                program_id=str(self._merge_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )

    def _emit_passed(self, integration_id: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "IntegrationPassed",
                {
                    "integration_id": integration_id,
                    "program_id": self._merge_context.get("program_id") or self.program_id,
                    "merge_id": self._merge_context.get("merge_id"),
                    "ewo_id": self._merge_context.get("ewo_id"),
                },
                program_id=str(self._merge_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )

    def _emit_failed(self, integration_id: str, reason: str) -> None:
        if self.bus is None:
            return
        self.bus.publish(
            event_now(
                "IntegrationFailed",
                {
                    "integration_id": integration_id,
                    "program_id": self._merge_context.get("program_id") or self.program_id,
                    "merge_id": self._merge_context.get("merge_id"),
                    "ewo_id": self._merge_context.get("ewo_id"),
                    "reason": reason,
                },
                program_id=str(self._merge_context.get("program_id") or self.program_id),
                cycle_id=self.cycle_id,
            )
        )


def register_integration_plugin(registry: Any, plugin: IntegrationPlugin) -> None:
    """Register IntegrationPlugin factory on PluginRegistry as integration interface."""
    registry.register("integration", 1, "integration", lambda: plugin)


def execute_integration_action(
    registry: Any,
    descriptor: ActionDescriptor,
    *,
    event_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve integration plugin from registry and execute rule action."""
    plugin = registry.resolve(descriptor)
    return plugin.on_action(descriptor, event_payload=event_payload)
