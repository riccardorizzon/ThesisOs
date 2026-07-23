"""Canonical thesis knowledge parsing tests."""

from pathlib import Path

from app.services.workspace.thesis_knowledge import (
    load_companion_resume,
    load_progress_summary,
    load_project_identity,
)


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_progress_drives_companion_resume(tmp_path, monkeypatch):
    monkeypatch.setenv("THESIS_AGENT_KNOWLEDGE_ROOT", str(tmp_path))
    _write(
        tmp_path,
        "03_PROJECT/Progress.md",
        """# Progress

**Run migrazione:** `kimi-claw-2026-07-13`

## Riepilogo

| Area | Sezioni | Stato |
|------|---------|-------|
| Capitolo 1 | §1.1–§1.3 | Congelato |
| Capitolo 3 | §3.1–§3.6 | §3.6 in bozza |

## Stato Capitolo 3

| Sezione | Titolo | Parole runtime | Stato |
|---------|--------|----------------|-------|
| 3.6 | Sintesi: il capo come costruzione di senso | 177 | draft |

## Prossimo passo operativo

1. Revisionare e completare §3.6.
2. Congelare il Capitolo 3.
""",
    )
    _write(
        tmp_path,
        "chapters/ch03/3.6_Sintesi_costruzione_di_significato.md",
        "# 3.6 Sintesi: il capo come costruzione di senso\n\nTesto reale.",
    )

    resume = load_companion_resume()

    assert resume.focus_section == "§3.6"
    assert resume.focus_status == "draft"
    assert resume.next_action == "Revisionare e completare §3.6."
    assert resume.section_text and "Testo reale" in resume.section_text
    assert load_progress_summary() == (
        "Capitolo 1: Congelato · Capitolo 3: §3.6 in bozza"
    )


def test_identity_comes_from_thesis_state(tmp_path, monkeypatch):
    monkeypatch.setenv("THESIS_AGENT_KNOWLEDGE_ROOT", str(tmp_path))
    _write(
        tmp_path,
        "03_PROJECT/Thesis-State.md",
        """# Thesis State

- **Titolo:** *Prima dei dieci minuti. Il processo creativo nel fashion design.*
- **Autrice:** Ilaria Marelli — triennale Fashion Design, **Accademia del Lusso, Milano**.
""",
    )

    identity = load_project_identity()

    assert identity.title == (
        "Prima dei dieci minuti. Il processo creativo nel fashion design."
    )
    assert identity.author == "Ilaria Marelli"
    assert identity.institution == "Accademia del Lusso, Milano"
