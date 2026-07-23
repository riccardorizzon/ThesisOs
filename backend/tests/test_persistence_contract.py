"""Persistence contract (ADR-0046) — taxonomy, resume parsing, NO WRITE = NO SAVE."""

from __future__ import annotations

import pytest

from app.services.workspace.persistence import (
    PersistenceTier,
    classify_persistence,
    focus_from_resume,
    next_action_from_resume,
    persist_turn,
    persistence_failure_text,
)
from tests.support.fake_memory import FakeMemoryService

_RESUME_BLOCK = (
    "[COMPANION RESUME]\n"
    "Stato operativo — FACTS ONLY.\n"
    "\n"
    "Focus: Capitolo 3 · §3.4 — Norma, deviazione, mediazione\n"
    "Stato: in revisione\n"
    "Prossima azione suggerita: Rileggere il paragrafo sulla mediazione\n"
)


def test_classify_persistence_maps_the_four_tiers():
    assert classify_persistence(preserve=True) is PersistenceTier.SESSION_STATE
    assert classify_persistence(save=True) is PersistenceTier.WORK_ARTIFACT
    # PRESERVE wins when both hints fire in the same turn (day close prevails)
    assert classify_persistence(preserve=True, save=True) is PersistenceTier.SESSION_STATE
    assert classify_persistence() is PersistenceTier.NONE


def test_resume_is_the_single_source_of_truth_for_focus_and_next_action():
    assert focus_from_resume([_RESUME_BLOCK]) == "§3.4"
    assert (
        next_action_from_resume([_RESUME_BLOCK])
        == "Rileggere il paragrafo sulla mediazione"
    )
    # Without a resume block we fall back to the default focus
    assert focus_from_resume(["altro testo di sistema"]) == "§3.6"
    assert next_action_from_resume(["altro testo di sistema"]) is None


@pytest.mark.asyncio
async def test_persist_turn_session_state_writes_the_work_close():
    memory = FakeMemoryService()

    outcome = await persist_turn(
        memory,
        tier=PersistenceTier.SESSION_STATE,
        user_text="Basta per oggi",
        assistant_text=(
            "Oggi abbiamo deciso: la palette resta.\n"
            "Non abbiamo ancora deciso: la chiusura del §3.4.\n"
            "Domani ti consiglierei di continuare da qui: rileggere la mediazione."
        ),
        focus="§3.4",
    )

    assert outcome.persisted is True
    assert outcome.error is None
    row = memory.row("companion_session")
    assert row is not None
    assert "**Focus:** §3.4" in row.content


@pytest.mark.asyncio
async def test_persist_turn_work_artifact_prefers_prior_proposal():
    memory = FakeMemoryService()

    outcome = await persist_turn(
        memory,
        tier=PersistenceTier.WORK_ARTIFACT,
        user_text="La salvo",
        assistant_text="Salvata per continuità.",
        prior_assistant="Che ne dici di:\n\n> Una frase di prova per il paragrafo.",
        focus="§3.4",
    )

    assert outcome.persisted is True
    row = memory.row("companion_work_artifact")
    assert row is not None
    assert "Una frase di prova per il paragrafo." in row.content


@pytest.mark.asyncio
async def test_persist_turn_reports_failure_instead_of_raising():
    memory = FakeMemoryService(fail_writes=True)

    outcome = await persist_turn(
        memory,
        tier=PersistenceTier.WORK_ARTIFACT,
        user_text="La salvo",
        assistant_text="Salvata.",
    )

    assert outcome.persisted is False
    assert outcome.error is not None
    assert memory.rows == []


@pytest.mark.asyncio
async def test_persist_turn_none_tier_writes_nothing():
    memory = FakeMemoryService()

    outcome = await persist_turn(
        memory,
        tier=PersistenceTier.NONE,
        user_text="Spiegami Derrida",
        assistant_text="Derrida sostiene che...",
    )

    assert outcome.persisted is False
    assert outcome.error is None
    assert memory.rows == []


def test_failure_text_is_honest_and_never_claims_success():
    for tier in (PersistenceTier.SESSION_STATE, PersistenceTier.WORK_ARTIFACT):
        text = persistence_failure_text(tier, focus="§3.4")
        assert "Non sono riuscita" in text
        assert "errore tecnico" in text
