"""/proposals HTTP adapter tests (M7, P-REVIEW-PERSIST-BE)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.schemas.chapter import ChapterCreate, ChapterRecord
from app.services.chapter import ChapterNotFoundError, ChapterService, ChapterWriteConflictError
from app.services.proposal.service import (
    InvalidProposalActionError,
    ProposalCreate,
    ProposalNotFoundError,
    ProposalNotPendingError,
    ProposalRecord,
    ProposalRow,
    ProposalService,
)

PROJECT = "thesis-agent"

_PROPOSALS_DDL = """
CREATE TABLE IF NOT EXISTS proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(64) NOT NULL,
    chapter_id UUID NOT NULL REFERENCES chapters(id),
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    original TEXT NOT NULL,
    proposed TEXT NOT NULL,
    action VARCHAR(32) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_proposals_project_chapter
    ON proposals (project_id, chapter_id);
"""


def _proposal(**kwargs) -> ProposalRecord:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id="prop-1",
        project_id=PROJECT,
        chapter_id="ch-1",
        status="pending",
        original="old text",
        proposed="new text",
        action="rewrite",
        created_at=now,
    )
    defaults.update(kwargs)
    return ProposalRecord(**defaults)


class FakeProposalService:
    async def create(self, data: ProposalCreate, *, session=None):
        if data.action not in ("rewrite", "verify", "expand", "find-sources"):
            raise InvalidProposalActionError(data.action)
        return _proposal(
            chapter_id=data.chapter_id,
            original=data.original,
            proposed=data.proposed,
            action=data.action,
        )

    async def list(self, *, project_id: str, chapter_id: str | None = None, session=None):
        item = _proposal(project_id=project_id, chapter_id=chapter_id or "ch-1")
        if chapter_id is not None and chapter_id != item.chapter_id:
            return []
        return [item]

    async def accept(self, proposal_id, data=None, *, session=None):
        if proposal_id == "missing":
            raise ProposalNotFoundError(proposal_id)
        if proposal_id == "resolved":
            raise ProposalNotPendingError(proposal_id, "accepted")
        if proposal_id == "bad-chapter":
            raise ChapterNotFoundError("missing-chapter")
        if proposal_id == "conflict":
            raise ChapterWriteConflictError("ch-1", expected_version=1, actual_version=2)
        now = datetime.now(timezone.utc)
        return ChapterRecord(
            id="ch-1",
            parent_id=None,
            order_index=0,
            title="Intro",
            status="draft",
            content_md="new text",
            summary=None,
            word_count=2,
            version=2,
            created_at=now,
            updated_at=now,
        )

    async def reject(self, proposal_id, data=None, *, session=None):
        if proposal_id == "missing":
            raise ProposalNotFoundError(proposal_id)
        if proposal_id == "resolved":
            raise ProposalNotPendingError(proposal_id, "rejected")
        return _proposal(id=proposal_id, status="rejected")


@pytest.fixture(scope="module", autouse=True)
def mount_proposals_router():
    import app.api.proposals as proposals_mod

    app.include_router(proposals_mod.router)
    yield


@pytest.fixture
def client(monkeypatch):
    import app.api.proposals as proposals_mod

    monkeypatch.setattr(proposals_mod, "_service", FakeProposalService())
    return TestClient(app)


@pytest.fixture
async def ensure_proposals_table(db_session):
    await db_session.execute(text(_PROPOSALS_DDL))
    await db_session.commit()


@pytest.fixture
def integration_client(monkeypatch, ensure_proposals_table):
    import app.api.proposals as proposals_mod

    monkeypatch.setattr(proposals_mod, "_service", ProposalService())
    return TestClient(app)


def test_create_proposal_201(client):
    r = client.post(
        "/proposals",
        json={
            "project_id": PROJECT,
            "chapter_id": "ch-1",
            "original": "old",
            "proposed": "new",
            "action": "rewrite",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["action"] == "rewrite"
    assert body["proposed"] == "new"


def test_create_invalid_action_422(client):
    r = client.post(
        "/proposals",
        json={
            "project_id": PROJECT,
            "chapter_id": "ch-1",
            "original": "old",
            "proposed": "new",
            "action": "summarize",
        },
    )
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_action"


def test_list_proposals(client):
    r = client.get("/proposals", params={"project_id": PROJECT, "chapter_id": "ch-1"})
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1


def test_accept_proposal(client):
    r = client.post("/proposals/prop-1/accept", json={"expected_chapter_version": 1})
    assert r.status_code == 200
    assert r.json()["chapter"]["content_md"] == "new text"
    assert r.json()["chapter"]["version"] == 2


def test_accept_not_found_404(client):
    r = client.post("/proposals/missing/accept", json={})
    assert r.status_code == 404
    assert r.json()["code"] == "proposal_not_found"


def test_accept_conflict_409(client):
    r = client.post("/proposals/conflict/accept", json={"expected_chapter_version": 1})
    assert r.status_code == 409
    assert r.json()["code"] == "write_conflict"


def test_accept_not_pending_422(client):
    r = client.post("/proposals/resolved/accept", json={})
    assert r.status_code == 422
    assert r.json()["code"] == "proposal_not_pending"


def test_reject_proposal(client):
    r = client.post("/proposals/prop-1/reject", json={"reason": "not needed"})
    assert r.status_code == 200
    assert r.json()["proposal"]["status"] == "rejected"


def test_reject_not_found_404(client):
    r = client.post("/proposals/missing/reject", json={})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_create_proposal_persists(integration_client, db_session):
    chapter_svc = ChapterService()
    chapter = await chapter_svc.create(
        ChapterCreate(title="Methods", content_md="Original paragraph."),
        session=db_session,
    )
    await db_session.commit()

    r = integration_client.post(
        "/proposals",
        json={
            "project_id": PROJECT,
            "chapter_id": chapter.id,
            "original": "Original paragraph.",
            "proposed": "Revised paragraph with clearer wording.",
            "action": "rewrite",
            "metadata": {"source": "test"},
        },
    )
    assert r.status_code == 201
    proposal_id = r.json()["id"]

    row = await db_session.get(ProposalRow, proposal_id)
    assert row is not None
    assert row.status == "pending"
    assert row.proposed.startswith("Revised")


@pytest.mark.asyncio
async def test_accept_updates_chapter_in_db(integration_client, db_session):
    chapter_svc = ChapterService()
    chapter = await chapter_svc.create(
        ChapterCreate(title="Results", content_md="Before accept."),
        session=db_session,
    )
    await db_session.commit()

    create = integration_client.post(
        "/proposals",
        json={
            "project_id": PROJECT,
            "chapter_id": chapter.id,
            "original": "Before accept.",
            "proposed": "After accept.",
            "action": "rewrite",
        },
    )
    proposal_id = create.json()["id"]

    accept = integration_client.post(
        f"/proposals/{proposal_id}/accept",
        json={"expected_chapter_version": 1},
    )
    assert accept.status_code == 200
    assert accept.json()["chapter"]["content_md"] == "After accept."
    assert accept.json()["chapter"]["version"] == 2

    refreshed = await chapter_svc.get(chapter.id, session=db_session)
    assert refreshed.content_md == "After accept."
    assert refreshed.version == 2

    row = await db_session.get(ProposalRow, proposal_id)
    assert row is not None
    assert row.status == "accepted"


@pytest.mark.asyncio
async def test_list_filters_by_chapter(integration_client, db_session):
    chapter_svc = ChapterService()
    ch_a = await chapter_svc.create(ChapterCreate(title="A", content_md="a"), session=db_session)
    ch_b = await chapter_svc.create(ChapterCreate(title="B", content_md="b"), session=db_session)
    await db_session.commit()

    svc = ProposalService()
    await svc.create(
        ProposalCreate(
            project_id=PROJECT,
            chapter_id=ch_a.id,
            original="a",
            proposed="a2",
            action="rewrite",
        ),
        session=db_session,
    )
    await svc.create(
        ProposalCreate(
            project_id=PROJECT,
            chapter_id=ch_b.id,
            original="b",
            proposed="b2",
            action="expand",
        ),
        session=db_session,
    )
    await db_session.commit()

    r = integration_client.get("/proposals", params={"project_id": PROJECT, "chapter_id": ch_a.id})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["chapter_id"] == ch_a.id


@pytest.mark.asyncio
async def test_reject_persists_status(integration_client, db_session):
    chapter_svc = ChapterService()
    chapter = await chapter_svc.create(ChapterCreate(title="Discussion", content_md="x"), session=db_session)
    await db_session.commit()

    proposal_id = integration_client.post(
        "/proposals",
        json={
            "project_id": PROJECT,
            "chapter_id": chapter.id,
            "original": "x",
            "proposed": "y",
            "action": "verify",
        },
    ).json()["id"]

    r = integration_client.post(f"/proposals/{proposal_id}/reject", json={"reason": "no change"})
    assert r.status_code == 200
    assert r.json()["proposal"]["status"] == "rejected"

    row = await db_session.get(ProposalRow, proposal_id)
    assert row is not None
    assert row.status == "rejected"
    assert row.metadata_.get("reject_reason") == "no change"
