"""Manuscript reading/export order — mirrors frontend/lib/manuscriptToc.ts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Protocol

TAG_PREFIX_RE = re.compile(r"^\[[^\]]+\]\s*")
SECTION_TITLE_RE = re.compile(r"^§\s*(\d+)\.(\d+)\s*(.+)$")
CHAPTER_TITLE_RE = re.compile(r"^Cap\.?\s*(\d+)\s*[—–-]\s*(.+)$", re.IGNORECASE)
NOISE_TITLE_RE = re.compile(r"^(G5 |E2E |M7 dogfood|prova$|Craftsmanship$)", re.IGNORECASE)


class ChapterLike(Protocol):
    id: str
    title: str
    order_index: int
    word_count: int
    content_md: str | None


ParsedKind = Literal["chapter", "section", "other"]


@dataclass(frozen=True)
class ParsedTitle:
    kind: ParsedKind
    major: int = 0
    minor: int = 0
    label: str = ""


def strip_manuscript_tag(title: str) -> str:
    return TAG_PREFIX_RE.sub("", title).strip()


def parse_manuscript_title(title: str) -> ParsedTitle:
    stripped = strip_manuscript_tag(title)
    section = SECTION_TITLE_RE.match(stripped)
    if section:
        return ParsedTitle(
            kind="section",
            major=int(section.group(1)),
            minor=int(section.group(2)),
            label=section.group(3).strip(),
        )
    chapter = CHAPTER_TITLE_RE.match(stripped)
    if chapter:
        return ParsedTitle(
            kind="chapter",
            major=int(chapter.group(1)),
            label=chapter.group(2).strip(),
        )
    return ParsedTitle(kind="other", label=stripped)


def is_manuscript_noise_title(title: str) -> bool:
    return bool(NOISE_TITLE_RE.match(strip_manuscript_tag(title)))


def dedupe_manuscript_chapters[T: ChapterLike](chapters: list[T]) -> list[T]:
    by_title: dict[str, T] = {}
    for chapter in chapters:
        if is_manuscript_noise_title(chapter.title):
            continue
        key = strip_manuscript_tag(chapter.title).lower()
        existing = by_title.get(key)
        if existing is None or chapter.word_count > existing.word_count:
            by_title[key] = chapter
    return list(by_title.values())


def _sort_tuple(chapter: ChapterLike) -> tuple[int, int, int]:
    parsed = parse_manuscript_title(chapter.title)
    if parsed.kind == "chapter":
        return (parsed.major, 0, 0)
    if parsed.kind == "section":
        return (parsed.major, parsed.minor, 1)
    return (10_000, chapter.order_index, 2)


def manuscript_export_order[T: ChapterLike](chapters: list[T]) -> list[T]:
    """Cap. N headers, then §N.x, then other titles — same as Manoscritto flatten."""
    entries = dedupe_manuscript_chapters(chapters)
    structured = [c for c in entries if parse_manuscript_title(c.title).kind != "other"]
    others = [c for c in entries if parse_manuscript_title(c.title).kind == "other"]
    structured.sort(key=_sort_tuple)
    others.sort(key=lambda c: c.order_index)
    return [*structured, *others]


def render_manuscript_markdown(chapters: list[ChapterLike]) -> str:
    ordered = manuscript_export_order(chapters)
    if not ordered:
        return "# Manoscritto\n"
    parts: list[str] = []
    for chapter in ordered:
        body = (chapter.content_md or "").rstrip()
        parts.append(f"# {chapter.title}\n\n{body}\n")
    return "\n---\n\n".join(parts) + "\n"
