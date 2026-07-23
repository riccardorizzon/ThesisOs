"""Sync pinned thesis memory from knowledge/thesis-agent (replaces stale EWO-1 title)."""

from __future__ import annotations

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate
from app.services.memory.service import MemoryService
from app.services.workspace.thesis_knowledge import load_project_identity, thesis_agent_root

_STALE_TITLES = frozenset(
    {
        "Thesis state (EWO-1 aligned)",
        "Tesi STIGMATA",
    }
)
_MAX_CONTENT_CHARS = 8000


def _thesis_memory_content() -> str:
    path = thesis_agent_root() / "03_PROJECT/Thesis-State.md"
    if not path.is_file():
        return ""
    body = path.read_text(encoding="utf-8").strip()
    if len(body) > _MAX_CONTENT_CHARS:
        body = body[:_MAX_CONTENT_CHARS].rstrip() + "\n…"
    return body


async def ensure_pinned_thesis_memory(memory: MemoryService) -> None:
    """Upsert pinned thesis row so Context API and memory prompts use live knowledge title."""
    identity = load_project_identity()
    if not identity.title:
        return

    content = _thesis_memory_content()
    rows = await memory.list(MemoryListFilters(kind="thesis", limit=1))
    existing = rows[0] if rows else None

    if existing is not None:
        stale = (existing.title or "") in _STALE_TITLES
        needs_update = stale or existing.title != identity.title or not existing.pinned
        if not needs_update and content and existing.content == content:
            return
        await memory.update(
            existing.id,
            MemoryUpdate(
                title=identity.title,
                content=content or existing.content,
                pinned=True,
                expected_version=existing.version,
            ),
        )
        return

    await memory.create(
        MemoryCreate(
            kind="thesis",
            key="thesis",
            title=identity.title,
            content=content or identity.title,
            pinned=True,
            source="knowledge",
        )
    )


_COLLABORATION_TITLE = "Come collaboriamo"
_LEARNED_SECTION = "## Regole imparate"


def _split_seed_and_learned(content: str) -> tuple[str, str]:
    if _LEARNED_SECTION in content:
        seed, _, learned = content.partition(_LEARNED_SECTION)
        return seed.rstrip(), learned.strip()
    return content.rstrip(), ""


async def ensure_collaboration_memory(memory: MemoryService) -> None:
    """Sync seed from knowledge; never wipe ## Regole imparate (Learning Loop)."""
    from app.services.workspace.thesis_knowledge import load_collaboration_rules

    seed = load_collaboration_rules()
    if not seed:
        return

    rows = await memory.list(MemoryListFilters(kind="user", limit=1))
    existing = rows[0] if rows else None

    if existing is None:
        await memory.create(
            MemoryCreate(
                kind="user",
                key="user",
                title=_COLLABORATION_TITLE,
                content=seed,
                pinned=True,
                source="knowledge",
            )
        )
        return

    _, learned = _split_seed_and_learned(existing.content)
    if learned:
        new_content = seed.rstrip() + f"\n\n{_LEARNED_SECTION}\n{learned}\n"
    else:
        new_content = seed

    needs_update = (
        existing.title != _COLLABORATION_TITLE
        or existing.content != new_content
        or not existing.pinned
    )
    if not needs_update:
        return
    await memory.update(
        existing.id,
        MemoryUpdate(
            title=_COLLABORATION_TITLE,
            content=new_content,
            pinned=True,
            expected_version=existing.version,
        ),
    )
