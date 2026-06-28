"""Engineering runtime cycle — preflight and postflight orchestration (MB2 D6)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder_engine.events import BuildEventBus, event_now, new_cycle_id
from builder_engine.observe import ObservedSnapshot, StateObserver
from builder_engine.paths import default_state_path
from builder_engine.planner import Plan, PlanError, build_plan
from builder_engine.policy import PolicyDecision, PolicyEngine
from builder_engine.replan import ReplanProposal, minimal_replan
from builder_engine.runtime import SyncResult


@dataclass(frozen=True)
class PreflightResult:
    cycle_id: str
    snapshot: ObservedSnapshot
    policy: PolicyDecision
    plan: Plan | None


class CycleError(Exception):
    """Preflight or postflight cycle failure."""


class EngineeringRuntimeCycle:
    """Observe → Policies → Plan preflight; publish + replan postflight."""

    def __init__(
        self,
        repo_root: Path,
        state_path: Path | None = None,
        bus: BuildEventBus | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.state_path = (state_path or default_state_path(self.repo_root)).resolve()
        self.bus = bus or BuildEventBus(self.repo_root)

    def run_preflight(self, *, cycle_id: str | None = None) -> PreflightResult:
        cid = cycle_id or new_cycle_id()
        self.bus.publish(event_now("CycleStarted", {"phase": "preflight"}, cycle_id=cid))

        snapshot = StateObserver(self.repo_root, self.state_path).observe()
        self.bus.publish(
            event_now(
                "SnapshotCreated",
                {"state_path": snapshot.state_path, "is_complete": snapshot.is_complete},
                cycle_id=cid,
            )
        )
        self.bus.publish(
            event_now(
                "StateObserved",
                {"epic": snapshot.epic, "wave": snapshot.wave, "ready_count": snapshot.ready_count},
                cycle_id=cid,
            )
        )

        policy = PolicyEngine(self.repo_root).evaluate(snapshot)
        if policy.outcome == "block":
            self.bus.publish(
                event_now(
                    "PolicyBlocked",
                    {"violations": [v.message for v in policy.violations]},
                    cycle_id=cid,
                )
            )
            self.bus.publish(event_now("CycleHalted", {"reason": "policy_block"}, cycle_id=cid))
            return PreflightResult(cycle_id=cid, snapshot=snapshot, policy=policy, plan=None)

        self.bus.publish(
            event_now("PolicyAllowed", {"outcome": policy.outcome}, cycle_id=cid)
        )

        plan: Plan | None = None
        try:
            plan = build_plan(snapshot, policy)
            event_type = "PlanEmpty" if plan.empty else "PlanGenerated"
            self.bus.publish(
                event_now(
                    event_type,
                    {
                        "ready_packets": list(plan.ready_packets),
                        "critical_path": list(plan.critical_path),
                        "empty": plan.empty,
                    },
                    cycle_id=cid,
                )
            )
        except PlanError:
            self.bus.publish(event_now("CycleHalted", {"reason": "plan_error"}, cycle_id=cid))

        return PreflightResult(cycle_id=cid, snapshot=snapshot, policy=policy, plan=plan)

    def run_postflight(
        self,
        sync_result: SyncResult,
        *,
        cycle_id: str | None = None,
    ) -> ReplanProposal | None:
        cid = cycle_id or new_cycle_id()

        for pid in sync_result.completed:
            self.bus.publish(
                event_now("ValidationPassed", {"packet_id": pid}, cycle_id=cid)
            )
        for pid in sync_result.failed:
            self.bus.publish(
                event_now("ValidationFailed", {"packet_id": pid}, cycle_id=cid)
            )

        if sync_result.completed or sync_result.failed:
            self.bus.publish(
                event_now(
                    "StateUpdated",
                    {
                        "completed": list(sync_result.completed),
                        "failed": list(sync_result.failed),
                    },
                    cycle_id=cid,
                )
            )

        if sync_result.advanced_to_wave is not None:
            self.bus.publish(
                event_now(
                    "WaveAdvanced",
                    {"wave": sync_result.advanced_to_wave},
                    cycle_id=cid,
                )
            )

        proposal = minimal_replan(sync_result, bus=self.bus, cycle_id=cid)

        self.bus.publish(
            event_now("EventsPublished", {"phase": "postflight"}, cycle_id=cid)
        )
        return proposal
