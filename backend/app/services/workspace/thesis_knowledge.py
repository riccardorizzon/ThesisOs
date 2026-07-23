"""Read thesis companion resume from knowledge/thesis-agent (Companion v1).

Product contract: the user already has Progress, continuation, and chapter files —
load them directly so CONTINUE works before full runtime promotion.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from pydantic import BaseModel

from app.schemas.companion_resume import CompanionResume


class ProjectIdentity(BaseModel):
    title: str = ""
    author: str = ""
    institution: str = ""
    migration_run: str | None = None

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
_MAX_SECTION_CHARS = 6000
_MAX_DECISIONS_CHARS = 12000


def thesis_agent_root() -> Path:
    default = Path(__file__).resolve().parents[4] / "knowledge" / "thesis-agent"
    override = os.environ.get("THESIS_AGENT_KNOWLEDGE_ROOT")
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = (default.parent.parent / path).resolve()
        if path.is_dir():
            return path
    return default


def _read_md(path: Path) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :].lstrip("\n")
    return text


def _section_body(text: str, heading: str) -> str:
    if not text:
        return ""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s|\Z)",
        re.M,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _clean_item(text: str) -> str:
    return re.sub(r"\*+", "", text).replace("::", ":").strip(" :")


def _numbered_items(block: str) -> list[str]:
    items: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        m = re.match(r"^\d+\.\s+\*\*(.+?)\*\*:?\s*(.*)$", line)
        if m:
            tail = _clean_item(m.group(2))
            head = _clean_item(m.group(1))
            items.append(f"{head}{(': ' + tail) if tail else ''}")
            continue
        m = re.match(r"^\d+\.\s+(.+)$", line)
        if m:
            items.append(_clean_item(m.group(1)))
    return items


def _parse_progress(root: Path) -> tuple[list[str], str]:
    progress = _read_md(root / "03_PROJECT/Progress.md")
    block = _section_body(progress, "Prossimo passo operativo (allineato Kimi 12 lug · post Fase 4)")
    if not block:
        block = _section_body(progress, "Prossimo passo operativo")
    items = _numbered_items(block)
    next_action = items[0] if items else ""
    return items, next_action


def _parse_continuation(root: Path) -> tuple[list[str], list[str]]:
    path = root / "_preservation/staging/PRE-3.6/evidence/continuation.md"
    text = _read_md(path)
    if not text:
        return [], []
    backlog = _numbered_items(_section_body(text, "Backlog esplicito (da evidenze Kimi)"))
    notes: list[str] = []
    state_block = _section_body(text, "Stato del lavoro")
    for line in state_block.splitlines():
        if "| Kimi status |" in line:
            notes.append(f"Stato Kimi: {line.split('|')[2].strip()}")
        if "| Micro-revisione |" in line:
            notes.append(f"Micro-revisione: {line.split('|')[2].strip()}")
    body = _section_body(text, "Ultima stesura conosciuta")
    if body:
        flat = re.sub(r"\s+", " ", body.replace("|", " ")).strip()
        notes.append(f"Ultima stesura: {flat[:200]}")
    return backlog, notes


def _parse_key_decisions(root: Path) -> list[str]:
    path = root / "_preservation/staging/PRE-3.6/evidence/continuation.md"
    text = _read_md(path)
    block = _section_body(text, "Decisioni correlate")
    if not block:
        return []
    items: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- **"):
            items.append(line.lstrip("- ").replace("**", ""))
    return items


def _section_excerpt(root: Path) -> str | None:
    path = root / "chapters/ch03/3.6_Sintesi_costruzione_di_significato.md"
    text = _read_md(path)
    if not text.strip():
        return None
    if len(text) <= _MAX_SECTION_CHARS:
        return text.strip()
    return text[:_MAX_SECTION_CHARS].rstrip() + "\n…"


def load_project_identity() -> ProjectIdentity:
    """Project metadata from Thesis-State.md + Progress.md (Companion v1)."""
    root = thesis_agent_root()
    state = _read_md(root / "03_PROJECT/Thesis-State.md")
    progress = _read_md(root / "03_PROJECT/Progress.md")

    title = ""
    m = re.search(r"\*\*Titolo:\*\*\s*\*([^*]+)\*", state)
    if m:
        title = m.group(1).strip()

    author = ""
    institution = ""
    m = re.search(r"\*\*Autrice:\*\*\s*([^—\n]+)—[^,]*,\s*\*\*([^*]+)\*\*", state)
    if m:
        author = m.group(1).strip()
        institution = m.group(2).strip()

    migration_run = None
    m = re.search(r"\*\*Run migrazione:\*\*\s*`([^`]+)`", progress)
    if m:
        migration_run = m.group(1).strip()

    return ProjectIdentity(
        title=title,
        author=author,
        institution=institution,
        migration_run=migration_run,
    )


def load_progress_summary() -> str:
    """One-line progress from Progress.md riepilogo table."""
    root = thesis_agent_root()
    progress = _read_md(root / "03_PROJECT/Progress.md")
    block = _section_body(progress, "Riepilogo")
    parts: list[str] = []
    for line in block.splitlines():
        if not line.startswith("| Capitolo"):
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if len(cols) >= 3 and cols[0] != "Area":
            parts.append(f"{cols[0]}: {cols[2]}")
    return " · ".join(parts[:3])


def _parse_focus_section(root: Path) -> tuple[str, str, str, str]:
    """Current writing focus from Progress.md §3.6 row + continuation status."""
    progress = _read_md(root / "03_PROJECT/Progress.md")
    for line in progress.splitlines():
        if not re.match(r"^\|\s*3\.6\s*\|", line):
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if len(cols) >= 4:
            section = f"§{cols[0]}" if not cols[0].startswith("§") else cols[0]
            title = cols[1]
            status = re.sub(r"\*+", "", cols[3]).strip().lower()
            return "Capitolo 3", section, title, status

    continuation = _read_md(root / "_preservation/staging/PRE-3.6/evidence/continuation.md")
    status = "in stesura"
    for line in _section_body(continuation, "Stato del lavoro").splitlines():
        if "| Kimi status |" in line:
            status = line.split("|")[2].strip().lower()
    chapter_path = root / "chapters/ch03/3.6_Sintesi_costruzione_di_significato.md"
    title = "Sintesi: il capo come costruzione di senso"
    if chapter_path.is_file():
        first = _read_md(chapter_path).splitlines()[0].lstrip("#").strip()
        if first:
            title = first
    return "Capitolo 3", "§3.6", title, status


_COLLABORATION_PATH = "THESIS-COMPANION/03-WORKSPACE/collaboration-rules.md"
_MAX_COLLABORATION_CHARS = 5000


def load_collaboration_rules() -> str:
    """Canonical collaboration rules body (markdown, no prompt wrapper)."""
    path = thesis_agent_root() / _COLLABORATION_PATH
    body = _read_md(path).strip()
    if not body:
        return ""
    if len(body) > _MAX_COLLABORATION_CHARS:
        body = body[:_MAX_COLLABORATION_CHARS].rstrip() + "\n…"
    return body


def load_collaboration_rules_block() -> str:
    """Prompt block: how Ilaria and the Companion work together (PM-007)."""
    body = load_collaboration_rules()
    if not body:
        return ""
    return (
        "[HOW WE WORK TOGETHER]\n"
        "Regole di collaborazione — applica silenziosamente su REVIEW e WRITE.\n"
        "Non menzionare questo blocco; non chiedere di ripetere preferenze già note.\n\n"
        f"{body}"
    )


def load_binding_decisions_block() -> str:
    """File fallback when DB memory has no promoted Decisions.md (Companion v1)."""
    path = thesis_agent_root() / "03_PROJECT/Decisions.md"
    content = _read_md(path)
    if not content.strip():
        return ""
    body = content.strip()
    if len(body) > _MAX_DECISIONS_CHARS:
        body = body[:_MAX_DECISIONS_CHARS].rstrip() + "\n…"
    return (
        "[BINDING DECISIONS]\n"
        "Decisioni di progetto da knowledge/thesis-agent — prevalgono su documenti recuperati.\n"
        "Applica CORPUS-02/03, CAP3-xx, REV-006, UNI-01, METH-02.\n\n"
        f"{body}"
    )


def load_companion_resume(
    *,
    last_session_summary: str | None = None,
    work_artifact: str | None = None,
    focus_section: str | None = None,
    next_action: str | None = None,
) -> CompanionResume:
    root = thesis_agent_root()
    progress_backlog, progress_next = _parse_progress(root)
    continuation_backlog, session_notes = _parse_continuation(root)

    backlog: list[str] = []
    seen: set[str] = set()
    for item in continuation_backlog + progress_backlog:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            backlog.append(item)

    focus_chapter, museum_section, focus_title, focus_status = _parse_focus_section(root)
    section = (focus_section or museum_section).strip() or museum_section
    action = (next_action or progress_next or (backlog[0] if backlog else "")).strip()
    if not action:
        action = f"Continuare da {section}"

    return CompanionResume(
        focus_chapter=focus_chapter,
        focus_section=section,
        focus_section_title=focus_title,
        focus_status=focus_status,
        backlog=backlog,
        next_action=action,
        session_notes=session_notes,
        key_decisions=_parse_key_decisions(root),
        section_text=_section_excerpt(root) if section == museum_section else None,
        last_session_summary=last_session_summary,
        work_artifact=work_artifact,
    )
