"""Add project_id to chapters for hard project isolation (CUR-7).

Revision ID: 0009_chapter_project_id
Revises: 0008_proposals
Create Date: 2026-07-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_chapter_project_id"
down_revision: Union[str, None] = "0008_proposals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chapters",
        sa.Column(
            "project_id",
            sa.String(length=64),
            nullable=False,
            server_default="thesis-agent",
        ),
    )
    # Dogfood / e2e seed rows belong to the demo project. Migrated Kimi thesis
    # chapters stay on thesis-agent so Riprendi keeps Cap.1–3 / §3.6.
    op.execute(
        sa.text(
            """
            UPDATE chapters
            SET project_id = 'demo-thesis'
            WHERE lower(title) = 'e2e export'
               OR lower(title) LIKE '%(dogfood%'
            """
        )
    )
    op.create_index("idx_chapters_project_id", "chapters", ["project_id"])


def downgrade() -> None:
    op.drop_index("idx_chapters_project_id", table_name="chapters")
    op.drop_column("chapters", "project_id")
