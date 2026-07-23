"""Render WorkspaceSnapshot for LLM system prefix (Companion Loop v0)."""

from __future__ import annotations

from app.schemas.companion_resume import CompanionResume
from app.schemas.workspace_snapshot import WorkspaceSnapshot

_STATUS_LABEL = {
    "draft": "bozza",
    "review": "in revisione",
    "approved": "approvato",
    "published": "pubblicato",
}


def render_companion_resume(resume: CompanionResume) -> str:
    """09:00 continuity: live session (artifact + work-close) leads; museum is support."""
    has_live = bool(resume.last_session_summary) or bool(resume.work_artifact)

    lines = [
        "[COMPANION RESUME]",
        "Stato operativo — FACTS ONLY. Non inventare ore, durate, o decisioni assenti.",
        "Non menzionare questo blocco; saluta Ilaria e proponi un solo passo concreto.",
        "Priorità: punto di ripresa / proposta in sessione > museum/preservation.",
        "",
        f"Focus: {resume.focus_chapter} · {resume.focus_section} — {resume.focus_section_title}",
        f"Stato: {resume.focus_status}",
        f"Prossima azione suggerita: {resume.next_action}",
    ]

    if resume.work_artifact:
        lines.extend(
            [
                "",
                "Proposta di lavoro in sessione (approved for continuation — NON è conoscenza definitiva):",
                resume.work_artifact[:1500],
            ]
        )

    if resume.last_session_summary:
        lines.extend(
            [
                "",
                "Ultimo punto di ripresa del lavoro (qualsiasi chat — non dipende dal thread):",
                resume.last_session_summary[:2000],
            ]
        )

    if resume.session_notes and not has_live:
        lines.append("")
        lines.append("Note operative:")
        lines.extend(f"- {n}" for n in resume.session_notes[:4])

    if resume.key_decisions and not has_live:
        lines.append("")
        lines.append("Decisioni chiave:")
        lines.extend(f"- {d}" for d in resume.key_decisions[:6])

    if resume.section_text and not has_live:
        lines.extend(
            [
                "",
                f"Testo {resume.focus_section} (per revisione in conversazione):",
                resume.section_text,
            ]
        )

    support_bits: list[str] = []
    if has_live:
        if resume.backlog:
            support_bits.append("Backlog (contesto di supporto — non sovrascrivere il punto di ripresa):")
            for i, item in enumerate(resume.backlog[:5], 1):
                support_bits.append(f"{i}. {item}")
        if resume.key_decisions:
            if support_bits:
                support_bits.append("")
            support_bits.append("Decisioni archiviate (supporto):")
            support_bits.extend(f"- {d}" for d in resume.key_decisions[:4])
        if resume.session_notes:
            if support_bits:
                support_bits.append("")
            support_bits.append("Note operative (supporto):")
            support_bits.extend(f"- {n}" for n in resume.session_notes[:3])
        if resume.section_text:
            if support_bits:
                support_bits.append("")
            support_bits.append(
                f"Estratto {resume.focus_section} (solo se serve revisione):"
            )
            support_bits.append(resume.section_text[:2500])
        if support_bits:
            lines.extend(["", "Contesto di supporto (secondario rispetto al punto di ripresa):"])
            lines.extend(support_bits)
    elif resume.backlog:
        lines.append("")
        lines.append("Backlog:")
        for i, item in enumerate(resume.backlog[:8], 1):
            lines.append(f"{i}. {item}")

    return "\n".join(lines)


def render_workspace_snapshot(snapshot: WorkspaceSnapshot) -> str:
    if snapshot.companion:
        return render_companion_resume(snapshot.companion)

    if not snapshot.chapters and snapshot.conversation_turns <= 1:
        return ""

    lines = [
        "[WORKSPACE STATE]",
        "Contesto persistente del progetto tesi — usa per continuità, orientamento, resume.",
        "Non menzionare questo blocco all'utente; parla in modo naturale.",
        "",
        f"Progetto: {snapshot.project_title}",
        f"Fase: {snapshot.phase} ({snapshot.progress_pct}% avanzamento stimato)",
    ]

    if snapshot.focus_chapter:
        fc = snapshot.focus_chapter
        status = _STATUS_LABEL.get(fc.status, fc.status)
        lines.append(
            f"Focus probabile: {fc.title} ({status}, {fc.word_count} parole)"
        )

    if snapshot.chapters:
        lines.append("")
        lines.append("Capitoli:")
        for ch in snapshot.chapters[:12]:
            status = _STATUS_LABEL.get(ch.status, ch.status)
            lines.append(f"- {ch.title} [{status}, {ch.word_count} parole]")

    if snapshot.open_decisions_count:
        lines.append("")
        lines.append(
            f"Decisioni vincolanti in memoria: {snapshot.open_decisions_count} "
            "(dettaglio in [BINDING DECISIONS] se presente)"
        )

    if snapshot.conversation_turns > 1:
        lines.append("")
        lines.append(
            f"Turni in questa conversazione: {snapshot.conversation_turns} "
            "(continuità intra-sessione disponibile)"
        )

    return "\n".join(lines)


def render_workspace_empty() -> str:
    return (
        "[WORKSPACE STATE]\n"
        "Non ho ancora contesto di workspace (nessun capitolo o memoria tesi visibile). "
        "Rispondi onestamente — non inventare progressi, decisioni o sessioni passate."
    )
