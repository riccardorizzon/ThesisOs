"""Compose transient LLM prompt wire from graph state (M4 grounding recovery).

Centralizes prompt assembly so conversation_node stays thin and future
components (memory, grounding, …) can be added in one place without ad-hoc
injection in the graph node.
"""

from __future__ import annotations

from app.graph.academic_production import (
    ACADEMIC_CITATION_INSTRUCTION,
    ACADEMIC_FEW_SHOT,
    ACADEMIC_GROUNDING_PREAMBLE,
    ACADEMIC_INFERENCE_ENFORCEMENT,
    ACADEMIC_PRODUCTION_BLOCK,
    NUMERIC_CITATION_INSTRUCTION,
    format_source_header,
    is_academic_writing_query,
)
from app.graph.corpus_query import is_corpus_list_query
from app.schemas.graph_state import GraphState, Message, RetrievedChunk


def render_grounding_prompt(
    chunks: list[RetrievedChunk],
    *,
    has_binding_decisions: bool = False,
    is_corpus_list_query: bool = False,
    academic_writing: bool = False,
) -> str:
    """Render retrieved chunks as a numbered, citable source block."""
    cite_rule = ACADEMIC_CITATION_INSTRUCTION if academic_writing else NUMERIC_CITATION_INSTRUCTION
    if academic_writing:
        lines = [ACADEMIC_GROUNDING_PREAMBLE + cite_rule]
        lines.append(ACADEMIC_PRODUCTION_BLOCK.strip())
        lines.append(ACADEMIC_FEW_SHOT.strip())
        lines.append(ACADEMIC_INFERENCE_ENFORCEMENT.strip())
    else:
        lines = [
            "Answer the user's question using the numbered sources below, which were "
            "retrieved from the user's uploaded documents. Prefer these sources and cite "
            f"{cite_rule}",
        ]
    if has_binding_decisions:
        lines.append(
            "Persistent [BINDING DECISIONS] above take precedence over contradictory "
            "numbered sources. Apply frozen corpus exclusions (e.g. CORPUS-02 Mythologies, "
            "CORPUS-03 Bourriaud) even when a retrieved source mentions an excluded work."
        )
    if is_corpus_list_query:
        lines.append(
            "For corpus author listings: classify roles using Bibliography-Master sections "
            "A.1 (FONDAMENTALE), A.2 (SUPPORTO), and A.3 (PERIFERICO). List all ~12 active "
            "authors (CORPUS-01) with opera and capitoli tesi when present in the sources. "
            "Do not label support or peripheral authors as FONDAMENTALE."
        )
    lines.extend(
        [
            "If the sources do not contain the answer, say so explicitly — except for "
            "topics already fixed by [BINDING DECISIONS] or other persistent memory above.",
            "",
            "Sources:",
        ]
    )
    for i, chunk in enumerate(chunks, 1):
        header = format_source_header(i, chunk, academic_writing=academic_writing)
        lines.append(f"{header}\n{chunk.content.strip()}")
    return "\n".join(lines)


def _split_transient_prefix(messages: list[Message]) -> tuple[list[Message], list[Message]]:
    """Leading system messages prepended by upstream nodes (e.g. M2 memory)."""
    prefix: list[Message] = []
    rest = list(messages)
    while rest and rest[0].role == "system":
        prefix.append(rest.pop(0))
    return prefix, rest


def _last_user_message(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


def compose_prompt_wire(state: GraphState) -> list[Message]:
    """Build the full transient wire: memory + grounding + conversation history."""
    memory_prefix, conversation = _split_transient_prefix(state.messages)
    sections: list[str] = [m.content for m in memory_prefix if m.content.strip()]
    has_binding = any("[BINDING DECISIONS]" in s for s in sections)
    user_query = _last_user_message(conversation)
    corpus_list = is_corpus_list_query(user_query or "")
    academic = is_academic_writing_query(user_query or "") and not corpus_list
    if state.retrieved_context:
        sections.append(
            render_grounding_prompt(
                state.retrieved_context,
                has_binding_decisions=has_binding,
                is_corpus_list_query=corpus_list,
                academic_writing=academic,
            )
        )

    wire: list[Message] = []
    if sections:
        wire.append(Message(role="system", content="\n\n".join(sections)))
    wire.extend(conversation)
    return wire


def format_grounding_sources(chunks: list[RetrievedChunk]) -> list[dict]:
    """Reference metadata for client/SSE consumers (transient, not persisted)."""
    return [
        {
            "index": i,
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "document_title": c.document_title,
            "page_from": c.page_from,
            "score": c.score,
        }
        for i, c in enumerate(chunks, 1)
    ]
