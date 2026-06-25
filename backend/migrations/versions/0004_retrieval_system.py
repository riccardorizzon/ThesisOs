"""M4 retrieval system: partitioned embeddings, HNSW, hybrid search on chunks.

Revision ID: 0004_retrieval_system
Revises: 0003_document_system
Create Date: 2026-06-25

LIST-partition embeddings by model (ADR-0024); HNSW on default model partition;
tsvector GIN on chunks.content for hybrid keyword leg (M4 spec §7).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_retrieval_system"
down_revision: Union[str, None] = "0003_document_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_EMBEDDING_MODEL = "text-multilingual-embedding-002"
DEFAULT_PARTITION = "embeddings_part_text_multilingual_embedding_002"


def upgrade() -> None:
    # --- chunks: generated tsvector for hybrid keyword search ---
    op.execute(
        """
        ALTER TABLE chunks
        ADD COLUMN content_tsv tsvector
        GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
        """
    )
    op.create_index(
        "idx_chunks_content_tsv",
        "chunks",
        ["content_tsv"],
        postgresql_using="gin",
    )

    # --- embeddings: LIST partition by model (PK must include partition key) ---
    op.execute("ALTER TABLE embeddings RENAME TO embeddings_legacy")
    op.execute(
        """
        CREATE TABLE embeddings (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            owner_type VARCHAR(16) NOT NULL,
            owner_id UUID NOT NULL,
            model VARCHAR(128) NOT NULL,
            dimension INTEGER NOT NULL,
            embedding vector(768) NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
            PRIMARY KEY (id, model)
        ) PARTITION BY LIST (model)
        """
    )
    op.execute(
        f"""
        CREATE TABLE {DEFAULT_PARTITION} PARTITION OF embeddings
        FOR VALUES IN ('{DEFAULT_EMBEDDING_MODEL}')
        """
    )
    op.execute(
        """
        INSERT INTO embeddings (
            id, owner_type, owner_id, model, dimension, embedding,
            metadata, content_hash, created_at
        )
        SELECT
            id, owner_type, owner_id, model, dimension, embedding,
            metadata, content_hash, created_at
        FROM embeddings_legacy
        """
    )
    op.execute("DROP TABLE embeddings_legacy")

    op.execute(
        f"""
        CREATE INDEX idx_{DEFAULT_PARTITION}_embedding_hnsw
        ON {DEFAULT_PARTITION}
        USING hnsw (embedding vector_cosine_ops)
        """
    )
    op.create_index(
        "idx_embeddings_owner_model",
        "embeddings",
        ["owner_type", "owner_id", "model"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_embeddings_chunk_owner_model
        ON embeddings (owner_type, owner_id, model)
        WHERE owner_type = 'chunk'
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_embeddings_chunk_owner_model")
    op.drop_index("idx_embeddings_owner_model", table_name="embeddings")
    op.execute(f"DROP INDEX IF EXISTS idx_{DEFAULT_PARTITION}_embedding_hnsw")

    op.execute("ALTER TABLE embeddings RENAME TO embeddings_partitioned")
    op.execute(
        """
        CREATE TABLE embeddings (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            owner_type VARCHAR(16) NOT NULL,
            owner_id UUID NOT NULL,
            model VARCHAR(128) NOT NULL,
            dimension INTEGER NOT NULL,
            embedding vector(768) NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
            PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        INSERT INTO embeddings (
            id, owner_type, owner_id, model, dimension, embedding,
            metadata, content_hash, created_at
        )
        SELECT
            id, owner_type, owner_id, model, dimension, embedding,
            metadata, content_hash, created_at
        FROM embeddings_partitioned
        """
    )
    op.execute("DROP TABLE embeddings_partitioned")

    op.drop_index("idx_chunks_content_tsv", table_name="chunks")
    op.drop_column("chunks", "content_tsv")
