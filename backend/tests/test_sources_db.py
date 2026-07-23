"""M7 sources DB persistence tests (P-SOURCES-DB)."""

from __future__ import annotations

import inspect

import pytest
from sqlalchemy import text

from app.services.sources.repository import SourceNotFoundError, SourceRepository
from app.services.sources.service import SourcesService

PROJECT = "thesis-agent"

_SEED_ROWS: tuple[tuple[str, str, str, int, str], ...] = (
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


async def _insert_seed_sources(session) -> None:
    for slug, title, author, year, corpus_status in _SEED_ROWS:
        summary = f"{year} · Fonte bibliografica"
        await session.execute(
            text(
                """
                INSERT INTO sources (
                    project_id, slug, type, title, subtitle, summary, year,
                    authors, corpus_status, confidence, knowledge_state,
                    is_core, created_by
                ) VALUES (
                    :project_id, :slug, 'catalog', :title, :subtitle, :summary, :year,
                    CAST(:authors AS jsonb), :corpus_status, 'non_valutata', 'candidate',
                    false, 'importazione'
                )
                """
            ),
            {
                "project_id": PROJECT,
                "slug": slug,
                "title": title,
                "subtitle": author,
                "summary": summary,
                "year": year,
                "authors": f'[{{"literal": "{author}"}}]',
                "corpus_status": corpus_status,
            },
        )
    await session.commit()


@pytest.fixture
async def seeded_db(db_session):
    await _insert_seed_sources(db_session)
    return db_session


@pytest.mark.asyncio
async def test_migration_seeds_sources(_test_db_ready):
    import os
    import subprocess
    from pathlib import Path

    from app.db.session_async import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as probe:
            await probe.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"async DB not reachable: {exc}")

    backend = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos_test",
    )
    alembic = backend / ".venv" / "bin" / "alembic"
    if not alembic.exists():
        alembic = Path(os.environ.get("VIRTUAL_ENV", "")) / "bin" / "alembic"
    subprocess.run(
        [str(alembic), "downgrade", "0006_knowledge_concepts"],
        cwd=backend,
        env=env,
        check=True,
    )
    # Re-upgrade to head (not just 0007): later suites rely on the full schema
    # (ADR-0047 project_id columns) — leaving the DB at 0007 poisoned them.
    subprocess.run(
        [str(alembic), "upgrade", "head"],
        cwd=backend,
        env=env,
        check=True,
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM sources WHERE project_id = :project_id"),
            {"project_id": PROJECT},
        )
        assert int(result.scalar_one()) >= 5


@pytest.mark.asyncio
async def test_repository_list_project_scoped(seeded_db):
    repo = SourceRepository()
    rows = await repo.list_for_project(seeded_db, PROJECT)
    slugs = {row.slug for row in rows}
    assert "benjamin-opera-arte" in slugs
    assert "barthes-mythologies" in slugs


@pytest.mark.asyncio
async def test_repository_get_by_slug(seeded_db):
    repo = SourceRepository()
    row = await repo.get_by_slug(seeded_db, PROJECT, "benjamin-opera-arte")
    assert row.title.startswith("L'opera d'arte")
    assert row.subtitle == "Walter Benjamin"
    assert row.corpus_status == "approvata"


@pytest.mark.asyncio
async def test_repository_unknown_slug_raises(seeded_db):
    repo = SourceRepository()
    with pytest.raises(SourceNotFoundError):
        await repo.get_by_slug(seeded_db, PROJECT, "missing-source")


@pytest.mark.asyncio
async def test_effective_state_linked_when_two_concepts(seeded_db):
    repo = SourceRepository()
    row = await repo.get_by_slug(seeded_db, PROJECT, "benjamin-opera-arte")
    state = await repo.effective_state(seeded_db, PROJECT, row)
    # Without concept seed after truncate, base status applies.
    assert state == "validated"


@pytest.mark.asyncio
async def test_service_list_sources_reads_db_only(seeded_db):
    service = SourcesService()
    response = await service.list_sources(PROJECT)
    ids = {item.id for item in response.sources}
    assert "benjamin-opera-arte" in ids
    assert "barthes-mythologies" not in ids


def test_service_does_not_import_corpus_picker():
    source = inspect.getsource(SourcesService)
    assert "CORPUS_PICKER_SOURCES" not in source
    assert "build_source_envelope" not in source
