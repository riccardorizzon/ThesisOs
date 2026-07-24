"""Citation validation API (PX6-EWO-002)."""

from fastapi import APIRouter

from app.schemas.citation import (
    CitationIssueOut,
    CitationValidateRequest,
    CitationValidateResponse,
)
from app.services.citation.validation import has_blocking_citation_issues, validate_citations
from app.services.project_scope import resolve_project_id
from app.services.sources.service import SourcesService

router = APIRouter()
_sources = SourcesService()


@router.post("/citations/validate", response_model=CitationValidateResponse)
async def validate_citation_text(body: CitationValidateRequest) -> CitationValidateResponse:
    if body.sources is None:
        source_dicts = await _sources.approved_citation_refs(
            resolve_project_id(body.project_id)
        )
    else:
        source_dicts = [source.model_dump() for source in body.sources]
    issues = validate_citations(body.text, source_dicts)
    return CitationValidateResponse(
        issues=[CitationIssueOut(**issue.__dict__) for issue in issues],
        blocking=has_blocking_citation_issues(body.text, source_dicts),
    )
