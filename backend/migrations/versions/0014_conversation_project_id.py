"""Add project_id to conversations — replaces the AgentRun scope hack (ADR-0047 M-D).

Backfill order: explicit scope rows (trigger='scope'), then any run that carried
a project in its input, then Default Thesis. Messages inherit via conversation_id.

Revision ID: 0014_conversation_project_id
Revises: 0013_memory_project_id
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0014_conversation_project_id"
down_revision: Union[str, None] = "0013_memory_project_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column("project_id", sa.String(length=64), nullable=True),
    )
    op.execute(
        sa.text(
            """
            UPDATE conversations c SET project_id = COALESCE(
              (SELECT ar.input->>'project_id' FROM agent_runs ar
                WHERE ar.conversation_id = c.id AND ar.trigger = 'scope'
                  AND COALESCE(ar.input->>'project_id', '') <> ''
                ORDER BY ar.created_at DESC LIMIT 1),
              (SELECT ar.input->>'project_id' FROM agent_runs ar
                WHERE ar.conversation_id = c.id
                  AND COALESCE(ar.input->>'project_id', '') <> ''
                ORDER BY ar.created_at DESC LIMIT 1),
              'thesis-agent')
            """
        )
    )
    op.alter_column(
        "conversations",
        "project_id",
        nullable=False,
        server_default="thesis-agent",
    )
    op.create_index("idx_conversations_project_id", "conversations", ["project_id"])


def downgrade() -> None:
    op.drop_index("idx_conversations_project_id", table_name="conversations")
    op.drop_column("conversations", "project_id")
