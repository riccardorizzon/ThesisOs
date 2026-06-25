"""DocumentService domain errors (M3). Mirrors the MemoryService error model."""

from __future__ import annotations


class DocumentServiceError(Exception):
    """Base error for DocumentService domain failures."""


class DocumentNotFoundError(DocumentServiceError):
    def __init__(self, document_id: str):
        self.document_id = document_id
        super().__init__(f"document not found: {document_id}")


class DocumentWriteConflictError(DocumentServiceError):
    """Optimistic lock failure on metadata PATCH — maps to 409 write_conflict."""

    def __init__(self, document_id: str, *, expected_version: int, actual_version: int):
        self.document_id = document_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"write_conflict: document {document_id} expected version {expected_version}, "
            f"actual {actual_version}"
        )


class UnsupportedFormatError(DocumentServiceError):
    """Source type is not one of pdf/epub/docx — maps to 400 unsupported_format."""

    def __init__(self, source_type: str | None):
        self.source_type = source_type
        super().__init__(f"unsupported_format: {source_type!r}")


class ParserUnavailableError(DocumentServiceError):
    """A parser backend (docling/pymupdf) is not installed in this environment."""

    def __init__(self, parser: str):
        self.parser = parser
        super().__init__(f"parser_unavailable: {parser}")


class ParseError(DocumentServiceError):
    """A parser failed to extract usable text — maps to 422 parse_failed."""
