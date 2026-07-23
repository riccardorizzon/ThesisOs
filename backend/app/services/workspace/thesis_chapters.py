"""Ensure migrated thesis outline chapters exist in runtime DB (CUR-8)."""

from __future__ import annotations

import re
from app.services.chapter import ChapterService
from app.schemas.chapter import ChapterCreate, ChapterListFilters
from app.services.workspace.thesis_knowledge import thesis_agent_root

_FRONTMATTER_RE = re.compile(r"^---\n[\s\S]*?\n---\n*", re.M)
_svc = ChapterService()

# (relative path under knowledge/thesis-agent, display title, order_index, status)
_CH03_SEEDS: list[tuple[str, str, int, str]] = [
    ("chapters/ch03/3.1_La_palette.md", "§3.1 La palette", 31, "review"),
    ("chapters/ch03/3.2_La_silhouette.md", "§3.2 La silhouette", 32, "review"),
    ("chapters/ch03/3.3_Sistema_di_segni.md", "§3.3 Sistema di segni", 33, "review"),
    (
        "chapters/ch03/3.4_Norma_deviazione_mediazione.md",
        "§3.4 Norma, deviazione, mediazione",
        34,
        "review",
    ),
    ("chapters/ch03/3.5_Estetica_del_difetto.md", "§3.5 Estetica del difetto", 35, "review"),
    (
        "chapters/ch03/3.6_Sintesi_costruzione_di_significato.md",
        "§3.6 Sintesi: il capo come costruzione di senso",
        36,
        "draft",
    ),
]


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text, count=1).strip()


def _title_matches_section(title: str, section_code: str) -> bool:
    t = title.lower()
    code = section_code.lower().lstrip("§")
    return code in t or f"§{code}" in t or f" {code} " in f" {t} "


async def ensure_thesis_outline_chapters() -> str | None:
    """Idempotently promote Cap.3 §3.1–§3.6 into chapters. Returns §3.6 id if present."""
    root = thesis_agent_root()
    focus_id: str | None = None

    existing = await _svc.list(ChapterListFilters(scope="owned", limit=500))
    by_needle: dict[str, str] = {}
    for ch in existing:
        for _, title, _, _ in _CH03_SEEDS:
            code = title.split()[0]  # §3.x
            if _title_matches_section(ch.title, code):
                by_needle[code] = ch.id
                if code == "§3.6":
                    focus_id = ch.id

    for rel, title, order_index, status in _CH03_SEEDS:
        code = title.split()[0]
        if code in by_needle:
            if code == "§3.6":
                focus_id = by_needle[code]
            continue
        path = root / rel
        if not path.is_file():
            continue
        body = _strip_frontmatter(path.read_text(encoding="utf-8"))
        display = f"[kimi-claw-2026-07-13] {title}"
        rec = await _svc.create(
            ChapterCreate(
                title=display,
                parent_id=None,
                order_index=order_index,
                status=status,
                content_md=body,
                summary=title,
            )
        )
        by_needle[code] = rec.id
        if code == "§3.6":
            focus_id = rec.id

    return focus_id


async def resolve_focus_chapter_id(focus_section: str = "§3.6") -> str | None:
    """Return chapter id for resume focus, ensuring outline seeds first."""
    focus_id = await ensure_thesis_outline_chapters()
    if focus_id:
        return focus_id
    existing = await _svc.list(ChapterListFilters(scope="owned", limit=500))
    needle = focus_section.lower()
    for ch in existing:
        if needle in ch.title.lower() or needle.lstrip("§") in ch.title.lower():
            return ch.id
    return None
