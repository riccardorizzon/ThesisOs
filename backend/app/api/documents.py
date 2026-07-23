"""Thin HTTP adapter for documents — validation, DocumentService delegation, and
error mapping only. No DB session, no parsing, no storage here (spec §9, §13)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, File, Form, Query, UploadFile
from fastapi.responses import JSONResponse, Response

from app.schemas.document import DocumentListFilters, DocumentUpdate, DocumentUploadMetadata
from app.services.document import (
    DocumentNotFoundError,
    DocumentService,
    DocumentWriteConflictError,
    UnsupportedFormatError,
)
from app.services.retrieval import EmbedFailedError, RetrievalService, RetrievalServiceError

router = APIRouter()
_service = DocumentService()
_log = logging.getLogger("app.api.documents")


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


async def _parse_in_background(document_id: str) -> None:
    """Run parse then the M4 embed pipeline off the request path.

    A failed embedding must never silently succeed (M4 recovery): the error is
    logged and recorded on the document (`error_message`) so it stays visible.
    """
    try:
        record = await _service.parse(document_id)
    except Exception:
        _log.exception("background parse failed for %s", document_id)
        return
    if record.status != "parsed":
        return  # parse failure already recorded on the document (status=failed)
    try:
        from app.services.retrieval import RetrievalService

        await RetrievalService().embed_document(document_id)
    except Exception as exc:
        _log.error("background indexing failed for %s: %s", document_id, exc, exc_info=True)
        try:
            await _service.record_index_error(document_id, str(exc))
        except Exception:
            _log.exception("failed to record index error for %s", document_id)


@router.post("/upload", status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    author: str | None = Form(default=None),
    language: str | None = Form(default=None),
    project_id: str | None = Form(default=None),
):
    data = await file.read()
    meta = DocumentUploadMetadata(
        title=title, author=author, language=language, project_id=project_id
    )
    try:
        record = await _service.upload(
            filename=file.filename or "upload", data=data, meta=meta
        )
    except UnsupportedFormatError as exc:
        return _err(400, "unsupported_format", str(exc))
    background_tasks.add_task(_parse_in_background, record.id)
    return record


@router.get("/documents")
async def list_documents(
    project_id: str | None = None,
    source_type: str | None = None,
    status: str | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = DocumentListFilters(
        project_id=project_id,
        source_type=source_type,
        status=status,
        q=q,
        limit=limit,
        offset=offset,
    )
    return await _service.list(filters)


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    try:
        return await _service.get(document_id)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))


@router.patch("/documents/{document_id}")
async def update_document(document_id: str, body: DocumentUpdate):
    try:
        return await _service.update(document_id, body)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))
    except DocumentWriteConflictError as exc:
        return _err(409, "write_conflict", str(exc))


@router.delete("/documents/{document_id}", status_code=204, response_model=None)
async def delete_document(document_id: str):
    try:
        await _service.delete(document_id)
        return Response(status_code=204)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))


@router.get("/documents/{document_id}/chunks")
async def list_document_chunks(document_id: str):
    try:
        return await _service.list_chunks(document_id)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))


@router.get("/documents/{document_id}/versions")
async def list_document_versions(document_id: str):
    try:
        return await _service.list_versions(document_id)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))


@router.post("/documents/{document_id}/reparse", status_code=202)
async def reparse_document(document_id: str, background_tasks: BackgroundTasks):
    try:
        await _service.get(document_id)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))
    background_tasks.add_task(_parse_in_background, document_id)
    return {"document_id": document_id, "status": "processing"}


@router.post("/documents/{document_id}/index")
async def index_document(document_id: str):
    """Manual embed trigger for parsed documents (M4 spec §5.1)."""
    try:
        count = await RetrievalService().embed_document(document_id)
    except DocumentNotFoundError as exc:
        return _err(404, "document_not_found", str(exc))
    except EmbedFailedError as exc:
        return _err(422, "embed_failed", str(exc))
    except RetrievalServiceError as exc:
        return _err(400, "index_failed", str(exc))
    return {"document_id": document_id, "embedded": count, "status": "indexed"}
