"""Knowledge Object envelope DTOs (PX-3, ADR-0037)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

KnowledgeObjectType = Literal["concept", "source"]
KnowledgeState = Literal[
    "candidate",
    "validated",
    "linked",
    "referenced",
    "deprecated",
]
ConfidenceLevel = Literal["alta", "media", "bassa", "non_valutata"]
CreatedBy = Literal["operatore", "importazione", "estrazione", "ai"]
ProposalState = Literal["nessuna", "in_attesa", "approvata", "rifiutata"]

KNOWLEDGE_STATE_LABELS: dict[KnowledgeState, str] = {
    "candidate": "Candidato",
    "validated": "Validato",
    "linked": "Collegato",
    "referenced": "Citato in tesi",
    "deprecated": "Deprecato",
}

CONFIDENCE_LABELS: dict[ConfidenceLevel, str] = {
    "alta": "Alta",
    "media": "Media",
    "bassa": "Bassa",
    "non_valutata": "Non valutata",
}


class LinkedCounts(BaseModel):
    sources: int = 0
    chapters: int = 0
    concepts: int = 0
    decisions: int = 0
    authors: int = 0
    citations: int = 0


class KnowledgeObjectEnvelope(BaseModel):
    """Shared envelope per px3-knowledge-experience-v2 §3.1."""

    id: str
    slug: str
    type: KnowledgeObjectType
    title: str
    subtitle: str | None = None
    summary: str | None = None
    confidence: ConfidenceLevel = "non_valutata"
    knowledge_state: KnowledgeState
    linked_counts: LinkedCounts = Field(default_factory=LinkedCounts)
    created_by: CreatedBy = "importazione"
    proposal_state: ProposalState = "nessuna"
    is_core: bool = False


class KnowledgeObjectListResponse(BaseModel):
    objects: list[KnowledgeObjectEnvelope]
    total: int


class ConceptDetailEnvelope(KnowledgeObjectEnvelope):
    """Explain Page concept detail — region B definition (PX3-EWO-005)."""

    definition: str | None = None


class ConceptHeaderEnvelope(BaseModel):
    """Explain Page region A — header bar (PX3-EWO-006)."""

    id: str
    slug: str
    title: str
    subtitle: str | None = None
    confidence: ConfidenceLevel = "non_valutata"
    knowledge_state: KnowledgeState
    is_core: bool = False


class ConceptDefinitionEnvelope(BaseModel):
    """Explain Page region B — definition block (PX3-EWO-006)."""

    slug: str
    definition: str | None = None
    source_count: int = 0


class RelatedConceptRef(BaseModel):
    id: str
    slug: str
    title: str


class SourceListItem(KnowledgeObjectEnvelope):
    related_concepts: list[RelatedConceptRef] = Field(default_factory=list)
    corpus_status: str | None = None
    document_id: str | None = None
    deletable: bool = False


class SourceListResponse(BaseModel):
    sources: list[SourceListItem]
    total: int


class ConceptCreate(BaseModel):
    """Create payload for PX-4 concept CRUD (ADR-0037)."""

    slug: str = Field(min_length=1, max_length=128, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    subtitle: str | None = None
    summary: str | None = None
    definition: str | None = None
    confidence: ConfidenceLevel = "non_valutata"
    is_core: bool = False
    created_by: CreatedBy = "operatore"
    source_slugs: list[str] = Field(default_factory=list)


class ConceptUpdate(BaseModel):
    """Partial update for an existing concept."""

    title: str | None = None
    subtitle: str | None = None
    summary: str | None = None
    definition: str | None = None
    confidence: ConfidenceLevel | None = None
    knowledge_state: KnowledgeState | None = None
    is_core: bool | None = None
    proposal_state: ProposalState | None = None
    source_slugs: list[str] | None = None
