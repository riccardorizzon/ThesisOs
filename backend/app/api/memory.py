"""Thin HTTP adapter for memory — validation, MemoryService delegation, error mapping only."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from app.schemas.memory import MemoryCreate, MemoryListFilters, MemoryUpdate
from app.services.memory import MemoryService
from app.services.memory.exceptions import (
    CannotDeleteSingletonError,
    MemoryNotFoundError,
    SingletonMemoryExistsError,
    WriteConflictError,
)

router = APIRouter()
_service = MemoryService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


async def _scope_error(memory_id: str, project_id: str | None) -> JSONResponse | None:
    """404 when the memory belongs to another thesis (ADR-0047 INV-MTW-2)."""
    if not project_id:
        return None
    record = await _service.get(memory_id)
    if record.project_id != project_id:
        return _err(404, "memory_not_found", f"Memory not found: {memory_id}")
    return None


@router.get("/memory")
async def list_memories(
    project_id: str | None = None,
    kind: str | None = None,
    key: str | None = None,
    pinned: bool | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    filters = MemoryListFilters(
        project_id=project_id, kind=kind, key=key, pinned=pinned, q=q, limit=limit, offset=offset
    )
    return await _service.list(filters)


@router.post("/memory", status_code=201)
async def create_memory(body: MemoryCreate):
    try:
        return await _service.create(body)
    except SingletonMemoryExistsError as exc:
        return _err(409, "singleton_exists", str(exc))
    except ValueError as exc:
        return _err(422, "invalid_kind", str(exc))


@router.get("/memory/{memory_id}")
async def get_memory(memory_id: str, project_id: str | None = None):
    try:
        record = await _service.get(memory_id)
        if project_id and record.project_id != project_id:
            return _err(404, "memory_not_found", f"Memory not found: {memory_id}")
        return record
    except MemoryNotFoundError as exc:
        return _err(404, "memory_not_found", str(exc))


@router.patch("/memory/{memory_id}")
async def update_memory(memory_id: str, body: MemoryUpdate, project_id: str | None = None):
    try:
        scope_err = await _scope_error(memory_id, project_id)
        if scope_err is not None:
            return scope_err
        return await _service.update(memory_id, body)
    except MemoryNotFoundError as exc:
        return _err(404, "memory_not_found", str(exc))
    except WriteConflictError as exc:
        return _err(409, "write_conflict", str(exc))


@router.delete("/memory/{memory_id}", status_code=204, response_model=None)
async def delete_memory(memory_id: str, project_id: str | None = None):
    try:
        scope_err = await _scope_error(memory_id, project_id)
        if scope_err is not None:
            return scope_err
        await _service.delete(memory_id)
        return Response(status_code=204)
    except MemoryNotFoundError as exc:
        return _err(404, "memory_not_found", str(exc))
    except CannotDeleteSingletonError as exc:
        return _err(400, "cannot_delete_singleton", str(exc))


@router.get("/memory/{memory_id}/versions")
async def list_memory_versions(memory_id: str, project_id: str | None = None):
    try:
        scope_err = await _scope_error(memory_id, project_id)
        if scope_err is not None:
            return scope_err
        return await _service.list_versions(memory_id)
    except MemoryNotFoundError as exc:
        return _err(404, "memory_not_found", str(exc))
