"""M4 Phase 1 — retrieval migration and model invariants."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from app.db.base import Base


def test_embedding_model_has_composite_primary_key():
    table = Base.metadata.tables["embeddings"]
    pk_cols = {col.name for col in table.primary_key.columns}
    assert pk_cols == {"id", "model"}


def test_chunks_table_has_content_tsv_index():
    indexes = {idx.name for idx in Base.metadata.tables["chunks"].indexes}
    assert "idx_chunks_content_tsv" in indexes


@pytest.fixture
async def db_available():
    from app.db.session_async import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"async DB not reachable: {exc}")


@pytest.mark.asyncio
async def test_retrieval_migration_partition_and_indexes(db_available):
    from app.db.session_async import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        part = await session.execute(
            text(
                """
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'embeddings_part_text_multilingual_embedding_002'
                  AND n.nspname = 'public'
                """
            )
        )
        assert part.scalar() == 1

        hnsw = await session.execute(
            text(
                """
                SELECT 1 FROM pg_indexes
                WHERE tablename = 'embeddings_part_text_multilingual_embedding_002'
                  AND indexname LIKE '%hnsw%'
                """
            )
        )
        assert hnsw.scalar() == 1

        tsv = await session.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'chunks' AND column_name = 'content_tsv'
                """
            )
        )
        assert tsv.scalar() == 1

        unique = await session.execute(
            text(
                """
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'uq_embeddings_chunk_owner_model'
                """
            )
        )
        assert unique.scalar() == 1
