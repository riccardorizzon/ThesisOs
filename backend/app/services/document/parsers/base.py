"""Parser boundary contracts (M3, spec §12).

A `Parser` turns raw bytes into a `ParseResult` of ordered `ParsedChunk`s plus
best-effort metadata. Docling is primary; PyMuPDF is the PDF-only fallback. The
two are NOT equal (`both_equal: false`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.services.document.chunking import sliding_window_chunks


@dataclass
class ParsedChunk:
    content: str
    page_from: int | None = None
    page_to: int | None = None
    section_path: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ParseResult:
    parser: str
    chunks: list[ParsedChunk]
    title: str | None = None
    author: str | None = None
    page_count: int | None = None
    language: str | None = None


class Parser(Protocol):
    name: str

    def parse(self, data: bytes, source_type: str) -> ParseResult: ...


def markdown_to_chunks(markdown: str) -> list[ParsedChunk]:
    """Split markdown on headings, then window long sections (spec §5.1).

    Single source of chunking for both the Docling export path and the native
    markdown parser — keeps ingestion logic un-duplicated (M4 recovery, P4).
    """
    chunks: list[ParsedChunk] = []
    section = "Document"
    buffer: list[str] = []

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if not body:
            return
        for piece in sliding_window_chunks(body):
            chunks.append(ParsedChunk(content=piece, section_path=section))

    for line in markdown.splitlines():
        if line.lstrip().startswith("#"):
            flush()
            buffer = []
            section = line.lstrip("#").strip() or section
        else:
            buffer.append(line)
    flush()
    return chunks
