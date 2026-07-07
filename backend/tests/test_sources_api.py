"""Sources module API tests (PX3-EWO-002; M7 DB-backed)."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app

client = TestClient(app)

_PROJECT = "thesis-agent"

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


async def _ensure_concept_seed() -> None:
    from app.db.session_async import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
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
        await session.commit()


@pytest.fixture(scope="session", autouse=True)
def _sources_api_db_seed(_test_db_ready):
    asyncio.run(_ensure_concept_seed())


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
