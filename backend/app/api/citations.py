"""Citation validation API (PX6-EWO-002)."""

from fastapi import APIRouter

from app.schemas.citation import (
    CitationIssueOut,
    CitationValidateRequest,
    CitationValidateResponse,
)
from app.services.citation.validation import has_blocking_citation_issues, validate_citations

router = APIRouter()


@router.post("/citations/validate", response_model=CitationValidateResponse)
async def validate_citation_text(body: CitationValidateRequest) -> CitationValidateResponse:
    source_dicts = [s.model_dump() for s in body.sources]
    issues = validate_citations(body.text, source_dicts or None)
    return CitationValidateResponse(
        issues=[CitationIssueOut(**issue.__dict__) for issue in issues],
        blocking=has_blocking_citation_issues(body.text, source_dicts or None),
    )
