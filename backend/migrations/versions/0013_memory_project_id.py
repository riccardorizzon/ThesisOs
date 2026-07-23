"""Add project_id to memories — per-thesis memory (ADR-0047 M-C).

Existing memories belong to the Default Thesis. Singleton kinds (user/thesis/
editable) become singleton-per-project so each thesis owns its identity memory.
memory_versions inherit scope via memory_id.

Revision ID: 0013_memory_project_id
Revises: 0012_document_project_id
Create Date: 2026-07-23
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_memory_project_id"
down_revision: Union[str, None] = "0012_document_project_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "memories",
        sa.Column(
            "project_id",
            sa.String(length=64),
            nullable=False,
            server_default="thesis-agent",
        ),
    )
    op.create_index("idx_memories_project_id", "memories", ["project_id"])

    # Singleton uniqueness becomes per-project (ADR-0047): each thesis owns its
    # user/thesis/editable identity memory and its own (kind, key) namespace.
    op.drop_index("uq_memories_kind_user", table_name="memories")
    op.drop_index("uq_memories_kind_thesis", table_name="memories")
    op.drop_index("uq_memories_kind_editable", table_name="memories")
    op.drop_index("uq_memories_kind_key", table_name="memories")
    for kind in ("user", "thesis", "editable"):
        op.create_index(
            f"uq_memories_kind_{kind}",
            "memories",
            ["project_id", "kind"],
            unique=True,
            postgresql_where=sa.text(f"kind = '{kind}' AND key = '{kind}'"),
        )
    op.create_index(
        "uq_memories_kind_key",
        "memories",
        ["project_id", "kind", "key"],
        unique=True,
        postgresql_where=sa.text("key IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_memories_kind_key", table_name="memories")
    for kind in ("user", "thesis", "editable"):
        op.drop_index(f"uq_memories_kind_{kind}", table_name="memories")
    for kind in ("user", "thesis", "editable"):
        op.create_index(
            f"uq_memories_kind_{kind}",
            "memories",
            ["kind"],
            unique=True,
            postgresql_where=sa.text(f"kind = '{kind}' AND key = '{kind}'"),
        )
    op.create_index(
        "uq_memories_kind_key",
        "memories",
        ["kind", "key"],
        unique=True,
        postgresql_where=sa.text("key IS NOT NULL"),
    )
    op.drop_index("idx_memories_project_id", table_name="memories")
    op.drop_column("memories", "project_id")
