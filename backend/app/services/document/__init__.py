"""Document ingestion service package (M3)."""

from app.services.document.exceptions import (
    DocumentNotFoundError,
    DocumentServiceError,
    DocumentWriteConflictError,
    ParseError,
    ParserUnavailableError,
    UnsupportedFormatError,
)
from app.services.document.service import DocumentService

__all__ = [
    "DocumentService",
    "DocumentServiceError",
    "DocumentNotFoundError",
    "DocumentWriteConflictError",
    "UnsupportedFormatError",
    "ParseError",
    "ParserUnavailableError",
]
