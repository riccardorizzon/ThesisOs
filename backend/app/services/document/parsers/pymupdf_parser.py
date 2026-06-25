"""PyMuPDF parser — subordinate PDF-only fallback (spec §12).

Invoked only when Docling fails or returns no text for a PDF. Forbidden for
docx/epub (`forbidden_for: [docx, epub]`). Plain-text extraction with fixed-size
windowed chunking.
"""

from __future__ import annotations

from app.services.document.chunking import sliding_window_chunks
from app.services.document.exceptions import ParseError, ParserUnavailableError
from app.services.document.parsers.base import ParsedChunk, ParseResult


class PyMuPDFParser:
    name = "pymupdf"

    def parse(self, data: bytes, source_type: str) -> ParseResult:
        if source_type != "pdf":
            raise ParseError(f"pymupdf is PDF-only, refused {source_type}")
        try:
            import fitz  # PyMuPDF, lazy import
        except ImportError as exc:  # pragma: no cover - env without pymupdf
            raise ParserUnavailableError("pymupdf") from exc

        try:
            doc = fitz.open(stream=data, filetype="pdf")
        except Exception as exc:
            raise ParseError(f"pymupdf could not open PDF: {exc}") from exc

        page_count = doc.page_count
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        chunks = [ParsedChunk(content=piece) for piece in sliding_window_chunks(text)]
        return ParseResult(parser=self.name, chunks=chunks, page_count=page_count)
