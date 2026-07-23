"""Context Engine service (ADR-0038) — graph assembly + presentation flattening."""

from __future__ import annotations

from app.schemas.context import ContextPacket, ContextRequest
from app.services.chapter import ChapterService
from app.services.context.graph import assemble_context_graph
from app.services.context.present import flatten_context_packet
from app.services.context.project import resolve_project_context
from app.services.memory import MemoryService


class ContextService:
    """Assembles ContextGraph then flattens to ContextPacket."""

    def __init__(
        self,
        *,
        memory_service: MemoryService | None = None,
        chapter_service: ChapterService | None = None,
    ) -> None:
        self._memory = memory_service or MemoryService()
        self._chapters = chapter_service or ChapterService()

    async def assemble(self, request: ContextRequest) -> ContextPacket:
        await resolve_project_context(request.project)

        graph = await assemble_context_graph(
            request,
            memory_service=self._memory,
            chapter_service=self._chapters,
        )
        return flatten_context_packet(request, graph)
