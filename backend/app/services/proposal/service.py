"""ProposalService — durable writing proposals (M7, P-REVIEW-PERSIST-BE).

Accept applies chapter content via ChapterService with optimistic versioning
(ADR-0032/0033). Proposals are stored in the `proposals` table (architecture lock).
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, String, Text, select, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.session_async import AsyncSessionLocal
from app.schemas.chapter import ChapterContentUpdate, ChapterRecord
from app.services.chapter import ChapterService

VALID_PROPOSAL_ACTIONS = frozenset({"rewrite", "verify", "expand", "find-sources"})
VALID_PROPOSAL_STATUSES = frozenset({"pending", "accepted", "rejected"})


class ProposalRecord(BaseModel):
    id: str
    project_id: str
    chapter_id: str
    status: str
    original: str
    proposed: str
    action: str
    created_at: datetime


class ProposalCreate(BaseModel):
    project_id: str = Field(min_length=1, max_length=64)
    chapter_id: str
    original: str
    proposed: str
    action: str = Field(min_length=1, max_length=32)
    metadata: dict = Field(default_factory=dict)


class ProposalAcceptRequest(BaseModel):
    expected_chapter_version: int | None = None


class ProposalRejectRequest(BaseModel):
    reason: str | None = None


class ProposalRow(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[str] = mapped_column(String(64))
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    original: Mapped[str] = mapped_column(Text)
    proposed: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(32))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )


class ProposalServiceError(Exception):
    """Base error for ProposalService domain failures."""


class ProposalNotFoundError(ProposalServiceError):
    def __init__(self, proposal_id: str):
        self.proposal_id = proposal_id
        super().__init__(f"proposal not found: {proposal_id}")


class ProposalNotPendingError(ProposalServiceError):
    def __init__(self, proposal_id: str, status: str):
        self.proposal_id = proposal_id
        self.status = status
        super().__init__(f"proposal not pending: {proposal_id} (status={status})")


class InvalidProposalActionError(ProposalServiceError):
    def __init__(self, action: str):
        self.action = action
        super().__init__(f"invalid_action: {action!r}")


class ProposalService:
    """Persist and resolve writing proposals."""

    def __init__(self, *, chapter_service: ChapterService | None = None) -> None:
        self._chapters = chapter_service or ChapterService()

    async def create(
        self, data: ProposalCreate, *, session: AsyncSession | None = None
    ) -> ProposalRecord:
        if data.action not in VALID_PROPOSAL_ACTIONS:
            raise InvalidProposalActionError(data.action)
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

    async def list(
        self,
        *,
        project_id: str,
        chapter_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> list[ProposalRecord]:
        if session is not None:
            return await self._list(session, project_id=project_id, chapter_id=chapter_id)
        async with AsyncSessionLocal() as s:
            return await self._list(s, project_id=project_id, chapter_id=chapter_id)

    async def accept(
        self,
        proposal_id: str,
        data: ProposalAcceptRequest | None = None,
        *,
        session: AsyncSession | None = None,
    ) -> ChapterRecord:
        data = data or ProposalAcceptRequest()
        if session is not None:
            return await self._accept(session, proposal_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._accept(s, proposal_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def reject(
        self,
        proposal_id: str,
        data: ProposalRejectRequest | None = None,
        *,
        session: AsyncSession | None = None,
    ) -> ProposalRecord:
        data = data or ProposalRejectRequest()
        if session is not None:
            return await self._reject(session, proposal_id, data)
        async with AsyncSessionLocal() as s:
            try:
                record = await self._reject(s, proposal_id, data)
                await s.commit()
                return record
            except Exception:
                await s.rollback()
                raise

    async def _create(self, session: AsyncSession, data: ProposalCreate) -> ProposalRecord:
        row = ProposalRow(
            project_id=data.project_id,
            chapter_id=data.chapter_id,
            status="pending",
            original=data.original,
            proposed=data.proposed,
            action=data.action,
            metadata_=dict(data.metadata),
        )
        session.add(row)
        await session.flush()
        return self._to_record(row)

    async def _list(
        self, session: AsyncSession, *, project_id: str, chapter_id: str | None
    ) -> list[ProposalRecord]:
        stmt = select(ProposalRow).where(ProposalRow.project_id == project_id)
        if chapter_id is not None:
            stmt = stmt.where(ProposalRow.chapter_id == chapter_id)
        stmt = stmt.order_by(ProposalRow.created_at.desc())
        rows = (await session.execute(stmt)).scalars().all()
        return [self._to_record(r) for r in rows]

    async def _accept(
        self, session: AsyncSession, proposal_id: str, data: ProposalAcceptRequest
    ) -> ChapterRecord:
        row = await self._require_pending(session, proposal_id)
        chapter = await self._chapters.get(row.chapter_id, session=session)
        expected_version = (
            data.expected_chapter_version
            if data.expected_chapter_version is not None
            else chapter.version
        )
        updated = await self._chapters.update_content(
            row.chapter_id,
            ChapterContentUpdate(content_md=row.proposed, expected_version=expected_version),
            session=session,
        )
        row.status = "accepted"
        row.metadata_ = {**dict(row.metadata_ or {}), "accepted_at": datetime.now(timezone.utc).isoformat()}
        await session.flush()
        return updated

    async def _reject(
        self, session: AsyncSession, proposal_id: str, data: ProposalRejectRequest
    ) -> ProposalRecord:
        row = await self._require_pending(session, proposal_id)
        row.status = "rejected"
        meta = dict(row.metadata_ or {})
        if data.reason:
            meta["reject_reason"] = data.reason
        meta["rejected_at"] = datetime.now(timezone.utc).isoformat()
        row.metadata_ = meta
        await session.flush()
        return self._to_record(row)

    async def _require_pending(self, session: AsyncSession, proposal_id: str) -> ProposalRow:
        row = await session.get(ProposalRow, proposal_id)
        if row is None:
            raise ProposalNotFoundError(proposal_id)
        if row.status != "pending":
            raise ProposalNotPendingError(proposal_id, row.status)
        return row

    @staticmethod
    def _to_record(row: ProposalRow) -> ProposalRecord:
        return ProposalRecord(
            id=row.id,
            project_id=row.project_id,
            chapter_id=row.chapter_id,
            status=row.status,
            original=row.original,
            proposed=row.proposed,
            action=row.action,
            created_at=row.created_at,
        )


__all__ = [
    "ProposalService",
    "ProposalServiceError",
    "ProposalNotFoundError",
    "ProposalNotPendingError",
    "InvalidProposalActionError",
    "ProposalRecord",
    "ProposalCreate",
    "ProposalAcceptRequest",
    "ProposalRejectRequest",
    "VALID_PROPOSAL_ACTIONS",
]
