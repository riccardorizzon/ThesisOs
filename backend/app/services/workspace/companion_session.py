"""Persist work-close for inter-day CONTINUE (PM-008 · BASTA PER OGGI).

Product rule: prepare tomorrow's Ilaria. Storage is project-scoped —
any new chat must resume THE WORK, not "the right thread".
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate
from app.services.memory.service import MemoryService

COMPANION_SESSION_KEY = "companion_session"
CLOSE_UTTERANCE = re.compile(
    r"\b(basta per oggi|chiudiamo per oggi|chiudiamo)\b",
    re.I,
)

_DECIDED_RE = re.compile(
    r"(?:oggi\s+)?(?:abbiamo\s+)?deciso[:\s]*([\s\S]*?)(?=(?:non\s+abbiamo|domani\b|\Z))",
    re.I,
)
_OPEN_RE = re.compile(
    r"non\s+abbiamo\s+ancora\s+deciso[:\s]*([\s\S]*?)(?=(?:domani\b|\Z))",
    re.I,
)
_TOMORROW_RE = re.compile(
    r"domani[^\n]*?(?:consiglierei|continuare|da qui)?[:\s]*([\s\S]*?)(?=\Z)",
    re.I,
)


class WorkClose(BaseModel):
    """Structured close — feeds tomorrow 09:00 / any new chat."""

    focus: str = "§3.6"
    decided: list[str] = Field(default_factory=list)
    open_points: list[str] = Field(default_factory=list)
    tomorrow: str = ""
    raw: str = ""


def is_session_close(utterance: str | None) -> bool:
    return bool(utterance and CLOSE_UTTERANCE.search(utterance))


def _bullet_items(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*•]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        if line and len(line) > 2:
            items.append(line[:300])
    if not items and block.strip():
        flat = re.sub(r"\s+", " ", block.strip())
        if flat:
            items.append(flat[:400])
    return items[:8]


def parse_work_close(assistant_text: str, *, focus: str = "§3.6") -> WorkClose:
    """Extract decided / open / tomorrow from PRESERVE reply (best-effort).

    Never returns junk tomorrow (E3 fix) — falls back to usable resume text.
    """
    text = (assistant_text or "").strip()
    decided: list[str] = []
    open_points: list[str] = []
    tomorrow = ""

    m = _DECIDED_RE.search(text)
    if m:
        decided = _bullet_items(m.group(1))
    m = _OPEN_RE.search(text)
    if m:
        open_points = _bullet_items(m.group(1))
    m = _TOMORROW_RE.search(text)
    if m:
        tomorrow = re.sub(r"\s+", " ", m.group(1).strip())[:500]

    if _is_junk_tomorrow(tomorrow) and text:
        paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        if paras:
            candidate = re.sub(r"\s+", " ", paras[-1])[:500]
            if not _is_junk_tomorrow(candidate):
                tomorrow = candidate

    if _is_junk_tomorrow(tomorrow):
        # Structured close failed — store whole reply as resume, never punctuation junk
        flat = re.sub(r"\s+", " ", text)[:500]
        tomorrow = (
            flat
            if len(flat) >= 20
            else f"Riprendere dal focus {focus} — chiusura senza dettaglio strutturato"
        )

    return WorkClose(
        focus=focus,
        decided=decided,
        open_points=open_points,
        tomorrow=tomorrow,
        raw=text,
    )


def _is_junk_tomorrow(value: str) -> bool:
    t = (value or "").strip()
    if len(t) < 12:
        return True
    if re.fullmatch(r"[!?.…,\s]+", t):
        return True
    if re.fullmatch(r"(?i)(ok|okay|a\s+domani|fine|ciao)[!?.…]*", t):
        return True
    return False


def format_work_close(close: WorkClose) -> str:
    """Canonical markdown stored in project memory (chat-agnostic)."""
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Punto di ripresa del lavoro ({stamp})",
        "",
        f"**Focus:** {close.focus}",
        "",
        "## Oggi abbiamo deciso",
    ]
    if close.decided:
        lines.extend(f"- {d}" for d in close.decided)
    else:
        lines.append("- (nessuna decisione esplicita in questa chiusura)")
    lines.extend(["", "## Non abbiamo ancora deciso"])
    if close.open_points:
        lines.extend(f"- {p}" for p in close.open_points)
    else:
        lines.append("- (nessun punto aperto esplicito)")
    lines.extend(
        [
            "",
            "## Domani continua da qui",
            close.tomorrow or "(riprendi dal focus corrente)",
            "",
            "## Testo chiusura Companion",
            close.raw[:3000],
        ]
    )
    return "\n".join(lines)


async def load_last_session_summary(memory: MemoryService) -> str | None:
    """Last work-close summary — chat-agnostic (project memory)."""
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=COMPANION_SESSION_KEY, limit=1)
    )
    if not rows:
        return None
    return rows[0].content.strip() or None


_FOCUS_LINE_RE = re.compile(r"(?im)^\*\*Focus:\*\*\s*(.+)$")
_TOMORROW_HEADING_RE = re.compile(
    r"(?is)##\s*Domani continua da qui\s*\n(.+?)(?=\n##\s|\Z)"
)


def parse_focus_from_summary(content: str | None) -> str | None:
    """Extract focus label from stored work-close markdown."""
    if not (content or "").strip():
        return None
    m = _FOCUS_LINE_RE.search(content)
    if not m:
        return None
    focus = m.group(1).strip()[:80]
    return focus or None


def parse_tomorrow_from_summary(content: str | None) -> str | None:
    """Extract tomorrow / next step from stored work-close markdown."""
    if not (content or "").strip():
        return None
    m = _TOMORROW_HEADING_RE.search(content)
    if not m:
        return None
    tomorrow = re.sub(r"\s+", " ", m.group(1).strip())[:500]
    if _is_junk_tomorrow(tomorrow):
        return None
    return tomorrow


async def save_session_close(
    memory: MemoryService,
    *,
    user_text: str,
    assistant_text: str,
    focus: str = "§3.6",
    next_action: str | None = None,
) -> WorkClose:
    """Persist structured close so tomorrow's 09:00 / any new chat continues the work."""
    close = parse_work_close(assistant_text, focus=focus)
    # Force usable structure when LLM was vague (experience ≥9)
    if not close.decided:
        close.decided = [
            "Nessuna decisione vincolante esplicitata in chiusura — "
            "riparti dal testo di riepilogo sotto"
        ]
    if not close.open_points:
        close.open_points = [f"Continuare il lavoro su {focus}"]
    if _is_junk_tomorrow(close.tomorrow) or not close.tomorrow:
        close.tomorrow = (next_action or f"Riprendere da {focus}").strip()[:500]

    content = format_work_close(close)
    content = content.replace(
        "## Testo chiusura Companion",
        f"**Chiusura utente:** {user_text.strip()}\n\n## Testo chiusura Companion",
    )

    rows = await memory.list(
        MemoryListFilters(kind="decision", key=COMPANION_SESSION_KEY, limit=1)
    )
    if rows:
        row = rows[0]
        await memory.update(
            row.id,
            MemoryUpdate(
                title="Companion work resume",
                content=content,
                expected_version=row.version,
            ),
        )
        return close

    await memory.create(
        MemoryCreate(
            kind="decision",
            key=COMPANION_SESSION_KEY,
            title="Companion work resume",
            content=content,
            source="companion",
        )
    )
    return close
