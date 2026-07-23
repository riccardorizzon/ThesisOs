"""In-memory MemoryService double for the persistence contract (ADR-0046)."""

from __future__ import annotations

from types import SimpleNamespace

from app.schemas.memory import (
    MemoryCreate,
    MemoryListFilters,
    MemoryUpdate,
    PromptContext,
)


class FakeMemoryService:
    """Supports list/create/update + load_prompt_context; can simulate write failures."""

    def __init__(
        self,
        *,
        fail_writes: bool = False,
        prompt_context: PromptContext | None = None,
    ) -> None:
        self.rows: list[SimpleNamespace] = []
        self.fail_writes = fail_writes
        self.prompt_context = prompt_context or PromptContext()
        self._next_id = 1

    async def load_prompt_context(self, **kwargs) -> PromptContext:
        return self.prompt_context

    async def list(self, filters: MemoryListFilters) -> list[SimpleNamespace]:
        rows = [
            row
            for row in self.rows
            if (filters.kind is None or row.kind == filters.kind)
            and (filters.key is None or row.key == filters.key)
        ]
        return rows[: filters.limit]

    async def create(self, payload: MemoryCreate) -> SimpleNamespace:
        if self.fail_writes:
            raise RuntimeError("db unavailable")
        row = SimpleNamespace(
            id=str(self._next_id),
            version=1,
            kind=payload.kind,
            key=payload.key,
            title=payload.title,
            content=payload.content,
        )
        self._next_id += 1
        self.rows.append(row)
        return row

    async def update(self, row_id: str, payload: MemoryUpdate) -> SimpleNamespace:
        if self.fail_writes:
            raise RuntimeError("db unavailable")
        for row in self.rows:
            if row.id == row_id:
                if payload.content is not None:
                    row.content = payload.content
                if payload.title is not None:
                    row.title = payload.title
                row.version += 1
                return row
        raise KeyError(row_id)

    def row(self, key: str) -> SimpleNamespace | None:
        return next((row for row in self.rows if row.key == key), None)
