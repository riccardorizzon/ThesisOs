"""Cascade source rows when their imported document is deleted.

Revision ID: 0010_source_document_cascade
Revises: 0009_chapter_project_id
"""

from alembic import op

revision = "0010_source_document_cascade"
down_revision = "0009_chapter_project_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("sources_document_id_fkey", "sources", type_="foreignkey")
    op.create_foreign_key(
        "sources_document_id_fkey",
        "sources",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("sources_document_id_fkey", "sources", type_="foreignkey")
    op.create_foreign_key(
        "sources_document_id_fkey",
        "sources",
        "documents",
        ["document_id"],
        ["id"],
    )
