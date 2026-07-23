"""Persistence contract — what ThesisOS persists (ADR-0046).

ThesisOS saves intellectual work, not messages. Exactly four tiers exist:

- ``NONE``: plain conversation («spiegami Derrida») — never persisted beyond
  the message log.
- ``SESSION_STATE``: where the work stands («basta per oggi» work-close) —
  stored via :func:`app.services.workspace.companion_session.save_session_close`.
- ``WORK_ARTIFACT``: something produced in session («la salvo» proposal) —
  stored via :func:`app.services.workspace.work_artifact.save_work_artifact`.
- ``PERSISTENT_MEMORY``: rules and decisions that survive over time —
  written by the learning loop (``learning_loop.append_learned_rule``) and by
  binding decisions, both confirmed explicitly before generation.

Invariant (NO WRITE = NO SAVE): a saved-confirmation may reach the user only
after the corresponding write succeeded. On failure the turn must end with an
honest failure message — never with a fake confirmation.

The rendered [COMPANION RESUME] block is the single source of truth for the
current focus and next action (see ``render.render_companion_resume``); this
module parses them back so every write is anchored to the same resume the
user and the model saw.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from app.services.memory.service import MemoryService
from app.services.workspace.companion_session import save_session_close
from app.services.workspace.work_artifact import extract_proposal, save_work_artifact

logger = logging.getLogger("app.services.workspace.persistence")

DEFAULT_FOCUS = "§3.6"


class PersistenceTier(str, Enum):
    NONE = "none"
    SESSION_STATE = "session_state"
    WORK_ARTIFACT = "work_artifact"
    PERSISTENT_MEMORY = "persistent_memory"


def classify_persistence(*, preserve: bool = False, save: bool = False) -> PersistenceTier:
    """Map the active Companion turn contract to a persistence tier.

    ``PERSISTENT_MEMORY`` is intentionally absent here: confirmed collaboration
    rules are written by the learning loop before generation, not per-turn.
    """
    if preserve:
        return PersistenceTier.SESSION_STATE
    if save:
        return PersistenceTier.WORK_ARTIFACT
    return PersistenceTier.NONE


@dataclass(frozen=True)
class PersistenceOutcome:
    tier: PersistenceTier
    persisted: bool
    error: str | None = None


# Inverse of render.render_companion_resume — resume is the single source of truth.
_RESUME_FOCUS_RE = re.compile(r"(?m)^Focus:\s*.+?·\s*(\S+)")
_RESUME_NEXT_RE = re.compile(r"(?m)^Prossima azione suggerita:\s*(.+)$")


def focus_from_resume(system_contents: Iterable[str]) -> str:
    for content in system_contents:
        if "[COMPANION RESUME]" not in content:
            continue
        m = _RESUME_FOCUS_RE.search(content)
        if m:
            return m.group(1).strip()[:80]
    return DEFAULT_FOCUS


def next_action_from_resume(system_contents: Iterable[str]) -> str | None:
    for content in system_contents:
        if "[COMPANION RESUME]" not in content:
            continue
        m = _RESUME_NEXT_RE.search(content)
        if m and m.group(1).strip():
            return m.group(1).strip()[:500]
    return None


async def persist_turn(
    memory: MemoryService,
    *,
    tier: PersistenceTier,
    user_text: str,
    assistant_text: str,
    prior_assistant: str | None = None,
    focus: str = DEFAULT_FOCUS,
    next_action: str | None = None,
) -> PersistenceOutcome:
    """Execute the write required by ``tier``. NO WRITE = NO SAVE.

    Returns the outcome; the caller must not confirm a save to the user
    unless ``persisted`` is True.
    """
    if tier is PersistenceTier.SESSION_STATE:
        try:
            await save_session_close(
                memory,
                user_text=user_text,
                assistant_text=assistant_text,
                focus=focus,
                next_action=next_action,
            )
            return PersistenceOutcome(tier=tier, persisted=True)
        except Exception as exc:
            logger.exception("session-state persistence failed (focus %s)", focus)
            return PersistenceOutcome(tier=tier, persisted=False, error=str(exc))

    if tier is PersistenceTier.WORK_ARTIFACT:
        try:
            proposal = extract_proposal(prior_assistant, fallback=assistant_text)
            await save_work_artifact(memory, proposal=proposal, focus=focus)
            return PersistenceOutcome(tier=tier, persisted=True)
        except Exception as exc:
            logger.exception("work-artifact persistence failed (focus %s)", focus)
            return PersistenceOutcome(tier=tier, persisted=False, error=str(exc))

    return PersistenceOutcome(tier=tier, persisted=False)


def persistence_failure_text(tier: PersistenceTier, *, focus: str = DEFAULT_FOCUS) -> str:
    """Honest reply when the write failed — never claims the save happened."""
    if tier is PersistenceTier.SESSION_STATE:
        return (
            "Non sono riuscita a registrare il punto di ripresa di oggi: "
            "c'è stato un errore tecnico e la chiusura NON è stata salvata.\n\n"
            "Il lavoro resta visibile in questa conversazione, ma domani non lo "
            "ritroverei in apertura. Riprova tra un momento con «basta per oggi»."
        )
    return (
        "Non sono riuscita a salvare la proposta: c'è stato un errore tecnico, "
        f"quindi NON è entrata nel punto di ripresa su {focus}.\n\n"
        "Resta visibile qui in conversazione. Riprova tra un momento con «la salvo»."
    )
