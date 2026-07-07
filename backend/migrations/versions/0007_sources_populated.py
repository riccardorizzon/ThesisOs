"""M7 — populate sources table from legacy corpus catalog (project-scoped)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_sources_populated"
down_revision: Union[str, None] = "0006_knowledge_concepts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_PROJECT = "thesis-agent"

# Legacy catalog aligned with CORPUS_PICKER_SOURCES (PX2-EWO-004).
_SEED_SOURCES: tuple[tuple[str, str, str, int, str], ...] = (
    (
        "benjamin-opera-arte",
        "L'opera d'arte nell'epoca della riproducibilità tecnica",
        "Walter Benjamin",
        1936,
        "approvata",
    ),
    (
        "barthes-mythologies",
        "Mythologies",
        "Roland Barthes",
        1957,
        "esclusa",
    ),
    (
        "albers-interaction-color",
        "Interaction of Color",
        "Josef Albers",
        1963,
        "candidata",
    ),
    (
        "csikszentmihalyi-flow",
        "Flow",
        "Mihaly Csikszentmihalyi",
        1990,
        "candidata",
    ),
    (
        "hollander-sex-suits",
        "Sex and Suits",
        "Anne Hollander",
        1994,
        "approvata",
    ),
)

# Concept links per source slug (matches 0006 seed).
_SOURCE_CONCEPT_COUNTS: dict[str, int] = {
    "benjamin-opera-arte": 2,
    "barthes-mythologies": 2,
    "albers-interaction-color": 2,
    "csikszentmihalyi-flow": 2,
    "hollander-sex-suits": 2,
}

_STATUS_TO_STATE: dict[str, str] = {
    "candidata": "candidate",
    "approvata": "validated",
    "esclusa": "deprecated",
}


def _knowledge_state(corpus_status: str, concept_count: int) -> str:
    base = _STATUS_TO_STATE.get(corpus_status, "candidate")
    if base == "deprecated":
        return "deprecated"
    if concept_count >= 2:
        return "linked"
    return base


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("project_id", sa.String(length=64), nullable=False, server_default="thesis-agent"),
    )
    op.add_column("sources", sa.Column("slug", sa.String(length=128), nullable=False, server_default=""))
    op.add_column(
        "sources",
        sa.Column(
            "corpus_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'candidata'"),
        ),
    )
    op.add_column("sources", sa.Column("subtitle", sa.Text(), nullable=True))
    op.add_column("sources", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column(
        "sources",
        sa.Column(
            "confidence",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'non_valutata'"),
        ),
    )
    op.add_column(
        "sources",
        sa.Column(
            "knowledge_state",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'candidate'"),
        ),
    )
    op.add_column(
        "sources",
        sa.Column("is_core", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "sources",
        sa.Column(
            "created_by",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'importazione'"),
        ),
    )

    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM sources"))

    op.create_unique_constraint("uq_sources_project_slug", "sources", ["project_id", "slug"])
    op.create_index("idx_sources_project_corpus_status", "sources", ["project_id", "corpus_status"])

    for slug, title, author, year, corpus_status in _SEED_SOURCES:
        concept_count = _SOURCE_CONCEPT_COUNTS.get(slug, 0)
        state = _knowledge_state(corpus_status, concept_count)
        summary = f"{year} · Fonte bibliografica"
        bind.execute(
            sa.text(
                """
                INSERT INTO sources (
                    project_id, slug, type, title, subtitle, summary, year,
                    authors, corpus_status, confidence, knowledge_state,
                    is_core, created_by
                ) VALUES (
                    :project_id, :slug, 'catalog', :title, :subtitle, :summary, :year,
                    CAST(:authors AS jsonb), :corpus_status, 'non_valutata', :knowledge_state,
                    false, 'importazione'
                )
                """
            ),
            {
                "project_id": _DEFAULT_PROJECT,
                "slug": slug,
                "title": title,
                "subtitle": author,
                "summary": summary,
                "year": year,
                "authors": f'[{{"literal": "{author}"}}]',
                "corpus_status": corpus_status,
                "knowledge_state": state,
            },
        )


def downgrade() -> None:
    op.drop_index("idx_sources_project_corpus_status", table_name="sources")
    op.drop_constraint("uq_sources_project_slug", "sources", type_="unique")
    op.drop_column("sources", "created_by")
    op.drop_column("sources", "is_core")
    op.drop_column("sources", "knowledge_state")
    op.drop_column("sources", "confidence")
    op.drop_column("sources", "summary")
    op.drop_column("sources", "subtitle")
    op.drop_column("sources", "corpus_status")
    op.drop_column("sources", "slug")
    op.drop_column("sources", "project_id")
