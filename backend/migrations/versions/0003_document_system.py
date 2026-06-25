"""M3 document system: document_versions, documents extensions, chunks.chunk_hash

Revision ID: 0003_document_system
Revises: 0002_memory_system
Create Date: 2026-06-24

Extends documents for versioning and parse lifecycle; adds document_versions
append-only history; adds chunk_hash for stable M4 references (ADR-0020, ADR-0021).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_document_system"
down_revision: Union[str, None] = "0002_memory_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _id_column() -> sa.Column:
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=False),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )


def upgrade() -> None:
    # --- documents: M3 metadata + versioning columns ---
    op.add_column(
        "documents",
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    )
    op.add_column("documents", sa.Column("parser", sa.String(length=32), nullable=True))
    op.add_column(
        "documents",
        sa.Column("parsed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column("documents", sa.Column("chunk_count", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))

    # Align legacy M0 status strings with M3 lifecycle (ADR-0022).
    op.execute("UPDATE documents SET status = 'processing' WHERE status = 'parsing'")
    op.execute("UPDATE documents SET status = 'failed' WHERE status = 'error'")

    # --- document_versions ---
    op.create_table(
        "document_versions",
        _id_column(),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=16), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=True),
        sa.Column("parser", sa.String(length=32), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "changed_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("change_reason", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("document_id", "version", name="uq_document_versions_document_id_version"),
    )
    op.create_index("idx_document_versions_document_id", "document_versions", ["document_id"])

    # --- chunks: stable hash for M4 (spec §5.2) ---
    op.add_column("chunks", sa.Column("chunk_hash", sa.String(length=64), nullable=True))
    # Backfill existing rows (typically none in fresh DBs); requires pgcrypto for digest().
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        """
        UPDATE chunks
        SET chunk_hash = encode(
            digest(
                convert_to(
                    document_id::text || ':' || chunk_index::text || ':' ||
                    regexp_replace(trim(both from content), E'\\r\\n', E'\\n', 'g'),
                    'UTF8'
                ),
                'sha256'
            ),
            'hex'
        )
        WHERE chunk_hash IS NULL
        """
    )
    op.alter_column("chunks", "chunk_hash", nullable=False)

    op.create_unique_constraint(
        "uq_chunks_document_id_chunk_index",
        "chunks",
        ["document_id", "chunk_index"],
    )
    op.create_unique_constraint(
        "uq_chunks_document_id_chunk_hash",
        "chunks",
        ["document_id", "chunk_hash"],
    )

    op.create_index("idx_documents_status", "documents", ["status"])
    op.create_index("idx_documents_updated_at", "documents", [sa.text("updated_at DESC")])


def downgrade() -> None:
    op.drop_index("idx_documents_updated_at", table_name="documents")
    op.drop_index("idx_documents_status", table_name="documents")
    op.drop_constraint("uq_chunks_document_id_chunk_hash", "chunks", type_="unique")
    op.drop_constraint("uq_chunks_document_id_chunk_index", "chunks", type_="unique")
    op.drop_column("chunks", "chunk_hash")
    op.drop_index("idx_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "parsed_at")
    op.drop_column("documents", "parser")
    op.drop_column("documents", "version")
    op.execute("UPDATE documents SET status = 'parsing' WHERE status = 'processing'")
    op.execute("UPDATE documents SET status = 'error' WHERE status = 'failed'")
