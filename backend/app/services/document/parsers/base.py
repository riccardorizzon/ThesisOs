"""Parser boundary contracts (M3, spec §12).

A `Parser` turns raw bytes into a `ParseResult` of ordered `ParsedChunk`s plus
best-effort metadata. Docling is primary; PyMuPDF is the PDF-only fallback. The
two are NOT equal (`both_equal: false`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


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
