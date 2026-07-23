"""Add project_id to documents — thesis workspace partition (ADR-0047 M-B).

Existing rows are attributed to the Default Thesis (thesis-agent): they are its
corpus. Chunks/embeddings/versions inherit scope via document_id.

Revision ID: 0012_document_project_id
Revises: 0011_projects_table
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_document_project_id"
down_revision: Union[str, None] = "0011_projects_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "project_id",
            sa.String(length=64),
            nullable=False,
            server_default="thesis-agent",
        ),
    )
    op.create_index("idx_documents_project_id", "documents", ["project_id"])


def downgrade() -> None:
    op.drop_index("idx_documents_project_id", table_name="documents")
    op.drop_column("documents", "project_id")
