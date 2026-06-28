"""Merge eligibility stub — no git mutations (MB2 D8)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MergeOutcome = Literal["deferred", "eligible", "rejected"]


@dataclass(frozen=True)
class MergeEligibility:
    outcome: MergeOutcome
    reason: str
    packet_ids: tuple[str, ...] = ()


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
