"""Projects table — durable thesis-workspace registry (ADR-0047 M-A).

Revision ID: 0011_projects_table
Revises: 0010_source_document_cascade
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_projects_table"
down_revision: Union[str, None] = "0010_source_document_cascade"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="owned"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="active"),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    # Seed the two known workspaces. Idempotent: fresh DBs and the live dev DB
    # both converge on the same rows (ADR-0047 §1).
    op.execute(
        sa.text(
            """
            INSERT INTO projects (id, display_name, kind) VALUES
              ('thesis-agent',
               'Prima dei dieci minuti. Il processo creativo nel fashion design',
               'owned'),
              ('demo-thesis', 'Progetto dimostrativo', 'demo')
            ON CONFLICT (id) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.drop_table("projects")
