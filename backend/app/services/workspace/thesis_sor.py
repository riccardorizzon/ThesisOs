"""Thesis-agent source-of-truth contract (Companion v1).

Pattern: knowledge/thesis-agent/ files are the only authoritative identity/progress.
Runtime reads via thesis_knowledge.py; DB memory is a cache reconciled on access.
Do not duplicate title/author/focus in registry seeds, migration scripts, or frontend constants.
"""

from __future__ import annotations

from app.schemas.context import DEFAULT_PROJECT_ID
from app.services.memory.service import MemoryService
from app.services.workspace.thesis_memory_sync import (
    ensure_collaboration_memory,
    ensure_pinned_thesis_memory,
)

THESIS_AGENT_PROJECT_ID = DEFAULT_PROJECT_ID


async def reconcile_thesis_agent_memory(
    memory: MemoryService,
    *,
    project_id: str | None,
) -> None:
    """Keep pinned thesis + collaboration memory aligned with knowledge files."""
    if project_id == THESIS_AGENT_PROJECT_ID:
        await ensure_pinned_thesis_memory(memory)
        await ensure_collaboration_memory(memory)
