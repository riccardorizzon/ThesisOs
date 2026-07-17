"""Context graph assembly nodes (ADR-0038). Logic independent of presentation surface."""

from __future__ import annotations

import re

from app.schemas.context import (
    DEFAULT_PROJECT_ID,
    ConstraintsNode,
    ContextGraph,
    ContextRequest,
    DecisionRef,
    DecisionsNode,
    EntityScope,
    ProjectSummary,
    SessionNode,
    UserIntentNode,
    WorkspaceNode,
)
from app.schemas.chapter import ChapterListFilters
from app.schemas.memory import PromptContextFilters
from app.services.chapter import ChapterNotFoundError, ChapterService
from app.services.context.knowledge_bridge import assemble_knowledge_node
from app.services.memory import MemoryService
from app.services.project_registry import ProjectRegistryService

_STATUS_FACTOR = {"draft": 0.4, "review": 0.7, "approved": 1.0, "published": 1.0}

_DEFAULT_CORPUS_CONSTRAINTS = [
    "CORPUS-02: Barthes Mythologies — escluso dal corpus attivo",
    "CORPUS-03: Bourriaud / estetica relazionale — escluso",
    "CORPUS-04: Library-first obbligatorio prima di paragrafi teorici",
]

_DEFAULT_WRITING_RULES = [
    "Italiano accademico; termini da Terminology.md",
    "Corpus approvato only (Bibliography-Master)",
    "Seguire OUTLINE_MASTER — no sezioni non approvate",
    "Separazione autore (A) / tesi (B) nei paragrafi teorici",
]

_CORPUS_LINE_RE = re.compile(r"CORPUS-\d+[^\n|]*", re.IGNORECASE)


def _compute_progress_pct(chapters) -> int:
    if not chapters:
        return 0
    weighted = 0.0
    total_weight = 0.0
    for ch in chapters:
        factor = _STATUS_FACTOR.get(ch.status, 0.4)
        weighted += factor
        total_weight += 1.0
    if total_weight == 0:
        return 0
    return round((weighted / total_weight) * 100)


def _phase_label(pct: int, *, fashion_empty: bool = False) -> str:
    if pct == 0:
        return "Prima dei dieci minuti" if fashion_empty else "Progetto vuoto"
    if pct < 40:
        return "Struttura e impostazione"
    if pct < 70:
        return "Sviluppo argomentativo"
    if pct < 100:
        return "Revisione e rifinitura"
    return "Capitoli approvati"


def _extract_corpus_constraints(decisions_content: str) -> list[str]:
    found = [m.group(0).strip() for m in _CORPUS_LINE_RE.finditer(decisions_content)]
    if found:
        return found
    return list(_DEFAULT_CORPUS_CONSTRAINTS)


def _decisions_from_prompt(ctx) -> list[DecisionRef]:
    return [
        DecisionRef(
            id=item.id,
            title=item.title,
            summary=item.content,
            binding=True,
        )
        for item in ctx.decisions
    ]


async def assemble_context_graph(
    request: ContextRequest,
    *,
    memory_service: MemoryService,
    chapter_service: ChapterService,
) -> ContextGraph:
    """Build full context graph — surface/presentation does not affect assembly."""
    project_id = request.project.project_id
    is_primary = project_id == DEFAULT_PROJECT_ID
    registry = ProjectRegistryService()
    registry_entry = registry.get(project_id)

    if is_primary:
        binding_ctx = await memory_service.load_prompt_context(
            filters=PromptContextFilters(
                include_binding_decisions=True,
                include_editable=False,
                include_pinned_user=False,
                include_pinned_thesis=False,
            )
        )
        decisions = _decisions_from_prompt(binding_ctx)
        decisions_content = "\n".join(d.summary for d in decisions)
        corpus = _extract_corpus_constraints(decisions_content)
        writing_rules = list(_DEFAULT_WRITING_RULES)
    else:
        # Hard isolation: do not leak thesis-agent decisions/rules into other projects.
        decisions = []
        corpus = []
        writing_rules = []

    entity: EntityScope | None = None
    if request.entity_type == "chapter" and request.entity_id:
        try:
            chapter = await chapter_service.get(request.entity_id)
            if chapter.project_id == project_id:
                snippet = chapter.summary
                if snippet is None and chapter.content_md:
                    snippet = chapter.content_md[:200]
                entity = EntityScope(
                    type="chapter",
                    id=chapter.id,
                    title=chapter.title,
                    snippet=snippet,
                )
        except ChapterNotFoundError:
            pass

    chapters = await chapter_service.list(ChapterListFilters(project_id=project_id))
    progress_pct = _compute_progress_pct(chapters)

    knowledge = await assemble_knowledge_node(project_id)

    if registry_entry is not None:
        project_title = registry_entry.display_name
    elif is_primary:
        project_title = "Tesi STIGMATA"
    else:
        project_title = project_id

    return ContextGraph(
        decisions=DecisionsNode(binding=decisions),
        constraints=ConstraintsNode(
            corpus=corpus,
            writing_rules=writing_rules,
        ),
        knowledge=knowledge,
        workspace=WorkspaceNode(
            project=ProjectSummary(
                title=project_title,
                phase=_phase_label(progress_pct, fashion_empty=is_primary),
                progress_pct=progress_pct,
            ),
            entity=entity,
        ),
        session=SessionNode(),
        user_intent=UserIntentNode(intent=request.user_intent),
    )
