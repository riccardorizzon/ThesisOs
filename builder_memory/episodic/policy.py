"""Episodic write policy — allowed and forbidden entry types."""

from __future__ import annotations

ALLOWED_ENTRY_TYPES = frozenset(
    {
        "lesson_learned",
        "architectural_decision",
        "known_risk",
        "milestone_complete",
        "task_outcome",
        "failure_analysis",
    }
)

FORBIDDEN_ENTRY_TYPES = frozenset(
    {
        "file_edit",
        "contract_mutation",
        "adr_mutation",
        "code_generation",
        "source_of_truth",
    }
)


class WritePolicyError(ValueError):
    pass


def validate_entry_type(entry_type: str) -> None:
    if entry_type in FORBIDDEN_ENTRY_TYPES:
        raise WritePolicyError(f"Entry type '{entry_type}' is forbidden by ADR-0019")
    if entry_type not in ALLOWED_ENTRY_TYPES:
        raise WritePolicyError(
            f"Entry type '{entry_type}' is not allowed. "
            f"Allowed: {sorted(ALLOWED_ENTRY_TYPES)}"
        )
