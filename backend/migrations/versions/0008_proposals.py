"""M7 — durable writing proposals (P-REVIEW-PERSIST-BE)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_proposals"
down_revision: Union[str, None] = "0007_sources_populated"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "proposals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("chapter_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("original", sa.Text(), nullable=False),
        sa.Column("proposed", sa.Text(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_proposals_project_chapter", "proposals", ["project_id", "chapter_id"])


def downgrade() -> None:
    op.drop_index("idx_proposals_project_chapter", table_name="proposals")
    op.drop_table("proposals")
