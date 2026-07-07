"""Read-only knowledge catalog — corpus + concepts (PX3-EWO-001)."""

from __future__ import annotations

from app.graph.corpus_query import CORPUS_PICKER_SOURCES
from app.schemas.knowledge import (
    KnowledgeObjectEnvelope,
    KnowledgeObjectType,
    KnowledgeState,
    LinkedCounts,
)
CONCEPT_CATALOG: tuple[dict[str, object], ...] = (
    {
        "id": "stigmata",
        "title": "STIGMATA",
        "subtitle": "Framework centrale della tesi",
        "summary": "Segno percettivo che condensa significato culturale — asse teorico del corpus.",
        "related_source_ids": (
            "barthes-mythologies",
            "albers-interaction-color",
            "hollander-sex-suits",
        ),
        "is_core": True,
        "confidence": "alta",
    },
    {
        "id": "aura",
        "title": "Aura",
        "subtitle": "Benjamin — unicità dell'originale",
        "summary": "Presenza unica dell'oggetto nel tempo e nello spazio — erode con la riproducibilità.",
        "related_source_ids": ("benjamin-opera-arte",),
        "is_core": True,
        "confidence": "alta",
    },
    {
        "id": "riproducibilita",
        "title": "Riproducibilità tecnica",
        "subtitle": "Meccanica della diffusione visiva",
        "summary": "Diffusione tecnica che altera la percezione dell'originale.",
        "related_source_ids": ("benjamin-opera-arte",),
        "is_core": False,
        "confidence": "media",
    },
    {
        "id": "percezione",
        "title": "Percezione visiva",
        "subtitle": "Intersezione colore, forma, corpo",
        "summary": "Asse che collega esperienza estetica e pratica visiva.",
        "related_source_ids": ("albers-interaction-color", "csikszentmihalyi-flow"),
        "is_core": False,
        "confidence": "media",
    },
    {
        "id": "mito",
        "title": "Mito borghese",
        "subtitle": "Barthes — naturalizzazione ideologica",
        "summary": "Sistema di comunicazione che naturalizza il significato ideologico.",
        "related_source_ids": ("barthes-mythologies",),
        "is_core": False,
        "confidence": "bassa",
    },
    {
        "id": "abbigliamento",
        "title": "Abbigliamento come segno",
        "subtitle": "Moda e identità visiva",
        "summary": "Il vestire come segno culturale e identitario.",
        "related_source_ids": ("hollander-sex-suits",),
        "is_core": False,
        "confidence": "media",
    },
    {
        "id": "esperienza",
        "title": "Esperienza estetica",
        "subtitle": "Flow e coinvolgimento percettivo",
        "summary": "Stato di coinvolgimento totale nell'attività percettiva.",
        "related_source_ids": ("csikszentmihalyi-flow",),
        "is_core": False,
        "confidence": "media",
    },
)

_SOURCE_STATUS_TO_STATE: dict[str, KnowledgeState] = {
    "candidata": "candidate",
    "approvata": "validated",
    "esclusa": "deprecated",
}


def _source_knowledge_state(status: str, concept_count: int) -> KnowledgeState:
    base = _SOURCE_STATUS_TO_STATE.get(status, "candidate")
    if base == "deprecated":
        return "deprecated"
    if concept_count >= 2:
        return "linked"
    return base


def _concept_knowledge_state(related_source_count: int) -> KnowledgeState:
    if related_source_count >= 2:
        return "linked"
    if related_source_count == 1:
        return "validated"
    return "candidate"


def _concept_ids_for_source(source_id: str) -> tuple[str, ...]:
    return tuple(
        str(entry["id"])
        for entry in CONCEPT_CATALOG
        if source_id in entry.get("related_source_ids", ())
    )


def _source_ids_for_concept(concept_id: str) -> tuple[str, ...]:
    for entry in CONCEPT_CATALOG:
        if entry["id"] == concept_id:
            return tuple(str(x) for x in entry.get("related_source_ids", ()))
    return ()


def build_source_envelope(entry: dict[str, str]) -> KnowledgeObjectEnvelope:
    concept_ids = _concept_ids_for_source(entry["id"])
    status = entry.get("status", "candidata")
    return KnowledgeObjectEnvelope(
        id=entry["id"],
        slug=entry["id"],
        type="source",
        title=entry["title"],
        subtitle=entry.get("author"),
        summary=f"{entry.get('year', '')} · Fonte bibliografica".strip(" ·"),
        confidence="non_valutata",
        knowledge_state=_source_knowledge_state(status, len(concept_ids)),
        linked_counts=LinkedCounts(concepts=len(concept_ids)),
        created_by="importazione",
        is_core=False,
    )


def build_concept_envelope(entry: dict[str, object]) -> KnowledgeObjectEnvelope:
    related = _source_ids_for_concept(str(entry["id"]))
    return KnowledgeObjectEnvelope(
        id=str(entry["id"]),
        slug=str(entry["id"]),
        type="concept",
        title=str(entry["title"]),
        subtitle=str(entry.get("subtitle") or ""),
        summary=str(entry.get("summary") or ""),
        confidence=entry.get("confidence", "non_valutata"),  # type: ignore[arg-type]
        knowledge_state=_concept_knowledge_state(len(related)),
        linked_counts=LinkedCounts(sources=len(related)),
        created_by="operatore",
        is_core=bool(entry.get("is_core", False)),
    )


def get_related_concepts_for_source(source_id: str) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for concept_id in _concept_ids_for_source(source_id):
        for entry in CONCEPT_CATALOG:
            if entry["id"] == concept_id:
                refs.append(
                    {
                        "id": str(entry["id"]),
                        "slug": str(entry["id"]),
                        "title": str(entry["title"]),
                    }
                )
                break
    return refs


def list_knowledge_objects(
    *,
    object_type: KnowledgeObjectType | None = None,
    include_deprecated: bool = False,
) -> list[KnowledgeObjectEnvelope]:
    items: list[KnowledgeObjectEnvelope] = []

    if object_type in (None, "source"):
        for raw in CORPUS_PICKER_SOURCES:
            envelope = build_source_envelope(raw)
            if not include_deprecated and envelope.knowledge_state == "deprecated":
                continue
            items.append(envelope)

    return items


def get_knowledge_object(slug: str) -> KnowledgeObjectEnvelope | None:
    for raw in CORPUS_PICKER_SOURCES:
        if raw["id"] == slug:
            return build_source_envelope(raw)
    for raw in CONCEPT_CATALOG:
        if raw["id"] == slug:
            return build_concept_envelope(raw)
    return None
