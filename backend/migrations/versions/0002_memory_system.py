"""M2 memory system: title column, memory_versions, indexes

Revision ID: 0002_memory_system
Revises: 0001_initial
Create Date: 2026-06-24

Adds human-readable title on memories, append-only version history, and
partial unique indexes for singleton operational kinds (ADR-0015, ADR-0017).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_memory_system"
down_revision: Union[str, None] = "0001_initial"
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
    op.add_column("memories", sa.Column("title", sa.Text(), nullable=True))

    op.create_table(
        "memory_versions",
        _id_column(),
        sa.Column("memory_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("changed_at", postgresql.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["memory_id"], ["memories.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("memory_id", "version", name="uq_memory_versions_memory_id_version"),
    )
    op.create_index("idx_memory_versions_memory_id", "memory_versions", ["memory_id"])

    op.create_index(
        "uq_memories_kind_user",
        "memories",
        ["kind"],
        unique=True,
        postgresql_where=sa.text("kind = 'user' AND key = 'user'"),
    )
    op.create_index(
        "uq_memories_kind_thesis",
        "memories",
        ["kind"],
        unique=True,
        postgresql_where=sa.text("kind = 'thesis' AND key = 'thesis'"),
    )
    op.create_index(
        "uq_memories_kind_editable",
        "memories",
        ["kind"],
        unique=True,
        postgresql_where=sa.text("kind = 'editable' AND key = 'editable'"),
    )
    op.create_index(
        "uq_memories_kind_key",
        "memories",
        ["kind", "key"],
        unique=True,
        postgresql_where=sa.text("key IS NOT NULL"),
    )
    op.create_index("idx_memories_kind", "memories", ["kind"])
    op.create_index("idx_memories_updated_at", "memories", [sa.text("updated_at DESC")])


def downgrade() -> None:
    op.drop_index("idx_memories_updated_at", table_name="memories")
    op.drop_index("idx_memories_kind", table_name="memories")
    op.drop_index("uq_memories_kind_key", table_name="memories")
    op.drop_index("uq_memories_kind_editable", table_name="memories")
    op.drop_index("uq_memories_kind_thesis", table_name="memories")
    op.drop_index("uq_memories_kind_user", table_name="memories")
    op.drop_index("idx_memory_versions_memory_id", table_name="memory_versions")
    op.drop_table("memory_versions")
    op.drop_column("memories", "title")
