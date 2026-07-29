"""Dedupe upload+catalog doubles that share document_id (pre-M7 Grounding solidity)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.schemas.knowledge import SourceListItem
from app.services.sources.service import dedupe_sources_by_document

client = TestClient(app)

_DOC = "56e7fbe5-34eb-4d2e-b0cc-e220a5f515cf"
_PROJECT = "thesis-agent"


def _item(**kwargs) -> SourceListItem:
    base = dict(
        id="x",
        slug="x",
        type="source",
        title="T",
        subtitle=None,
        summary=None,
        confidence="non_valutata",
        knowledge_state="candidate",
        linked_counts={"concepts": 0, "notes": 0, "chapters": 0},
        created_by="importazione",
        is_core=False,
        related_concepts=[],
        corpus_status="candidata",
        document_id=None,
        deletable=False,
    )
    base.update(kwargs)
    return SourceListItem(**base)


def test_dedupe_prefers_catalog_linked_over_uuid_upload():
    upload = _item(
        id=_DOC,
        slug=_DOC,
        title="Benjamin_Opera-Arte-Riproducibilita",
        knowledge_state="candidate",
        corpus_status="candidata",
        document_id=_DOC,
        deletable=True,
    )
    catalog = _item(
        id="benjamin-opera-arte",
        slug="benjamin-opera-arte",
        title="L'opera d'arte nell'epoca della riproducibilità tecnica",
        knowledge_state="linked",
        corpus_status="approvata",
        document_id=_DOC,
    )
    out = dedupe_sources_by_document([upload, catalog])
    assert len(out) == 1
    assert out[0].slug == "benjamin-opera-arte"


def test_dedupe_keeps_rows_without_document_id():
    a = _item(id="a", slug="a", title="A", document_id=None)
    b = _item(id="b", slug="b", title="B", document_id=None)
    assert len(dedupe_sources_by_document([a, b])) == 2


@pytest.mark.asyncio
async def test_list_api_hides_upload_duplicate_of_catalog(db_session):
    """Live-shaped double: catalog benjamin + upload slug=document_id."""
    await db_session.execute(
        text(
            """
            INSERT INTO documents (
                id, project_id, title, source_type, status, version
            ) VALUES (
                CAST(:doc AS uuid), :project_id, 'Benjamin upload', 'pdf', 'ready', 1
            )
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"project_id": _PROJECT, "doc": _DOC},
    )
    await db_session.execute(
        text(
            """
            INSERT INTO sources (
                project_id, slug, type, document_id, title, subtitle, summary,
                corpus_status, confidence, knowledge_state, is_core, created_by, authors
            ) VALUES (
                :project_id, 'benjamin-opera-arte', 'catalog', CAST(:doc AS uuid),
                'L''opera d''arte', 'Walter Benjamin', '1936',
                'approvata', 'alta', 'candidate', false, 'importazione', '[]'::jsonb
            )
            ON CONFLICT (project_id, slug) DO UPDATE SET
                document_id = EXCLUDED.document_id,
                corpus_status = 'approvata'
            """
        ),
        {"project_id": _PROJECT, "doc": _DOC},
    )
    await db_session.execute(
        text(
            """
            INSERT INTO sources (
                project_id, slug, type, document_id, title, subtitle, summary,
                corpus_status, confidence, knowledge_state, is_core, created_by, authors
            ) VALUES (
                :project_id, :slug, 'upload', CAST(:doc AS uuid),
                'Benjamin_Opera-Arte-Riproducibilita', null, 'Caricato',
                'candidata', 'non_valutata', 'candidate', false, 'importazione', '[]'::jsonb
            )
            ON CONFLICT (project_id, slug) DO NOTHING
            """
        ),
        {"project_id": _PROJECT, "slug": _DOC, "doc": _DOC},
    )
    await db_session.commit()

    res = client.get(f"/projects/{_PROJECT}/sources", params={"q": "Benjamin"})
    assert res.status_code == 200
    sources = res.json()["sources"]
    assert len(sources) == 1
    assert sources[0]["id"] == "benjamin-opera-arte"
