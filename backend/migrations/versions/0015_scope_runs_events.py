"""Add project_id to tasks, notes, agent_runs, events (ADR-0047 M-E).

agent_runs backfills from its own input JSON when a project was recorded;
everything else is attributed to the Default Thesis.

Revision ID: 0015_scope_tasks_notes_runs_events
Revises: 0014_conversation_project_id
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_scope_runs_events"
down_revision: Union[str, None] = "0014_conversation_project_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = ("tasks", "notes", "agent_runs", "events")


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(
            table,
            sa.Column("project_id", sa.String(length=64), nullable=True),
        )
    op.execute(
        sa.text(
            """
            UPDATE agent_runs
            SET project_id = COALESCE(NULLIF(input->>'project_id', ''), 'thesis-agent')
            """
        )
    )
    for table in ("tasks", "notes", "events"):
        op.execute(sa.text(f"UPDATE {table} SET project_id = 'thesis-agent'"))
    for table in _TABLES:
        op.alter_column(
            table, "project_id", nullable=False, server_default="thesis-agent"
        )
        op.create_index(f"idx_{table}_project_id", table, ["project_id"])


def downgrade() -> None:
    for table in _TABLES:
        op.drop_index(f"idx_{table}_project_id", table_name=table)
        op.drop_column(table, "project_id")
