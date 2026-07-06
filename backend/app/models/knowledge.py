"""Concept domain models (PX-4, ADR-0037)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

CONCEPT_RELATION_TYPES = frozenset({"supports", "contradicts", "extends", "used_in", "related"})


class Concept(Base):
    """Canonical concept entity — singleton per (project_id, slug) per INV-KM-2."""

    __tablename__ = "concepts"
    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_concepts_project_slug"),
        Index("idx_concepts_project_state", "project_id", "knowledge_state"),
        Index("idx_concepts_project_title", "project_id", "title"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    definition: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(32), server_default=text("'non_valutata'"))
    knowledge_state: Mapped[str] = mapped_column(String(32), server_default=text("'candidate'"))
    is_core: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_by: Mapped[str] = mapped_column(String(32), server_default=text("'operatore'"))
    proposal_state: Mapped[str] = mapped_column(String(32), server_default=text("'nessuna'"))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )


class ConceptSourceLink(Base):
    """M:N bridge — concept ↔ corpus source slug (ADR-0037)."""

    __tablename__ = "concept_source_links"
    __table_args__ = (
        UniqueConstraint("concept_id", "source_slug", name="uq_concept_source_links_pair"),
        Index("idx_concept_source_links_source_slug", "source_slug"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"))
    source_slug: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )


class ConceptRelation(Base):
    """Typed edges between concepts (ADR-0037 graph)."""

    __tablename__ = "concept_relations"
    __table_args__ = (
        UniqueConstraint(
            "from_concept_id",
            "to_concept_id",
            "relation_type",
            name="uq_concept_relations_triple",
        ),
        Index("idx_concept_relations_from", "from_concept_id"),
        Index("idx_concept_relations_to", "to_concept_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    from_concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"))
    to_concept_id: Mapped[str] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"))
    relation_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
