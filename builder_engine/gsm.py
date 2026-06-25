"""L2 Global State Machine — platform transition registry (Task entity)."""

from __future__ import annotations

from builder_engine import gsm_task
from builder_engine.graph import BuilderGraph
from builder_engine.state_machine import ExecutionState

transition = gsm_task.transition
schedule_packet = gsm_task.schedule_packet
sync_validate_outcome = gsm_task.sync_validate_outcome


class GlobalStateMachine:
    """Authoritative Task FSM (L2 §5.5). Other entities remain governance/cycle-scoped."""

    @staticmethod
    def transition_task(
        current: ExecutionState,
        event: str,
        *,
        graph: BuilderGraph | None = None,
        packet_id: str | None = None,
    ) -> ExecutionState:
        return gsm_task.transition(current, event, graph=graph, packet_id=packet_id)
