"""Minimal replan — advisory proposals only, no STATE writes (MB2 D5)."""

from __future__ import annotations

from dataclasses import dataclass

from builder_engine.events import BuildEvent, BuildEventBus, event_now
from builder_engine.runtime import SyncResult


@dataclass(frozen=True)
class ReplanProposal:
    trigger: str
    failed_packets: tuple[str, ...]
    suggested_actions: tuple[str, ...]
    recovery_packet_snippet: str | None = None


def minimal_replan(
    sync_result: SyncResult,
    *,
    bus: BuildEventBus | None = None,
    cycle_id: str | None = None,
) -> ReplanProposal | None:
    """Produce recovery guidance after validation failures — never writes STATE."""
    if not sync_result.failed:
        return None

    failed = tuple(sync_result.failed)
    actions = tuple(
        f"Inspect integration_notes for {pid}; add fix packet or reset status to ready"
        for pid in failed
    )
    snippet = (
        "# Suggested recovery packet (operator applies manually to STATE.yaml)\n"
        f"  FIX-{failed[0]}:\n"
        "    wave: <current>\n"
        "    agent_type: implementer\n"
        "    status: ready\n"
        f"    depends_on: [{failed[0]}]\n"
        "    owned_files: []\n"
        "    checks: [make unit-builder-engine]\n"
    )

    proposal = ReplanProposal(
        trigger="ValidationFailed",
        failed_packets=failed,
        suggested_actions=actions,
        recovery_packet_snippet=snippet,
    )

    if bus is not None:
        events: list[BuildEvent] = [
            event_now(
                "Replanned",
                {"trigger": proposal.trigger, "failed": list(failed)},
                cycle_id=cycle_id,
            ),
            event_now(
                "RecoveryTaskCreated",
                {"failed_packets": list(failed), "advisory": True},
                cycle_id=cycle_id,
            ),
        ]
        bus.publish_many(events)

    return proposal
