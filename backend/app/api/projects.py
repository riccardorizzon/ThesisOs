"""Projects API — Context Engine endpoint (ADR-0038)."""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas.companion_resume_packet import CompanionResumePacket
from app.schemas.context import (
    DEFAULT_PRODUCT_ID,
    DEFAULT_PROJECT_ID,
    ContextRequest,
    PresentationHint,
    ProjectContext,
)
from app.services.context import ContextService, ProjectNotFoundError
from app.services.memory.service import MemoryService
from app.services.workspace.companion_session import load_last_session_summary
from app.services.workspace.work_artifact import load_work_artifact, resume_block
from app.services.workspace.thesis_knowledge import (
    load_companion_resume,
    load_progress_summary,
    load_project_identity,
)
from app.services.workspace.thesis_sor import reconcile_thesis_agent_memory
from app.services.workspace.thesis_chapters import resolve_focus_chapter_id

router = APIRouter()
_service = ContextService()


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@router.get("/projects/{project_id}/context")
async def get_project_context(
    project_id: str,
    surface: str = Query(default="writing", description="Presentation hint only"),
    entity_type: str | None = None,
    entity_id: str | None = None,
    selection_anchor: str | None = None,
    product_id: str = Query(default=DEFAULT_PRODUCT_ID),
    workspace_id: str | None = None,
    session_id: str | None = None,
    user_intent: str | None = None,
):
    """Assemble ContextPacket. Surface is a presentation hint — not assembly driver."""
    request = ContextRequest(
        project=ProjectContext(
            project_id=project_id,
            product_id=product_id,
            workspace_id=workspace_id,
            session_id=session_id,
        ),
        presentation=PresentationHint(surface=surface),
        entity_type=entity_type,
        entity_id=entity_id,
        selection_anchor=selection_anchor,
        user_intent=user_intent,
    )
    try:
        return await _service.assemble(request)
    except ProjectNotFoundError as exc:
        return _err(404, "project_not_found", str(exc))


@router.get("/projects/{project_id}/companion/resume")
async def get_companion_resume(project_id: str):
    """Live companion resume — thesis-agent only; empty packet for other projects."""
    from app.services.project_registry import ProjectRegistryService

    registry = ProjectRegistryService()
    if not await registry.has(project_id):
        return _err(404, "project_not_found", f"Unknown project: {project_id}")

    if project_id != DEFAULT_PROJECT_ID:
        from app.schemas.companion_resume import CompanionResume

        entry = await registry.get(project_id)
        return CompanionResumePacket(
            project_id=project_id,
            title=entry.display_name if entry else project_id,
            author="",
            institution="",
            migration_run=None,
            progress_summary="Progetto vuoto — nessuna sessione precedente.",
            resume=CompanionResume(
                focus_chapter="",
                focus_section="",
                focus_section_title="",
                focus_status="",
                backlog=[],
                next_action="Definisci titolo e struttura della tesi",
                session_notes=[],
                key_decisions=[],
                section_text=None,
                last_session_summary=None,
            ),
            continue_prompt="Iniziamo questa tesi da zero.",
        )

    memory = MemoryService()
    await reconcile_thesis_agent_memory(memory, project_id=project_id)
    identity = load_project_identity()
    last_session = await load_last_session_summary(memory)
    art = await load_work_artifact(memory)
    resume = load_companion_resume(
        last_session_summary=last_session,
        work_artifact=resume_block(art),
    )
    focus_chapter_id = await resolve_focus_chapter_id(resume.focus_section)

    return CompanionResumePacket(
        project_id=project_id,
        title=identity.title,
        author=identity.author,
        institution=identity.institution,
        migration_run=identity.migration_run,
        progress_summary=load_progress_summary(),
        focus_chapter_id=focus_chapter_id,
        resume=resume,
    )
