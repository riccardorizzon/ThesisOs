"""Parser orchestration boundary (spec §12).

Authority order is fixed: Docling is primary for pdf/docx/epub; PyMuPDF is a
PDF-only fallback, used only when Docling raises or returns zero text. docx/epub
have NO fallback — failure becomes a ParseError (→ status=failed).

Parsers are injectable so the boundary logic is unit-testable without the heavy
docling/pymupdf dependencies installed.
"""

from __future__ import annotations

from app.schemas.document import VALID_SOURCE_TYPES
from app.services.document.exceptions import (
    ParseError,
    ParserUnavailableError,
    UnsupportedFormatError,
)
from app.services.document.parsers.base import ParsedChunk, ParseResult, Parser

__all__ = ["ParsedChunk", "ParseResult", "Parser", "parse_document"]


def parse_document(
    source_type: str,
    data: bytes,
    *,
    primary: Parser | None = None,
    fallback: Parser | None = None,
) -> ParseResult:
    """Run the Docling-primary / PyMuPDF-fallback boundary for one document."""
    source_type = (source_type or "").lower()
    if source_type not in VALID_SOURCE_TYPES:
        raise UnsupportedFormatError(source_type)

    if primary is None:
        from app.services.document.parsers.docling_parser import DoclingParser

        primary = DoclingParser()

    primary_error: Exception | None = None
    result: ParseResult | None = None
    try:
        result = primary.parse(data, source_type)
    except (ParseError, ParserUnavailableError) as exc:
        primary_error = exc
        result = None

    if result is not None and result.chunks:
        return result

    # Fallback path is PDF-only.
    if source_type == "pdf":
        if fallback is None:
            from app.services.document.parsers.pymupdf_parser import PyMuPDFParser

            fallback = PyMuPDFParser()
        return fallback.parse(data, source_type)

    # docx / epub: no fallback.
    if result is not None:  # parsed but produced zero chunks
        raise ParseError(f"primary parser produced no text for {source_type}")
    raise primary_error if primary_error is not None else ParseError(source_type)
