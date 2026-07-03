"""Context Engine DTOs (ADR-0038). PX-1 v0 — graph assembly + presentation hint."""

from __future__ import annotations

from pydantic import BaseModel, Field

CONTEXT_PACKET_VERSION = "0.2"
DEFAULT_PROJECT_ID = "thesis-agent"
DEFAULT_PRODUCT_ID = "thesisos"
DEFAULT_TOKEN_BUDGET = 8000


class ProjectContext(BaseModel):
    """Multi-product scope — PX1-EWO-006 foundation."""

    project_id: str
    product_id: str = DEFAULT_PRODUCT_ID
    workspace_id: str | None = None
    session_id: str | None = None


class PresentationHint(BaseModel):
    """UI-only surface hint — does not drive assembly logic (ADR-0038)."""

    surface: str = "writing"


class ProjectSummary(BaseModel):
    title: str
    phase: str
    progress_pct: int = Field(ge=0, le=100)


class EntityScope(BaseModel):
    type: str
    id: str
    title: str
    snippet: str | None = None


class SourceRef(BaseModel):
    id: str
    title: str
    kind: str | None = None


class ConceptRef(BaseModel):
    id: str
    title: str
    slug: str | None = None


class DecisionRef(BaseModel):
    id: str
    title: str | None = None
    summary: str
    binding: bool = True


class DefinitionRef(BaseModel):
    term: str
    definition: str


class CitationRef(BaseModel):
    id: str
    label: str
    source_id: str | None = None


class ActivityRef(BaseModel):
    entity_type: str
    title: str
    href: str | None = None


class DecisionsNode(BaseModel):
    binding: list[DecisionRef] = Field(default_factory=list)


class ConstraintsNode(BaseModel):
    corpus: list[str] = Field(default_factory=list)
    writing_rules: list[str] = Field(default_factory=list)


class KnowledgeNode(BaseModel):
    concepts: list[ConceptRef] = Field(default_factory=list)
    definitions: list[DefinitionRef] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    citations: list[CitationRef] = Field(default_factory=list)


class WorkspaceNode(BaseModel):
    project: ProjectSummary
    entity: EntityScope | None = None


class SessionNode(BaseModel):
    memory_proposals_pending: int = 0
    recent_activity: list[ActivityRef] = Field(default_factory=list)


class UserIntentNode(BaseModel):
    intent: str | None = None


class ContextGraph(BaseModel):
    """Assembly graph — same engine for Chat, Writing, Sources, Review."""

    decisions: DecisionsNode = Field(default_factory=DecisionsNode)
    constraints: ConstraintsNode = Field(default_factory=ConstraintsNode)
    knowledge: KnowledgeNode = Field(default_factory=KnowledgeNode)
    workspace: WorkspaceNode
    session: SessionNode = Field(default_factory=SessionNode)
    user_intent: UserIntentNode = Field(default_factory=UserIntentNode)


class ContextRequest(BaseModel):
    project: ProjectContext
    presentation: PresentationHint = Field(default_factory=PresentationHint)
    entity_type: str | None = None
    entity_id: str | None = None
    user_intent: str | None = None


class ContextPacket(BaseModel):
    """Flattened view for API consumers. UI selects what to display via presentation."""

    schema_version: str = CONTEXT_PACKET_VERSION
    project_context: ProjectContext
    presentation: PresentationHint
    project: ProjectSummary
    entity: EntityScope | None = None
    relevant_sources: list[SourceRef] = Field(default_factory=list)
    concepts: list[ConceptRef] = Field(default_factory=list)
    decisions: list[DecisionRef] = Field(default_factory=list)
    definitions: list[DefinitionRef] = Field(default_factory=list)
    citations_available: list[CitationRef] = Field(default_factory=list)
    corpus_constraints: list[str] = Field(default_factory=list)
    writing_rules: list[str] = Field(default_factory=list)
    memory_proposals_pending: int = 0
    recent_activity: list[ActivityRef] = Field(default_factory=list)
    token_budget: int = DEFAULT_TOKEN_BUDGET
