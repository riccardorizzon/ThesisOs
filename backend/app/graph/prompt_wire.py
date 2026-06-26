"""Compose transient LLM prompt wire from graph state (M4 grounding recovery).

Centralizes prompt assembly so conversation_node stays thin and future
components (memory, grounding, …) can be added in one place without ad-hoc
injection in the graph node.
"""

from __future__ import annotations

from app.schemas.graph_state import GraphState, Message, RetrievedChunk


def render_grounding_prompt(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks as a numbered, citable source block."""
    lines = [
        "Answer the user's question using the numbered sources below, which were "
        "retrieved from the user's uploaded documents. Prefer these sources and cite "
        "them inline with bracketed numbers like [1], [2]. If the sources do not "
        "contain the answer, say so explicitly rather than relying on outside knowledge.",
        "",
        "Sources:",
    ]
    for i, chunk in enumerate(chunks, 1):
        title = (chunk.document_title or "").strip()
        page = f", p. {chunk.page_from}" if chunk.page_from else ""
        header = f"[{i}] {title}{page}".rstrip()
        lines.append(f"{header}\n{chunk.content.strip()}")
    return "\n".join(lines)


def _split_transient_prefix(messages: list[Message]) -> tuple[list[Message], list[Message]]:
    """Leading system messages prepended by upstream nodes (e.g. M2 memory)."""
    prefix: list[Message] = []
    rest = list(messages)
    while rest and rest[0].role == "system":
        prefix.append(rest.pop(0))
    return prefix, rest


def compose_prompt_wire(state: GraphState) -> list[Message]:
    """Build the full transient wire: memory + grounding + conversation history."""
    memory_prefix, conversation = _split_transient_prefix(state.messages)
    sections: list[str] = [m.content for m in memory_prefix if m.content.strip()]
    if state.retrieved_context:
        sections.append(render_grounding_prompt(state.retrieved_context))

    wire: list[Message] = []
    if sections:
        wire.append(Message(role="system", content="\n\n".join(sections)))
    wire.extend(conversation)
    return wire
