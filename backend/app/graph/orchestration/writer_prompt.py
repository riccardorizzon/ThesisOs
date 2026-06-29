"""Writer LLM wire + citation helpers (M6, ADR-0031).

Centralizes drafting prompt assembly and citation discipline so the writer
capability stays thin. Pure helpers — no DB / runtime / persistence.
"""

from __future__ import annotations

from app.graph.orchestration.messages import format_plan_for_prompt
from app.graph.prompt_wire import render_grounding_prompt
from app.schemas.draft import WriterBrief
from app.schemas.graph_state import CitationRef, Message, RetrievedChunk

WRITER_SYSTEM = """You are the Writer agent for ThesisOS.

Draft thesis prose — a chapter or section — in the user's academic register
(Italian unless the conversation is in another language), following the writing
brief and grounded in the numbered sources below.

Rules:
- Use the writing brief (plan) to decide structure and what to cover this turn.
- Ground claims in the numbered sources; cite them inline with bracketed numbers
  like [1], [2]. Do NOT invent sources, quotations, or facts not supported by the
  sources or the conversation.
- If the sources do not support a needed claim, write cautiously and say what is
  missing rather than fabricating support.
- Produce coherent, well-structured prose (Markdown). Do not output JSON.
"""


def allowed_citation_source_ids(chunks: list[RetrievedChunk]) -> set[str]:
    """Source ids the writer may legitimately cite (⊆ retrieved sources)."""
    allowed: set[str] = set()
    for chunk in chunks:
        if chunk.document_id:
            allowed.add(chunk.document_id)
        allowed.add(chunk.chunk_id)
    return allowed


def build_citations(chunks: list[RetrievedChunk]) -> list[CitationRef]:
    """Citations for the sources the draft was grounded on (source_id ⊆ retrieved)."""
    return [
        CitationRef(
            source_id=chunk.document_id or chunk.chunk_id,
            locator=(f"p.{chunk.page_from}" if chunk.page_from else chunk.chunk_id),
        )
        for chunk in chunks
    ]


def filter_citations(citations: list[CitationRef], allowed: set[str]) -> list[CitationRef]:
    """Drop any citation whose source_id is not a retrieved source (ADR-0031 §5)."""
    return [c for c in citations if c.source_id in allowed]


def compose_writer_wire(brief: WriterBrief) -> list[Message]:
    """Build the transient drafting wire: system instruction + memory + plan + grounding + conversation."""
    rest = list(brief.messages)
    memory_prefix: list[Message] = []
    while rest and rest[0].role == "system":
        memory_prefix.append(rest.pop(0))

    sections: list[str] = [WRITER_SYSTEM]
    sections.extend(m.content for m in memory_prefix if m.content.strip())
    if brief.plan is not None and brief.plan.steps:
        sections.append("Writing brief (plan for this turn):\n" + format_plan_for_prompt(brief.plan))
    if brief.retrieved_context:
        sections.append(render_grounding_prompt(brief.retrieved_context))

    wire: list[Message] = [Message(role="system", content="\n\n".join(s for s in sections if s.strip()))]
    wire.extend(rest)
    return wire
