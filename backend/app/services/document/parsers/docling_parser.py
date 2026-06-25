"""Docling parser — primary for PDF/DOCX/EPUB (spec §12).

Docling is imported lazily and written to a temp file because its converter works
on paths. If the library is absent we raise ParserUnavailableError so the package
still imports in environments (e.g. CI) without the heavy dependency installed.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from app.services.document.chunking import sliding_window_chunks
from app.services.document.exceptions import ParseError, ParserUnavailableError
from app.services.document.parsers.base import ParsedChunk, ParseResult

_EXT = {"pdf": ".pdf", "docx": ".docx", "epub": ".epub"}


def _chunks_from_markdown(markdown: str) -> list[ParsedChunk]:
    """Split exported markdown on headings; window long sections (spec §5.1)."""
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


class DoclingParser:
    name = "docling"

    def parse(self, data: bytes, source_type: str) -> ParseResult:
        try:
            from docling.document_converter import DocumentConverter  # lazy import
        except ImportError as exc:  # pragma: no cover - env without docling
            raise ParserUnavailableError("docling") from exc

        suffix = _EXT.get(source_type, "")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            try:
                result = DocumentConverter().convert(Path(tmp.name))
                markdown = result.document.export_to_markdown()
            except Exception as exc:  # docling raises a variety of errors
                raise ParseError(f"docling failed for {source_type}: {exc}") from exc

        chunks = _chunks_from_markdown(markdown or "")
        return ParseResult(parser=self.name, chunks=chunks)
