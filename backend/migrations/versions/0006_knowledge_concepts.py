"""PX-4 concept persistence — domain tables + seed from PX-3 catalog."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_knowledge_concepts"
down_revision: Union[str, None] = "0005_writing_workspace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_PROJECT = "thesis-agent"

_SEED_CONCEPTS: tuple[tuple[str, str, str, str, bool, str, tuple[str, ...]], ...] = (
    (
        "stigmata",
        "STIGMATA",
        "Framework centrale della tesi",
        "Segno percettivo che condensa significato culturale — asse teorico del corpus.",
        True,
        "alta",
        ("barthes-mythologies", "albers-interaction-color", "hollander-sex-suits"),
    ),
    (
        "aura",
        "Aura",
        "Benjamin — unicità dell'originale",
        "Presenza unica dell'oggetto nel tempo e nello spazio — erode con la riproducibilità.",
        True,
        "alta",
        ("benjamin-opera-arte",),
    ),
    (
        "riproducibilita",
        "Riproducibilità tecnica",
        "Meccanica della diffusione visiva",
        "Diffusione tecnica che altera la percezione dell'originale.",
        False,
        "media",
        ("benjamin-opera-arte",),
    ),
    (
        "percezione",
        "Percezione visiva",
        "Intersezione colore, forma, corpo",
        "Asse che collega esperienza estetica e pratica visiva.",
        False,
        "media",
        ("albers-interaction-color", "csikszentmihalyi-flow"),
    ),
    (
        "mito",
        "Mito borghese",
        "Barthes — naturalizzazione ideologica",
        "Sistema di comunicazione che naturalizza il significato ideologico.",
        False,
        "bassa",
        ("barthes-mythologies",),
    ),
    (
        "abbigliamento",
        "Abbigliamento come segno",
        "Moda e identità visiva",
        "Il vestire come segno culturale e identitario.",
        False,
        "media",
        ("hollander-sex-suits",),
    ),
    (
        "esperienza",
        "Esperienza estetica",
        "Flow e coinvolgimento percettivo",
        "Stato di coinvolgimento totale nell'attività percettiva.",
        False,
        "media",
        ("csikszentmihalyi-flow",),
    ),
)


def _knowledge_state(source_count: int) -> str:
    if source_count >= 2:
        return "linked"
    if source_count == 1:
        return "validated"
    return "candidate"


def upgrade() -> None:
    op.create_table(
        "concepts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column(
            "confidence",
            sa.String(length=32),
            server_default=sa.text("'non_valutata'"),
            nullable=False,
        ),
        sa.Column(
            "knowledge_state",
            sa.String(length=32),
            server_default=sa.text("'candidate'"),
            nullable=False,
        ),
        sa.Column("is_core", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_by",
            sa.String(length=32),
            server_default=sa.text("'operatore'"),
            nullable=False,
        ),
        sa.Column(
            "proposal_state",
            sa.String(length=32),
            server_default=sa.text("'nessuna'"),
            nullable=False,
        ),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("project_id", "slug", name="uq_concepts_project_slug"),
    )
    op.create_index("idx_concepts_project_state", "concepts", ["project_id", "knowledge_state"])
    op.create_index("idx_concepts_project_title", "concepts", ["project_id", "title"])

    op.create_table(
        "concept_source_links",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("concept_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("source_slug", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("concept_id", "source_slug", name="uq_concept_source_links_pair"),
    )
    op.create_index("idx_concept_source_links_source_slug", "concept_source_links", ["source_slug"])

    op.create_table(
        "concept_relations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("from_concept_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("to_concept_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("relation_type", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["from_concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "from_concept_id",
            "to_concept_id",
            "relation_type",
            name="uq_concept_relations_triple",
        ),
    )
    op.create_index("idx_concept_relations_from", "concept_relations", ["from_concept_id"])
    op.create_index("idx_concept_relations_to", "concept_relations", ["to_concept_id"])

    concepts = sa.table(
        "concepts",
        sa.column("project_id", sa.String),
        sa.column("slug", sa.String),
        sa.column("title", sa.Text),
        sa.column("subtitle", sa.Text),
        sa.column("summary", sa.Text),
        sa.column("definition", sa.Text),
        sa.column("confidence", sa.String),
        sa.column("knowledge_state", sa.String),
        sa.column("is_core", sa.Boolean),
        sa.column("created_by", sa.String),
    )
    links = sa.table(
        "concept_source_links",
        sa.column("concept_id", postgresql.UUID(as_uuid=False)),
        sa.column("source_slug", sa.String),
    )

    bind = op.get_bind()
    for slug, title, subtitle, summary, is_core, confidence, source_slugs in _SEED_CONCEPTS:
        state = _knowledge_state(len(source_slugs))
        result = bind.execute(
            sa.text(
                """
                INSERT INTO concepts (
                    project_id, slug, title, subtitle, summary, definition,
                    confidence, knowledge_state, is_core, created_by
                ) VALUES (
                    :project_id, :slug, :title, :subtitle, :summary, :definition,
                    :confidence, :knowledge_state, :is_core, 'importazione'
                )
                RETURNING id
                """
            ),
            {
                "project_id": _DEFAULT_PROJECT,
                "slug": slug,
                "title": title,
                "subtitle": subtitle,
                "summary": summary,
                "definition": summary,
                "confidence": confidence,
                "knowledge_state": state,
                "is_core": is_core,
            },
        )
        concept_id = result.scalar_one()
        for source_slug in source_slugs:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO concept_source_links (concept_id, source_slug)
                    VALUES (:concept_id, :source_slug)
                    """
                ),
                {"concept_id": concept_id, "source_slug": source_slug},
            )


def downgrade() -> None:
    op.drop_index("idx_concept_relations_to", table_name="concept_relations")
    op.drop_index("idx_concept_relations_from", table_name="concept_relations")
    op.drop_table("concept_relations")
    op.drop_index("idx_concept_source_links_source_slug", table_name="concept_source_links")
    op.drop_table("concept_source_links")
    op.drop_index("idx_concepts_project_title", table_name="concepts")
    op.drop_index("idx_concepts_project_state", table_name="concepts")
    op.drop_table("concepts")
