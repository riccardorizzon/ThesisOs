"""Writer LLM wire + citation helpers (M6, ADR-0031).

Centralizes drafting prompt assembly and citation discipline so the writer
capability stays thin. Pure helpers — no DB / runtime / persistence.
"""

from __future__ import annotations

from app.graph.orchestration.messages import format_plan_for_prompt
from app.graph.academic_production import (
    ACADEMIC_CITATION_INSTRUCTION,
    ACADEMIC_FEW_SHOT,
    ACADEMIC_INFERENCE_ENFORCEMENT,
    ACADEMIC_PRODUCTION_BLOCK,
)
from app.graph.prompt_wire import render_grounding_prompt
from app.schemas.draft import WriterBrief
from app.schemas.graph_state import CitationRef, Message, RetrievedChunk

WRITER_SYSTEM = f"""You are the Writer agent for ThesisOS.

Draft thesis prose — a chapter or section — in the user's academic register
(Italian unless the conversation is in another language), following the writing
brief and grounded in the numbered sources below.

{ACADEMIC_PRODUCTION_BLOCK.strip()}

{ACADEMIC_FEW_SHOT.strip()}

{ACADEMIC_INFERENCE_ENFORCEMENT.strip()}

Rules:
- Use the writing brief (plan) to decide structure and what to cover this turn.
- Ground claims in the sources; cite {ACADEMIC_CITATION_INSTRUCTION}
- Do NOT invent sources, quotations, or facts not supported by the sources or the conversation.
- If the sources do not support a needed claim, write cautiously and say what is
  missing rather than fabricating support.
- Produce coherent, well-structured prose (Markdown). Do not output JSON.
"""

WRITING_PANEL_ACTIONS: dict[str, str] = {
    "rewrite": (
        "Riscrivi il passaggio selezionato in registro accademico italiano. "
        "Mantieni il significato; migliora chiarezza e stile. Output solo il testo riscritto."
    ),
    "verify": (
        "Verifica coerenza del testo con decisioni vincolanti e vincoli corpus forniti. "
        "Segnala conflitti o conferma allineamento. Output in prosa breve."
    ),
    "find-sources": (
        "Suggerisci fonti dal corpus pertinenti al passaggio o capitolo. "
        "Elenca titoli e motivazione; non inventare fonti assenti dal contesto."
    ),
    "expand": (
        "Espandi il passaggio selezionato con approfondimento argomentativo "
        "grounded nel contesto. Output in Markdown."
    ),
}


def compose_writing_panel_wire(
    *,
    action: str,
    selection_text: str | None,
    chapter_content: str,
    context_summary: str | None,
    retrieved_context: list[RetrievedChunk],
) -> list[Message]:
    """Build LLM wire for lateral Writing panel actions (PX2-EWO-003)."""
    instruction = WRITING_PANEL_ACTIONS.get(
        action,
        "Assist the operator with the requested writing action in Italian academic register.",
    )
    sections: list[str] = [
        WRITER_SYSTEM,
        f"Writing panel action: {action}\n\nTask:\n{instruction}",
    ]
    if context_summary and context_summary.strip():
        sections.append(f"Context packet summary:\n{context_summary.strip()}")
    if retrieved_context:
        sections.append(render_grounding_prompt(retrieved_context, academic_writing=True))
    if chapter_content.strip():
        sections.append(f"Chapter content (reference):\n{chapter_content.strip()}")
    if selection_text and selection_text.strip():
        sections.append(f"Selected passage:\n{selection_text.strip()}")

    user_prompt = f"Execute the '{action}' action for the writing panel."
    return [
        Message(role="system", content="\n\n".join(s for s in sections if s.strip())),
        Message(role="user", content=user_prompt),
    ]


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
        sections.append(
            render_grounding_prompt(brief.retrieved_context, academic_writing=True)
        )

    wire: list[Message] = [Message(role="system", content="\n\n".join(s for s in sections if s.strip()))]
    wire.extend(rest)
    return wire
