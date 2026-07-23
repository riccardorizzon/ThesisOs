"""Session work-proposal artifact — «la salvo» continuity (not chapter SoR).

Pipeline: Chat → Session → Artifact → Continuity → (later) Workspace / definitive knowledge.

«La salvo» means: approved for continuation. Never writes chapters/.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate
from app.services.memory.service import MemoryService

WORK_ARTIFACT_KEY = "companion_work_artifact"
STATUS_APPROVED = "approved_for_continuation"

SAVE_UTTERANCE = re.compile(
    r"(?i)\b("
    r"la\s+salvo|salviamola|salvala|congelala|congeliamola|"
    r"salva\s+(questa|la)\s+(proposta|frase|versione|scelta)|"
    r"congela\s+(questa|la)\s+(proposta|frase|versione)|"
    r"salva\s+il\s+punto|congela|memorizza\s+questo"
    r")\b"
)

_BLOCKQUOTE = re.compile(r"(?m)^\s*>\s?(.+)$")


class WorkArtifact(BaseModel):
    focus: str = "§3.6"
    status: str = STATUS_APPROVED
    proposal: str = ""
    note: str = ""
    saved_at: str = ""


def is_work_save(utterance: str | None) -> bool:
    return bool(utterance and SAVE_UTTERANCE.search(utterance))


def extract_proposal(prior_assistant: str | None, *, fallback: str = "") -> str:
    """Prefer blockquoted draft; else last substantial paragraph of prior reply."""
    text = (prior_assistant or "").strip()
    if not text:
        return (fallback or "").strip()[:2000]
    quotes = [m.group(1).strip() for m in _BLOCKQUOTE.finditer(text) if m.group(1).strip()]
    if quotes:
        return " ".join(quotes)[:2000]
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for p in reversed(paras):
        flat = re.sub(r"\s+", " ", p)
        if len(flat) >= 40 and not re.search(
            r"(?i)^(ricevuto|perfetto|ok|qual[ei]\b|perch)", flat
        ):
            return flat[:2000]
    flat = re.sub(r"\s+", " ", text)
    return flat[:2000] if flat else (fallback or "")[:2000]


def format_work_artifact(art: WorkArtifact) -> str:
    stamp = art.saved_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Proposta di lavoro in sessione ({stamp})",
        "",
        f"**Focus:** {art.focus}",
        f"**Stato:** {art.status}",
        "",
        "## Proposta approvata per continuità",
        art.proposal or "(vuota)",
        "",
        "## Nota",
        art.note or "Salvata in sessione — non ancora promossa a conoscenza definitiva.",
        "",
        "## Regola",
        "Questo NON è il capitolo. È continuità di lavoro per riprendere da qui.",
    ]
    return "\n".join(lines)


def parse_work_artifact_content(content: str | None) -> WorkArtifact | None:
    if not (content or "").strip():
        return None
    focus = "§3.6"
    status = STATUS_APPROVED
    proposal = ""
    note = ""
    m = re.search(r"(?i)\*\*Focus:\*\*\s*(.+)", content)
    if m:
        focus = m.group(1).strip()[:80]
    m = re.search(r"(?i)\*\*Stato:\*\*\s*(.+)", content)
    if m:
        status = m.group(1).strip()[:80]
    m = re.search(
        r"(?is)##\s*Proposta approvata per continuità\s*\n(.+?)(?=\n##\s|\Z)",
        content,
    )
    if m:
        proposal = m.group(1).strip()[:2000]
    m = re.search(r"(?is)##\s*Nota\s*\n(.+?)(?=\n##\s|\Z)", content)
    if m:
        note = m.group(1).strip()[:500]
    return WorkArtifact(focus=focus, status=status, proposal=proposal, note=note)


async def load_work_artifact(memory: MemoryService) -> WorkArtifact | None:
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=WORK_ARTIFACT_KEY, limit=1)
    )
    if not rows:
        return None
    return parse_work_artifact_content(rows[0].content)


async def save_work_artifact(
    memory: MemoryService,
    *,
    proposal: str,
    focus: str = "§3.6",
    note: str = "",
) -> WorkArtifact:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    art = WorkArtifact(
        focus=focus,
        status=STATUS_APPROVED,
        proposal=(proposal or "").strip()[:2000],
        note=note
        or "Salvata in sessione — non ancora promossa a conoscenza definitiva.",
        saved_at=stamp,
    )
    content = format_work_artifact(art)
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=WORK_ARTIFACT_KEY, limit=1)
    )
    if rows:
        row = rows[0]
        await memory.update(
            row.id,
            MemoryUpdate(
                title="Companion work proposal",
                content=content,
                expected_version=row.version,
            ),
        )
        return art
    await memory.create(
        MemoryCreate(
            kind="decision",
            key=WORK_ARTIFACT_KEY,
            title="Companion work proposal",
            content=content,
            source="companion",
        )
    )
    return art


def resume_block(art: WorkArtifact | None) -> str | None:
    if not art or not art.proposal.strip():
        return None
    return (
        f"Proposta di lavoro salvata ({art.status}) su {art.focus}:\n"
        f"{art.proposal[:1200]}"
    )
