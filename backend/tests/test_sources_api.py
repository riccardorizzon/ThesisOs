"""Sources module API tests (PX3-EWO-002; M7 DB-backed)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app

client = TestClient(app)

_PROJECT = "thesis-agent"

_SOURCE_SEED_ROWS: tuple[tuple[str, str, str, int, str], ...] = (
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

# Minimal PX-4 / 0006 concept seed for DB-backed related_concepts (no catalog fallback).
_CONCEPT_SEED: tuple[tuple[str, str, str, str, bool, str, tuple[str, ...]], ...] = (
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
)


def _knowledge_state(link_count: int) -> str:
    if link_count >= 2:
        return "linked"
    return "validated"


async def _ensure_source_seed(session) -> None:
    count = int(
        (
            await session.execute(
                text(
                    "SELECT COUNT(*) FROM sources WHERE project_id = :project_id"
                ),
                {"project_id": _PROJECT},
            )
        ).scalar_one()
    )
    if count > 0:
        return
    for slug, title, author, year, corpus_status in _SOURCE_SEED_ROWS:
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
                "project_id": _PROJECT,
                "slug": slug,
                "title": title,
                "subtitle": author,
                "summary": summary,
                "year": year,
                "authors": f'[{{"literal": "{author}"}}]',
                "corpus_status": corpus_status,
            },
        )


async def _ensure_concept_seed(session) -> None:
    count = int(
        (await session.execute(text("SELECT COUNT(*) FROM concepts"))).scalar_one()
    )
    if count > 0:
        return
    for slug, title, subtitle, summary, is_core, confidence, source_slugs in _CONCEPT_SEED:
        state = _knowledge_state(len(source_slugs))
        result = await session.execute(
            text(
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
                "project_id": _PROJECT,
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
            await session.execute(
                text(
                    """
                    INSERT INTO concept_source_links (concept_id, source_slug)
                    VALUES (:concept_id, :source_slug)
                    """
                ),
                {"concept_id": concept_id, "source_slug": source_slug},
            )


@pytest.fixture(autouse=True)
async def _sources_api_db_seed(db_session):
    await _ensure_source_seed(db_session)
    await _ensure_concept_seed(db_session)
    await db_session.commit()


def test_list_sources_default_omits_deprecated():
    res = client.get("/projects/thesis-agent/sources")
    assert res.status_code == 200
    body = res.json()
    ids = {s["id"] for s in body["sources"]}
    assert "barthes-mythologies" not in ids
    assert "benjamin-opera-arte" in ids


def test_list_sources_include_related_concepts():
    res = client.get("/projects/thesis-agent/sources")
    benjamin = next(
        s for s in res.json()["sources"] if s["id"] == "benjamin-opera-arte"
    )
    assert len(benjamin["related_concepts"]) >= 1
    assert benjamin["related_concepts"][0]["slug"] == "aura"


def test_list_sources_search():
    res = client.get(
        "/projects/thesis-agent/sources",
        params={"q": "Benjamin"},
    )
    assert res.status_code == 200
    assert len(res.json()["sources"]) == 1


def test_list_sources_filter_state():
    res = client.get(
        "/projects/thesis-agent/sources",
        params={"state": "linked", "include_deprecated": "true"},
    )
    assert res.status_code == 200
    assert all(s["knowledge_state"] == "linked" for s in res.json()["sources"])


def test_get_source_detail_with_concepts():
    res = client.get("/projects/thesis-agent/sources/benjamin-opera-arte")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == "benjamin-opera-arte"
    assert any(c["slug"] == "aura" for c in body["related_concepts"])


def test_get_source_not_found():
    res = client.get("/projects/thesis-agent/sources/missing-source")
    assert res.status_code == 404


def test_add_candidate_source_to_bibliography_is_idempotent():
    first = client.post(
        "/projects/thesis-agent/sources/albers-interaction-color/bibliography"
    )
    second = client.post(
        "/projects/thesis-agent/sources/albers-interaction-color/bibliography"
    )

    assert first.status_code == 200
    assert first.json()["corpus_status"] == "approvata"
    assert second.status_code == 200
    assert second.json()["corpus_status"] == "approvata"


def test_add_source_to_bibliography_is_project_scoped():
    response = client.post(
        "/projects/other-project/sources/albers-interaction-color/bibliography"
    )
    assert response.status_code == 404
    assert response.json()["code"] == "source_not_found"


def test_export_bibliography_bibtex_from_db():
    res = client.get("/projects/thesis-agent/sources/bibliography/export")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/x-bibtex")
    assert "attachment" in res.headers.get("content-disposition", "")
    text = res.text
    assert "@book{" in text
    assert "Benjamin" in text
    assert "Hollander" in text
    assert "Barthes" not in text


def test_delete_catalog_source_forbidden():
    res = client.delete("/projects/thesis-agent/sources/benjamin-opera-arte")
    assert res.status_code == 403
    assert res.json()["code"] == "source_not_deletable"


def test_delete_upload_source_round_trip():
    upload = client.post(
        "/upload",
        files={"file": ("delete-me.pdf", b"%PDF-1.4", "application/pdf")},
        data={"title": "Fonte da eliminare"},
    )
    assert upload.status_code == 201
    doc_id = upload.json()["id"]

    listed = client.get("/projects/thesis-agent/sources")
    assert listed.status_code == 200
    assert any(s["slug"] == doc_id for s in listed.json()["sources"])

    deleted = client.delete(f"/projects/thesis-agent/sources/{doc_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/projects/thesis-agent/sources/{doc_id}")
    assert missing.status_code == 404

    doc = client.get(f"/documents/{doc_id}")
    assert doc.status_code == 404
