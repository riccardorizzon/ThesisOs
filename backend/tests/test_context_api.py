"""GET /projects/{id}/context — Context Engine v0 (PX1-EWO-005)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chapter import ChapterListFilters, ChapterRecord
from app.schemas.context import (
    DEFAULT_PRODUCT_ID,
    DEFAULT_PROJECT_ID,
    ContextRequest,
    PresentationHint,
    ProjectContext,
)
from app.schemas.memory import PromptContext, PromptContextFilters, PromptMemoryItem
from uuid import uuid4


def _chapter(**kwargs) -> ChapterRecord:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id="ch-1",
        parent_id=None,
        order_index=0,
        title="Introduzione",
        status="draft",
        content_md="Primo paragrafo della tesi.",
        summary="Sintesi capitolo introduttivo",
        word_count=5,
        version=1,
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return ChapterRecord(**defaults)


class FakeMemoryService:
    async def load_prompt_context(
        self,
        *,
        conversation_id=None,
        max_tokens=None,
        filters: PromptContextFilters | None = None,
        session=None,
    ) -> PromptContext:
        filters = filters or PromptContextFilters()
        ctx = PromptContext(conversation_id=conversation_id)
        if filters.include_binding_decisions:
            ctx.decisions.append(
                PromptMemoryItem(
                    id="dec-binding",
                    kind="decision",
                    title="Decisions",
                    content="CORPUS-02 Barthes Mythologies escluso\nCORPUS-03 Bourriaud escluso",
                    version=1,
                    pinned=True,
                    key="decisions",
                )
            )
        if filters.include_pinned_thesis:
            ctx.thesis.append(
                PromptMemoryItem(
                    id="thesis-1",
                    kind="thesis",
                    title="STIGMATA — Design e processo creativo",
                    content="Tesi di laurea magistrale",
                    version=1,
                    pinned=True,
                    key="thesis",
                )
            )
        return ctx


class FakeChapterService:
    async def list(self, filters: ChapterListFilters | None = None, *, session=None):
        filters = filters or ChapterListFilters()
        # Primary / unspecified fixtures keep the progress sample; other projects are empty.
        if filters.project_id not in (None, DEFAULT_PROJECT_ID, "thesis-agent"):
            return []
        return [
            _chapter(id="ch-1", status="approved"),
            _chapter(id="ch-2", status="review", title="Quadro teorico"),
        ]

    async def get(self, chapter_id: str, *, session=None):
        if chapter_id == "missing":
            from app.services.chapter import ChapterNotFoundError

            raise ChapterNotFoundError(chapter_id)
        return _chapter(id=chapter_id, title=f"Capitolo {chapter_id}")


@pytest.fixture
def client(monkeypatch):
    from app.api import projects as projects_api
    from app.services.context.service import ContextService

    projects_api._service = ContextService(
        memory_service=FakeMemoryService(),
        chapter_service=FakeChapterService(),
    )
    return TestClient(app)


def test_get_context_returns_packet_subset(client):
    r = client.get(f"/projects/{DEFAULT_PROJECT_ID}/context?surface=writing")
    assert r.status_code == 200
    body = r.json()
    assert body["schema_version"] == "0.2"
    assert body["project"]["title"] == "Demo (esempio)"
    assert body["project"]["progress_pct"] == 85
    assert body["project_context"]["project_id"] == DEFAULT_PROJECT_ID
    assert body["project_context"]["product_id"] == DEFAULT_PRODUCT_ID
    assert body["presentation"]["surface"] == "writing"
    assert len(body["decisions"]) == 1
    assert body["decisions"][0]["binding"] is True
    assert any("CORPUS-02" in c for c in body["corpus_constraints"])
    assert len(body["writing_rules"]) >= 1
    assert body["token_budget"] == 8000
    assert len(body["concepts"]) >= 1
    assert any(c["slug"] == "stigmata" for c in body["concepts"])
    assert len(body["relevant_sources"]) >= 1


def test_get_context_includes_chapter_entity(client):
    r = client.get(
        f"/projects/{DEFAULT_PROJECT_ID}/context"
        "?surface=writing&entity_type=chapter&entity_id=ch-2"
    )
    assert r.status_code == 200
    entity = r.json()["entity"]
    assert entity["type"] == "chapter"
    assert entity["id"] == "ch-2"
    assert entity["title"] == "Capitolo ch-2"


def test_get_context_with_selection_anchor(client):
    r = client.get(
        f"/projects/{DEFAULT_PROJECT_ID}/context"
        "?surface=writing&entity_type=chapter&entity_id=ch-2&selection_anchor=%C2%A73.2"
    )
    assert r.status_code == 200
    body = r.json()
    assert body["selection_anchor"] == "§3.2"
    assert body["entity"]["id"] == "ch-2"


def test_get_context_without_selection_anchor_backward_compatible(client):
    r = client.get(f"/projects/{DEFAULT_PROJECT_ID}/context?surface=writing")
    assert r.status_code == 200
    assert r.json().get("selection_anchor") is None


def test_binding_decisions_precede_corpus_constraints(client):
    r = client.get(f"/projects/{DEFAULT_PROJECT_ID}/context?surface=writing")
    body = r.json()
    assert body["decisions"]
    assert body["corpus_constraints"]
    assert "CORPUS-02" in body["corpus_constraints"][0]


def test_unknown_project_returns_404(client):
    r = client.get("/projects/unknown-project/context")
    assert r.status_code == 404
    assert r.json()["code"] == "project_not_found"


def test_demo_project_context_ok(client):
    r = client.get("/projects/demo-thesis/context?surface=writing")
    assert r.status_code == 200
    body = r.json()
    assert body["project_context"]["project_id"] == "demo-thesis"
    assert body["decisions"] == []


def test_created_project_context_ok(client):
    stamp = uuid4().hex[:8]
    display_name = f"Nuova tesi CUR-7 {stamp}"
    created = client.post("/projects", json={"display_name": display_name}).json()
    pid = created["id"]
    r = client.get(f"/projects/{pid}/context?surface=agent")
    assert r.status_code == 200
    body = r.json()
    assert body["project_context"]["project_id"] == pid
    assert body["project"]["title"] == display_name
    assert body["project"]["progress_pct"] == 0
    assert body["project"]["phase"] == "Progetto vuoto"
    assert body["decisions"] == []
    assert body["writing_rules"] == []
    assert body["corpus_constraints"] == []


def test_surface_is_presentation_hint_not_assembly_driver(client):
    """Writing rules assembled regardless of surface — UI decides display."""
    home = client.get(f"/projects/{DEFAULT_PROJECT_ID}/context?surface=home").json()
    review = client.get(
        f"/projects/{DEFAULT_PROJECT_ID}/context?surface=review"
    ).json()
    assert home["presentation"]["surface"] == "home"
    assert review["presentation"]["surface"] == "review"
    assert len(home["writing_rules"]) >= 1
    assert home["writing_rules"] == review["writing_rules"]


def test_project_context_query_params(client):
    r = client.get(
        f"/projects/{DEFAULT_PROJECT_ID}/context"
        "?product_id=thesisos&workspace_id=ws-1&session_id=sess-1"
    )
    assert r.status_code == 200
    ctx = r.json()["project_context"]
    assert ctx["project_id"] == DEFAULT_PROJECT_ID
    assert ctx["product_id"] == "thesisos"
    assert ctx["workspace_id"] == "ws-1"
    assert ctx["session_id"] == "sess-1"


def test_resolve_project_context_stub():
    from app.services.context.exceptions import ProjectNotFoundError
    from app.services.context.project import resolve_project_context

    ctx = ProjectContext(project_id=DEFAULT_PROJECT_ID, product_id=DEFAULT_PRODUCT_ID)
    assert resolve_project_context(ctx) == ctx

    with pytest.raises(ProjectNotFoundError):
        resolve_project_context(ProjectContext(project_id="unknown"))


def test_flatten_context_packet_maps_graph_nodes():
    from app.schemas.context import (
        ConstraintsNode,
        ContextGraph,
        DecisionsNode,
        DecisionRef,
        ProjectSummary,
        WorkspaceNode,
    )
    from app.services.context.present import flatten_context_packet

    request = ContextRequest(
        project=ProjectContext(project_id=DEFAULT_PROJECT_ID),
        presentation=PresentationHint(surface="sources"),
    )
    graph = ContextGraph(
        decisions=DecisionsNode(
            binding=[DecisionRef(id="d1", summary="rule", binding=True)]
        ),
        constraints=ConstraintsNode(
            corpus=["CORPUS-02"],
            writing_rules=["Italiano accademico"],
        ),
        workspace=WorkspaceNode(
            project=ProjectSummary(title="T", phase="P", progress_pct=10)
        ),
    )
    packet = flatten_context_packet(request, graph)
    assert packet.decisions[0].id == "d1"
    assert packet.corpus_constraints == ["CORPUS-02"]
    assert packet.writing_rules == ["Italiano accademico"]
    assert packet.presentation.surface == "sources"
