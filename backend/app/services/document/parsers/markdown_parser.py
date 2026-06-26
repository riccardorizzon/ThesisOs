"""Native markdown / plain-text parser (M4 recovery, P4).

Reuses the shared markdown chunker so `.md`/`.txt` ingest into the same canonical
chunk representation as PDF/DOCX/EPUB — no duplicate ingestion logic. Pure-python,
so it needs no Docling and has no fallback.
"""

from __future__ import annotations

from app.services.document.chunking import sliding_window_chunks
from app.services.document.exceptions import ParseError
from app.services.document.parsers.base import (
    ParsedChunk,
    ParseResult,
    markdown_to_chunks,
)


class MarkdownParser:
    name = "markdown"

    def parse(self, data: bytes, source_type: str) -> ParseResult:
        text = data.decode("utf-8", errors="replace")
        if source_type == "text":
            chunks = [ParsedChunk(content=piece) for piece in sliding_window_chunks(text)]
        else:  # markdown
            chunks = markdown_to_chunks(text)
        if not chunks:
            raise ParseError(f"{source_type} produced no usable text")
        return ParseResult(parser=self.name, chunks=chunks)
