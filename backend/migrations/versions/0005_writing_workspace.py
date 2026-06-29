"""M6 writing workspace: chapters.version + chapter_versions change stream

Revision ID: 0005_writing_workspace
Revises: 0004_retrieval_system
Create Date: 2026-06-29

Additive only: adds an optimistic-lock token to chapters and an append-only
chapter_versions change stream (ADR-0032, ADR-0033). M0 chapters are preserved.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_writing_workspace"
down_revision: Union[str, None] = "0004_retrieval_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- chapters: optimistic-lock version token (ADR-0033) ---
    op.add_column(
        "chapters",
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    )

    # --- chapter_versions: append-only change stream ---
    op.create_table(
        "chapter_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("change_kind", sa.String(length=16), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "changed_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("chapter_id", "version", name="uq_chapter_versions_chapter_id_version"),
    )
    op.create_index("idx_chapter_versions_chapter_id", "chapter_versions", ["chapter_id"])


def downgrade() -> None:
    op.drop_index("idx_chapter_versions_chapter_id", table_name="chapter_versions")
    op.drop_table("chapter_versions")
    op.drop_column("chapters", "version")
