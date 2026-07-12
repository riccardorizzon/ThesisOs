"""ChapterService domain errors (M6). Mirrors the DocumentService error model."""

from __future__ import annotations


class ChapterServiceError(Exception):
    """Base error for ChapterService domain failures."""


class ChapterNotFoundError(ChapterServiceError):
    def __init__(self, chapter_id: str):
        self.chapter_id = chapter_id
        super().__init__(f"chapter not found: {chapter_id}")


class ChapterWriteConflictError(ChapterServiceError):
    """Optimistic lock failure on a chapter write — maps to 409 write_conflict."""

    def __init__(self, chapter_id: str, *, expected_version: int, actual_version: int):
        self.chapter_id = chapter_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"write_conflict: chapter {chapter_id} expected version {expected_version}, "
            f"actual {actual_version}"
        )


class InvalidChapterStatusError(ChapterServiceError):
    """Status not in the frozen lifecycle (ADR-0032 §3) — maps to 422."""

    def __init__(self, status: str):
        self.status = status
        super().__init__(f"invalid_status: {status!r}")


class ChapterNotDeletableError(ChapterServiceError):
    """Chapter is seeded or has dependents — maps to 403."""

    def __init__(self, chapter_id: str):
        self.chapter_id = chapter_id
        super().__init__(f"chapter_not_deletable: {chapter_id}")
