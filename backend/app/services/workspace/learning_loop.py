"""Learning Loop v1 — learn how WE work (PM-008 §6).

Not thesis facts. Collaboration rules stated by Ilaria, confirmed, then applied.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate
from app.services.memory.service import MemoryService

LEARNED_SECTION = "## Regole imparate"
PENDING_KEY = "companion_learning_pending"
_COLLABORATION_TITLE = "Come collaboriamo"

# Utterances that change how we collaborate (not thesis content)
_RULE_SIGNAL = re.compile(
    r"(?i)\b("
    r"preferisco|sempre|non\s+(?:modificare|cambiare|imporre)\b|"
    r"da\s+oggi|meglio\s+se|prima\s+.+\s+poi|"
    r"tre\s+possibilit|cinque\s+possibilit|"
    r"riepilogo\s+iniziale|revisioni?\s+conservative|"
    r"non\s+modificare\s+mai"
    r")"
)

_CONFIRM = re.compile(
    r"(?i)^\s*("
    r"confermo|"
    r"s[iì],?\s*confermo|"
    r"ok,?\s*confermo|"
    r"d['']accordo|"
    r"va\s+bene\s+cos[iì]|"
    r"s[iì],?\s*da\s+ora|"
    # Bare sì/ok only count when a pending rule exists (checked in process_learning_turn)
    r"s[iì]|si|ok|okay|va\s+bene|perfetto"
    r")\s*[.!?]?\s*$"
)

# Avoid treating CONTINUE / PRESERVE as learning
_NOT_LEARNING = re.compile(
    r"(?i)\b(basta\s+per\s+oggi|chiudiamo|continuiamo\s+da|ciao\b|vuoi\s+continuare)\b"
)


def looks_like_collaboration_rule(utterance: str | None) -> bool:
    text = (utterance or "").strip()
    if len(text) < 12 or len(text) > 400:
        return False
    if _NOT_LEARNING.search(text):
        return False
    # REVIEW choice — not a lasting collaboration rule
    if re.search(
        r"(?i)\b(preferisco\s+la\s+(prima|seconda|terza)|opzione\s*[abc123]|la\s+[abc]\b)\b",
        text,
    ):
        return False
    if not _RULE_SIGNAL.search(text):
        return False
    # Thesis-fact heuristic: chapter refs alone are not collaboration rules
    if re.search(r"(?i)^\s*§?\d", text) and "prefer" not in text.lower():
        return False
    return True


def is_learning_confirmation(utterance: str | None) -> bool:
    return bool(utterance and _CONFIRM.match(utterance.strip()))


def learning_confirm_hint(rule_text: str) -> str:
    return (
        "[INTERNAL — LEARNING LOOP]\n"
        f"Ilaria ha espresso una regola di collaborazione: «{rule_text[:200]}».\n"
        "Chiedi conferma breve. Accetta «sì» / «ok» / «confermo».\n"
        "Es.: «Ho capito: da ora lavoriamo così. Confermi?»\n"
        "Non aggiornare la memoria tesi. Non inventare regole."
    )


async def load_pending_rule(memory: MemoryService) -> str | None:
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=PENDING_KEY, limit=1)
    )
    if not rows:
        return None
    return rows[0].content.strip() or None


async def set_pending_rule(memory: MemoryService, rule_text: str) -> None:
    content = rule_text.strip()[:500]
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=PENDING_KEY, limit=1)
    )
    if rows:
        row = rows[0]
        await memory.update(
            row.id,
            MemoryUpdate(content=content, expected_version=row.version),
        )
        return
    await memory.create(
        MemoryCreate(
            kind="decision",
            key=PENDING_KEY,
            title="Collaboration rule pending confirmation",
            content=content,
            source="companion",
        )
    )


async def clear_pending_rule(memory: MemoryService) -> None:
    rows = await memory.list(
        MemoryListFilters(kind="decision", key=PENDING_KEY, limit=1)
    )
    if not rows:
        return
    # Soft-clear content (decision rows may not be deletable as singleton-ish)
    row = rows[0]
    await memory.update(
        row.id,
        MemoryUpdate(content="", expected_version=row.version),
    )


def _split_seed_and_learned(content: str) -> tuple[str, str]:
    if LEARNED_SECTION in content:
        seed, _, learned = content.partition(LEARNED_SECTION)
        return seed.rstrip(), learned.strip()
    return content.rstrip(), ""


async def append_learned_rule(memory: MemoryService, rule_text: str) -> None:
    """Append confirmed collaboration rule under ## Regole imparate."""
    from app.services.workspace.thesis_knowledge import load_collaboration_rules

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    line = f"- ({stamp}) {rule_text.strip()[:400]}"

    rows = await memory.list(MemoryListFilters(kind="user", limit=1))
    seed = load_collaboration_rules() or ""

    if not rows:
        body = seed
        if body:
            body += f"\n\n{LEARNED_SECTION}\n{line}\n"
        else:
            body = f"{LEARNED_SECTION}\n{line}\n"
        await memory.create(
            MemoryCreate(
                kind="user",
                key="user",
                title=_COLLABORATION_TITLE,
                content=body,
                pinned=True,
                source="learning",
            )
        )
        return

    row = rows[0]
    seed_part, learned = _split_seed_and_learned(row.content)
    # Prefer live seed file if present
    if seed:
        seed_part = seed
    learned_lines = [ln for ln in learned.splitlines() if ln.strip()]
    # Dedup similar
    if any(rule_text.strip()[:60].lower() in ln.lower() for ln in learned_lines):
        return
    learned_lines.append(line)
    new_content = seed_part.rstrip() + f"\n\n{LEARNED_SECTION}\n" + "\n".join(learned_lines) + "\n"
    await memory.update(
        row.id,
        MemoryUpdate(
            title=_COLLABORATION_TITLE,
            content=new_content,
            pinned=True,
            expected_version=row.version,
        ),
    )


async def process_learning_turn(
    memory: MemoryService,
    *,
    user_text: str,
) -> str | None:
    """Handle confirm or stage a new pending rule. Returns hint for next system inject, if any."""
    pending = await load_pending_rule(memory)
    text = (user_text or "").strip()

    # Opening a new day abandons stale pending (avoid «sì» after 09:00 learning junk)
    if pending and re.search(
        r"(?i)(__companion_open__|\bciao\b|continuiamo\s+da\s+ieri)",
        text,
    ):
        await clear_pending_rule(memory)
        return None

    if pending and is_learning_confirmation(text):
        await append_learned_rule(memory, pending)
        await clear_pending_rule(memory)
        return None

    if looks_like_collaboration_rule(text):
        await set_pending_rule(memory, text)
        return learning_confirm_hint(text)

    return None
