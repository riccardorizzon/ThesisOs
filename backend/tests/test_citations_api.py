from fastapi.testclient import TestClient

from app.db import models
from app.main import app


async def test_citation_validation_uses_only_approved_sources_in_active_project(
    db_session,
):
    db_session.add_all(
        [
            models.Source(
                project_id="thesis-citation-a",
                type="book",
                slug="benjamin-a",
                title="Opera d’arte",
                subtitle="Walter Benjamin",
                year=1936,
                corpus_status="approvata",
            ),
            models.Source(
                project_id="thesis-citation-b",
                type="book",
                slug="albers-b",
                title="Interaction of Color",
                subtitle="Josef Albers",
                year=1963,
                corpus_status="approvata",
            ),
        ]
    )
    await db_session.commit()

    client = TestClient(app)
    linked = client.post(
        "/citations/validate",
        json={
            "project_id": "thesis-citation-a",
            "text": "L’aura cambia (Benjamin, 1936).",
        },
    )
    foreign = client.post(
        "/citations/validate",
        json={
            "project_id": "thesis-citation-b",
            "text": "L’aura cambia (Benjamin, 1936).",
        },
    )

    assert linked.status_code == 200
    assert linked.json() == {"issues": [], "blocking": False}
    assert foreign.status_code == 200
    assert foreign.json()["blocking"] is True
    assert foreign.json()["issues"][0]["code"] == "unlinked_author_date"


async def test_citation_validation_ignores_candidate_sources(db_session):
    db_session.add(
        models.Source(
            project_id="thesis-citation-candidate",
            type="upload",
            slug="candidate-benjamin",
            title="Opera d’arte",
            subtitle="Walter Benjamin",
            year=1936,
            corpus_status="candidata",
        )
    )
    await db_session.commit()

    response = TestClient(app).post(
        "/citations/validate",
        json={
            "project_id": "thesis-citation-candidate",
            "text": "(Benjamin, 1936)",
        },
    )

    assert response.status_code == 200
    assert response.json()["blocking"] is True
