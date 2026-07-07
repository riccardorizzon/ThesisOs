"""Proposals API (M7) — persist writing proposals; accept applies chapter update."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.services.chapter import ChapterNotFoundError, ChapterWriteConflictError
from app.services.proposal.service import (
    InvalidProposalActionError,
    ProposalAcceptRequest,
    ProposalCreate,
    ProposalNotFoundError,
    ProposalNotPendingError,
    ProposalRejectRequest,
    ProposalService,
)

router = APIRouter()
_service = ProposalService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/proposals")
async def list_proposals(
    project_id: str = Query(min_length=1),
    chapter_id: str | None = None,
):
    items = await _service.list(project_id=project_id, chapter_id=chapter_id)
    return {"items": [item.model_dump(mode="json") for item in items]}


@router.post("/proposals", status_code=201)
async def create_proposal(body: ProposalCreate):
    try:
        record = await _service.create(body)
        return record.model_dump(mode="json")
    except InvalidProposalActionError as exc:
        return _err(422, "invalid_action", str(exc))


@router.post("/proposals/{proposal_id}/accept")
async def accept_proposal(proposal_id: str, body: ProposalAcceptRequest | None = None):
    try:
        chapter = await _service.accept(proposal_id, body)
        return {"chapter": chapter.model_dump(mode="json")}
    except ProposalNotFoundError as exc:
        return _err(404, "proposal_not_found", str(exc))
    except ProposalNotPendingError as exc:
        return _err(422, "proposal_not_pending", str(exc))
    except ChapterNotFoundError as exc:
        return _err(404, "chapter_not_found", str(exc))
    except ChapterWriteConflictError as exc:
        return _err(409, "write_conflict", str(exc))


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, body: ProposalRejectRequest | None = None):
    try:
        proposal = await _service.reject(proposal_id, body)
        return {"proposal": proposal.model_dump(mode="json")}
    except ProposalNotFoundError as exc:
        return _err(404, "proposal_not_found", str(exc))
    except ProposalNotPendingError as exc:
        return _err(422, "proposal_not_pending", str(exc))
