from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Computed, ForeignKey, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

EMBEDDING_DIM = 768


class Project(Base):
    """Thesis workspace registry — durable SoR (ADR-0047)."""

    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(16), default="owned", server_default=text("'owned'"))
    status: Mapped[str] = mapped_column(String(16), default="active", server_default=text("'active'"))
    settings: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (Index("idx_documents_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    title: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(16))
    original_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    gcs_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="uploaded")
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    parser: Mapped[str | None] = mapped_column(String(32), nullable=True)
    parsed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint("document_id", "version", name="uq_document_versions_document_id_version"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(16))
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parser: Mapped[str | None] = mapped_column(String(32), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    changed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    change_reason: Mapped[str] = mapped_column(String(16))


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunks_document_id_chunk_index"),
        UniqueConstraint("document_id", "chunk_hash", name="uq_chunks_document_id_chunk_hash"),
        Index("idx_chunks_content_tsv", "content_tsv", postgresql_using="gin"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_hash: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    content_tsv: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)", persisted=True),
    )
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = (
        PrimaryKeyConstraint("id", "model"),
        Index("idx_embeddings_owner_model", "owner_type", "owner_id", "model"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), server_default=text("gen_random_uuid()"))
    owner_type: Mapped[str] = mapped_column(String(16))
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False))
    model: Mapped[str] = mapped_column(String(128))
    dimension: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    content_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_sources_project_slug"),
        Index("idx_sources_project_corpus_status", "project_id", "corpus_status"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=True
    )
    type: Mapped[str] = mapped_column(String(32))
    csl_json: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    doi: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    # M7 sources corpus columns (Alembic 0007) — kept in sync for the schema contract.
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    slug: Mapped[str] = mapped_column(String(128), default="", server_default=text("''"))
    corpus_status: Mapped[str] = mapped_column(String(32), default="candidata", server_default=text("'candidata'"))
    subtitle: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(32), default="non_valutata", server_default=text("'non_valutata'"))
    knowledge_state: Mapped[str] = mapped_column(String(32), default="candidate", server_default=text("'candidate'"))
    is_core: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    created_by: Mapped[str] = mapped_column(String(32), default="importazione", server_default=text("'importazione'"))


class Citation(Base):
    __tablename__ = "citations"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    chapter_id: Mapped[str | None] = mapped_column(ForeignKey("chapters.id"), nullable=True)
    locator: Mapped[str | None] = mapped_column(Text, nullable=True)
    prefix: Mapped[str | None] = mapped_column(Text, nullable=True)
    suffix: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Chapter(Base):
    __tablename__ = "chapters"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("chapters.id"), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="draft")
    content_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)  # M6 (ADR-0033): optimistic-lock token
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class ChapterVersion(Base):
    """Append-only change stream for chapters (M6, ADR-0033)."""

    __tablename__ = "chapter_versions"
    __table_args__ = (
        UniqueConstraint("chapter_id", "version", name="uq_chapter_versions_chapter_id_version"),
    )

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    change_kind: Mapped[str] = mapped_column(String(16))  # WRITE|EDIT|PROMOTE|MERGE|RESTORE
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16))
    content_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    changed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Note(Base):
    __tablename__ = "notes"
    __table_args__ = (Index("idx_notes_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    chapter_id: Mapped[str | None] = mapped_column(ForeignKey("chapters.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    anchor: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (Index("idx_memories_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    kind: Mapped[str] = mapped_column(String(16))
    key: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(16), default="user")
    version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class MemoryVersion(Base):
    __tablename__ = "memory_versions"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    memory_id: Mapped[str] = mapped_column(ForeignKey("memories.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    source: Mapped[str] = mapped_column(String(16))
    changed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("idx_conversations_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    tool_calls: Mapped[list] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("idx_tasks_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    parent_task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    owner_agent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (Index("idx_events_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (Index("idx_agent_runs_project_id", "project_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64), default="thesis-agent", server_default=text("'thesis-agent'"))
    conversation_id: Mapped[str | None] = mapped_column(ForeignKey("conversations.id"), nullable=True)
    graph: Mapped[str | None] = mapped_column(String(64), nullable=True)
    trigger: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class AgentStep(Base):
    __tablename__ = "agent_steps"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    agent_run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"))
    agent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phase: Mapped[str | None] = mapped_column(String(16), nullable=True)
    input: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))


class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = (Index("idx_proposals_project_chapter", "project_id", "chapter_id"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    project_id: Mapped[str] = mapped_column(String(64))
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    original: Mapped[str] = mapped_column(Text)
    proposed: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(32))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
