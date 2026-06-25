"""Heading-aware markdown and YAML chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass

HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
MIN_CHUNK_CHARS = 80


@dataclass(frozen=True)
class ChunkDraft:
    content: str
    title: str
    heading_path: str


def chunk_markdown(text: str, *, fallback_title: str) -> list[ChunkDraft]:
    """Split markdown on ## headings; keep heading breadcrumb in each chunk."""
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        body = text.strip()
        if len(body) < MIN_CHUNK_CHARS:
            return []
        return [ChunkDraft(content=body, title=fallback_title, heading_path=fallback_title)]

    chunks: list[ChunkDraft] = []
    preamble = text[: matches[0].start()].strip()
    if len(preamble) >= MIN_CHUNK_CHARS:
        chunks.append(ChunkDraft(content=preamble, title=fallback_title, heading_path=fallback_title))

    for i, match in enumerate(matches):
        level = len(match.group(1))
        if level > 3:
            continue
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if len(section) < MIN_CHUNK_CHARS:
            continue
        heading = match.group(2).strip()
        chunks.append(ChunkDraft(content=section, title=heading, heading_path=heading))

    if not chunks and text.strip():
        return [ChunkDraft(content=text.strip(), title=fallback_title, heading_path=fallback_title)]
    return chunks


def chunk_yaml(text: str, *, fallback_title: str) -> list[ChunkDraft]:
    """YAML files are indexed as a single chunk (STATE.yaml etc.)."""
    body = text.strip()
    if not body:
        return []
    return [ChunkDraft(content=body, title=fallback_title, heading_path=fallback_title)]


def chunk_file(rel_path: str, text: str) -> list[ChunkDraft]:
    title = rel_path.rsplit("/", 1)[-1]
    if rel_path.endswith((".md", ".markdown")):
        return chunk_markdown(text, fallback_title=title)
    if rel_path.endswith((".yaml", ".yml")):
        return chunk_yaml(text, fallback_title=title)
    if rel_path.endswith((".json", ".sql", ".yaml")):
        body = text.strip()
        if len(body) < MIN_CHUNK_CHARS:
            return []
        return [ChunkDraft(content=body[:8000], title=title, heading_path=title)]
    body = text.strip()
    if len(body) < MIN_CHUNK_CHARS:
        return []
    return [ChunkDraft(content=body[:8000], title=title, heading_path=title)]
