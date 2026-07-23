"""MemoryService — sole write port for the memories domain (ADR-0015).

All DB mutations on ``memories`` and ``memory_versions`` MUST go through this
module. API handlers, graph nodes, and future agents call MemoryService only.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.db.session_async import AsyncSessionLocal
from app.schemas.graph_state import MemoryOp
from app.schemas.memory import (
    BINDING_DECISION_KEY,
    CANONICAL_KEYS,
    SINGLETON_KINDS,
    VALID_KINDS,
    MemoryCreate,
    MemoryListFilters,
    MemoryRecord,
    MemoryUpdate,
    MemoryVersionRecord,
    PromptContext,
    PromptContextFilters,
    PromptMemoryItem,
)
from app.services.memory.exceptions import (
    CannotDeleteSingletonError,
    MemoryNotFoundError,
    SingletonMemoryExistsError,
    WriteConflictError,
)
from app.services.project_scope import resolve_project_id

_CHARS_PER_TOKEN_ESTIMATE = 4


class MemoryService:
    """Single write/read service for operational and knowledge memory rows."""

    # ------------------------------------------------------------------
    # Public API — optional injected session for tests; otherwise self-contained
    # ------------------------------------------------------------------

    async def create(
        self,
        data: MemoryCreate,
        *,
        session: AsyncSession | None = None,
    ) -> MemoryRecord:
        if session is not None:
            return await self._create(session, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._create(s, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def get(self, memory_id: str, *, session: AsyncSession | None = None) -> MemoryRecord:
        if session is not None:
            return await self._get(session, memory_id)
        async with AsyncSessionLocal() as s:
            return await self._get(s, memory_id)

    async def list(
        self,
        filters: MemoryListFilters | None = None,
        *,
        session: AsyncSession | None = None,
    ) -> list[MemoryRecord]:
        filters = filters or MemoryListFilters()
        if session is not None:
            return await self._list(session, filters)
        async with AsyncSessionLocal() as s:
            return await self._list(s, filters)

    async def update(
        self,
        memory_id: str,
        data: MemoryUpdate,
        *,
        session: AsyncSession | None = None,
    ) -> MemoryRecord:
        if session is not None:
            return await self._update(session, memory_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._update(s, memory_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def delete(self, memory_id: str, *, session: AsyncSession | None = None) -> None:
        if session is not None:
            await self._delete(session, memory_id)
            return
        async with AsyncSessionLocal() as s:
            try:
                await self._delete(s, memory_id)
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def list_versions(
        self,
        memory_id: str,
        *,
        session: AsyncSession | None = None,
    ) -> list[MemoryVersionRecord]:
        if session is not None:
            return await self._list_versions(session, memory_id)
        async with AsyncSessionLocal() as s:
            return await self._list_versions(s, memory_id)

    async def get_version(
        self,
        memory_id: str,
        version: int,
        *,
        session: AsyncSession | None = None,
    ) -> MemoryVersionRecord:
        if session is not None:
            return await self._get_version(session, memory_id, version)
        async with AsyncSessionLocal() as s:
            return await self._get_version(s, memory_id, version)

    async def load_prompt_context(
        self,
        *,
        conversation_id: str | None = None,
        project_id: str | None = None,
        max_tokens: int | None = None,
        filters: PromptContextFilters | None = None,
        session: AsyncSession | None = None,
    ) -> PromptContext:
        """Stable contract: structured PromptContext, not a rendered string."""
        filters = filters or PromptContextFilters()
        if session is not None:
            return await self._load_prompt_context(
                session,
                conversation_id=conversation_id,
                project_id=project_id,
                max_tokens=max_tokens,
                filters=filters,
            )
        async with AsyncSessionLocal() as s:
            return await self._load_prompt_context(
                s,
                conversation_id=conversation_id,
                project_id=project_id,
                max_tokens=max_tokens,
                filters=filters,
            )

    async def apply_ops(
        self,
        ops: list[MemoryOp],
        *,
        project_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> list[MemoryRecord]:
        """Hook for M5 memory agent — uses the same write path as CRUD."""
        if session is not None:
            return await self._apply_ops(session, ops, project_id=project_id)
        async with AsyncSessionLocal() as s:
            try:
                results = await self._apply_ops(s, ops, project_id=project_id)
                await s.commit()
                return results
            except Exception:
                await s.rollback()
                raise

    # ------------------------------------------------------------------
    # Internal write path — only place that INSERT/UPDATE/DELETE memories
    # ------------------------------------------------------------------

    async def _create(self, session: AsyncSession, data: MemoryCreate) -> MemoryRecord:
        self._validate_kind(data.kind)
        key = self._resolve_key(data.kind, data.key)
        project_id = resolve_project_id(data.project_id)

        if data.kind in SINGLETON_KINDS:
            # Singleton-per-project (ADR-0047): each thesis owns its identity memory.
            existing = await self._find_singleton(session, data.kind, project_id=project_id)
            if existing is not None:
                raise SingletonMemoryExistsError(data.kind, key)

        now = datetime.now(timezone.utc)
        row = models.Memory(
            project_id=project_id,
            kind=data.kind,
            key=key,
            title=data.title,
            content=data.content,
            pinned=data.pinned,
            source=data.source,
            version=1,
            metadata_=data.metadata,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()
        await self._append_version_snapshot(session, row)
        await session.flush()
        return self._to_record(row)

    async def _get(self, session: AsyncSession, memory_id: str) -> MemoryRecord:
        row = await session.get(models.Memory, memory_id)
        if row is None:
            raise MemoryNotFoundError(memory_id)
        return self._to_record(row)

    async def _list(self, session: AsyncSession, filters: MemoryListFilters) -> list[MemoryRecord]:
        stmt = select(models.Memory).where(
            models.Memory.project_id == resolve_project_id(filters.project_id)
        )
        if filters.kind is not None:
            stmt = stmt.where(models.Memory.kind == filters.kind)
        if filters.key is not None:
            stmt = stmt.where(models.Memory.key == filters.key)
        if filters.pinned is not None:
            stmt = stmt.where(models.Memory.pinned == filters.pinned)
        if filters.q:
            pattern = f"%{filters.q}%"
            stmt = stmt.where(
                or_(
                    models.Memory.title.ilike(pattern),
                    models.Memory.content.ilike(pattern),
                )
            )
        stmt = (
            stmt.order_by(models.Memory.updated_at.desc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        rows = (await session.execute(stmt)).scalars().all()
        return [self._to_record(r) for r in rows]

    async def _update(
        self,
        session: AsyncSession,
        memory_id: str,
        data: MemoryUpdate,
    ) -> MemoryRecord:
        row = await session.get(models.Memory, memory_id)
        if row is None:
            raise MemoryNotFoundError(memory_id)
        if row.version != data.expected_version:
            raise WriteConflictError(
                memory_id,
                expected_version=data.expected_version,
                actual_version=row.version,
            )

        values: dict = {"updated_at": datetime.now(timezone.utc), "version": row.version + 1}
        if data.title is not None:
            values["title"] = data.title
        if data.content is not None:
            values["content"] = data.content
        if data.metadata is not None:
            values["metadata"] = data.metadata
        if data.pinned is not None:
            values["pinned"] = data.pinned

        result = await session.execute(
            update(models.Memory)
            .where(
                models.Memory.id == memory_id,
                models.Memory.version == data.expected_version,
            )
            .values(**values)
            .returning(models.Memory)
        )
        updated = result.scalar_one_or_none()
        if updated is None:
            await session.refresh(row)
            raise WriteConflictError(
                memory_id,
                expected_version=data.expected_version,
                actual_version=row.version,
            )

        await self._append_version_snapshot(session, updated)
        await session.flush()
        return self._to_record(updated)

    async def _delete(self, session: AsyncSession, memory_id: str) -> None:
        row = await session.get(models.Memory, memory_id)
        if row is None:
            raise MemoryNotFoundError(memory_id)
        if row.kind in SINGLETON_KINDS:
            raise CannotDeleteSingletonError(row.kind)
        await session.delete(row)
        await session.flush()

    async def _list_versions(
        self,
        session: AsyncSession,
        memory_id: str,
    ) -> list[MemoryVersionRecord]:
        await self._get(session, memory_id)
        rows = (
            await session.execute(
                select(models.MemoryVersion)
                .where(models.MemoryVersion.memory_id == memory_id)
                .order_by(models.MemoryVersion.version)
            )
        ).scalars().all()
        return [self._to_version_record(memory_id, r) for r in rows]

    async def _get_version(
        self,
        session: AsyncSession,
        memory_id: str,
        version: int,
    ) -> MemoryVersionRecord:
        row = (
            await session.execute(
                select(models.MemoryVersion).where(
                    models.MemoryVersion.memory_id == memory_id,
                    models.MemoryVersion.version == version,
                )
            )
        ).scalar_one_or_none()
        if row is None:
            raise MemoryNotFoundError(f"{memory_id}@v{version}")
        return self._to_version_record(memory_id, row)

    async def _load_prompt_context(
        self,
        session: AsyncSession,
        *,
        conversation_id: str | None,
        max_tokens: int | None,
        filters: PromptContextFilters,
        project_id: str | None = None,
    ) -> PromptContext:
        # conversation_id reserved for future per-conversation scoping (M5+).
        ctx = PromptContext(conversation_id=conversation_id)

        if filters.include_binding_decisions:
            binding = await self._find_by_key(
                session, BINDING_DECISION_KEY, project_id=project_id
            )
            if binding is not None:
                ctx.decisions.append(self._to_prompt_item(binding))

        if filters.include_editable:
            editable = await self._find_singleton(session, "editable", project_id=project_id)
            if editable is not None:
                ctx.editable.append(self._to_prompt_item(editable))

        if filters.include_pinned_user:
            user = await self._find_singleton(session, "user", project_id=project_id)
            if user is not None and user.pinned:
                ctx.user.append(self._to_prompt_item(user))

        if filters.include_pinned_thesis:
            thesis = await self._find_singleton(session, "thesis", project_id=project_id)
            if thesis is not None and thesis.pinned:
                ctx.thesis.append(self._to_prompt_item(thesis))

        if max_tokens is not None:
            ctx = self._truncate_prompt_context(ctx, max_tokens)

        return ctx

    async def _apply_ops(
        self,
        session: AsyncSession,
        ops: list[MemoryOp],
        *,
        project_id: str | None = None,
    ) -> list[MemoryRecord]:
        scope = resolve_project_id(project_id)
        results: list[MemoryRecord] = []
        for op in ops:
            if op.op == "upsert":
                existing = None
                if op.key:
                    existing = (
                        await session.execute(
                            select(models.Memory).where(
                                models.Memory.kind == op.kind,
                                models.Memory.key == op.key,
                                models.Memory.project_id == scope,
                            )
                        )
                    ).scalar_one_or_none()
                if existing is not None:
                    record = await self._update(
                        session,
                        existing.id,
                        MemoryUpdate(content=op.content, expected_version=existing.version),
                    )
                else:
                    record = await self._create(
                        session,
                        MemoryCreate(
                            project_id=scope,
                            kind=op.kind,
                            key=op.key,
                            content=op.content or "",
                        ),
                    )
                results.append(record)
            elif op.op == "delete":
                if op.key:
                    row = (
                        await session.execute(
                            select(models.Memory).where(
                                models.Memory.kind == op.kind,
                                models.Memory.key == op.key,
                                models.Memory.project_id == scope,
                            )
                        )
                    ).scalar_one_or_none()
                    if row is not None:
                        await self._delete(session, row.id)
        return results

    async def _append_version_snapshot(self, session: AsyncSession, row: models.Memory) -> None:
        session.add(
            models.MemoryVersion(
                memory_id=row.id,
                version=row.version,
                title=row.title,
                content=row.content,
                metadata_=row.metadata_,
                source=row.source,
            )
        )

    async def _find_by_key(
        self,
        session: AsyncSession,
        key: str,
        *,
        project_id: str | None = None,
    ) -> models.Memory | None:
        return (
            await session.execute(
                select(models.Memory).where(
                    models.Memory.key == key,
                    models.Memory.project_id == resolve_project_id(project_id),
                )
            )
        ).scalar_one_or_none()

    async def _find_singleton(
        self,
        session: AsyncSession,
        kind: str,
        *,
        project_id: str | None = None,
    ) -> models.Memory | None:
        key = CANONICAL_KEYS[kind]
        return (
            await session.execute(
                select(models.Memory).where(
                    models.Memory.kind == kind,
                    models.Memory.key == key,
                    models.Memory.project_id == resolve_project_id(project_id),
                )
            )
        ).scalar_one_or_none()

    @staticmethod
    def _validate_kind(kind: str) -> None:
        if kind not in VALID_KINDS:
            raise ValueError(f"invalid memory kind: {kind}")

    @staticmethod
    def _resolve_key(kind: str, key: str | None) -> str | None:
        if kind in SINGLETON_KINDS:
            return CANONICAL_KEYS[kind]
        return key

    @staticmethod
    def _to_record(row: models.Memory) -> MemoryRecord:
        return MemoryRecord(
            id=row.id,
            project_id=resolve_project_id(getattr(row, "project_id", None)),
            kind=row.kind,
            title=row.title,
            content=row.content,
            metadata=dict(row.metadata_ or {}),
            key=row.key,
            pinned=row.pinned,
            source=row.source,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_version_record(memory_id: str, row: models.MemoryVersion) -> MemoryVersionRecord:
        return MemoryVersionRecord(
            memory_id=memory_id,
            version=row.version,
            title=row.title,
            content=row.content,
            metadata=dict(row.metadata_ or {}),
            source=row.source,
            changed_at=row.changed_at,
        )

    @staticmethod
    def _to_prompt_item(row: models.Memory) -> PromptMemoryItem:
        return PromptMemoryItem(
            id=row.id,
            kind=row.kind,
            title=row.title,
            content=row.content,
            version=row.version,
            pinned=row.pinned,
            key=row.key,
        )

    @staticmethod
    def _truncate_prompt_context(ctx: PromptContext, max_tokens: int) -> PromptContext:
        max_chars = max_tokens * _CHARS_PER_TOKEN_ESTIMATE

        def trim(items: list[PromptMemoryItem]) -> list[PromptMemoryItem]:
            out: list[PromptMemoryItem] = []
            used = 0
            for item in items:
                chunk = item.content
                if used + len(chunk) > max_chars:
                    remaining = max_chars - used
                    if remaining <= 0:
                        break
                    chunk = chunk[:remaining] + "…"
                out.append(item.model_copy(update={"content": chunk}))
                used += len(chunk)
            return out

        return PromptContext(
            decisions=trim(ctx.decisions),
            editable=trim(ctx.editable),
            user=trim(ctx.user),
            thesis=trim(ctx.thesis),
            conversation_id=ctx.conversation_id,
        )


def prompt_context_kinds(ctx: PromptContext) -> set[str]:
    """Test helper — kinds present in a PromptContext."""
    kinds: set[str] = set()
    if ctx.decisions:
        kinds.add("decision")
    if ctx.editable:
        kinds.add("editable")
    if ctx.user:
        kinds.add("user")
    if ctx.thesis:
        kinds.add("thesis")
    return kinds
