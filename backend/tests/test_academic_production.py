"""EWO-7B academic production path tests."""

from __future__ import annotations

from app.graph.academic_production import (
    ACADEMIC_CITATION_INSTRUCTION,
    CITATION_ENFORCEMENT_RETRY_MESSAGE,
    is_academic_writing_query,
    infer_author_year,
    needs_citation_enforcement_retry,
)
from app.graph.orchestration import writer_prompt as writer_prompt_mod
from app.graph.prompt_wire import compose_prompt_wire, render_grounding_prompt
from app.schemas.graph_state import GraphState, Message, RetrievedChunk


def _chunk(title: str = "Albers Interaction of Color") -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="c1",
        score=0.9,
        content="Relational color theory.",
        document_title=f"[kimi-claw-2026-06] {title}",
        document_id="d1",
        page_from=12,
    )


def test_is_academic_writing_query_or6_prompt():
    prompt = (
        "Scrivi un paragrafo di prova per §3.2 colore e Josef Albers in modalità "
        "scrittura accademica. Applica REV-006, separazione A/B."
    )
    assert is_academic_writing_query(prompt)


def test_is_academic_writing_query_corpus_list_negative():
    assert not is_academic_writing_query("Elenca gli autori del corpus attivo.")


def test_is_academic_writing_query_rules_list_negative():
    assert not is_academic_writing_query("Elenca tutte le regole università e relatrice.")


def test_render_grounding_prompt_academic_mode():
    out = render_grounding_prompt([_chunk()], academic_writing=True)
    assert "author-date" in out
    assert "(Albers, 1963)" in out
    assert "[Source 1]" in out
    assert "numbered sources" not in out.lower()
    assert "bracketed numbers like [1]" not in out
    assert "Do NOT use numeric bracket citations" in out
    assert "Academic writing mode" in out
    assert "Example of correct citation format" in out
    assert "Output constraints (inference enforcement" in out


def test_render_grounding_prompt_default_numeric_mode():
    out = render_grounding_prompt([_chunk()], academic_writing=False)
    # Q&A prefers author-date; [n] remains as fallback when year unknown.
    assert "author-date" in out
    assert "bracketed numbers like [1], [2]" in out
    assert "[1] Albers Interaction of Color" in out


def test_compose_prompt_wire_academic_turn():
    state = GraphState(
        messages=[
            Message(role="system", content="[BINDING DECISIONS] frozen"),
            Message(
                role="user",
                content="Scrivi un paragrafo di prova per §3.2 in modalità scrittura accademica.",
            ),
        ],
        retrieved_context=[_chunk()],
    )
    wire = compose_prompt_wire(state)
    assert len(wire) == 2
    system = wire[0].content
    assert ACADEMIC_CITATION_INSTRUCTION.split(".")[0] in system
    assert "Albers (1963)" in system


def test_compose_prompt_wire_corpus_list_prefers_author_date():
    state = GraphState(
        messages=[Message(role="user", content="Elenca gli autori del corpus attivo.")],
        retrieved_context=[_chunk()],
    )
    wire = compose_prompt_wire(state)
    assert "author-date" in wire[0].content
    assert "bracketed numbers like [1], [2]" in wire[0].content


def test_writer_system_uses_author_date():
    assert "author-date" in writer_prompt_mod.WRITER_SYSTEM
    assert "bracketed numbers like [1]" not in writer_prompt_mod.WRITER_SYSTEM


def test_infer_author_year_albers():
    author, year = infer_author_year(_chunk())
    assert author == "Albers"
    assert year == 1963


def test_needs_citation_enforcement_retry_numeric_only():
    assert needs_citation_enforcement_retry("Teoria cromatica [2] secondo Albers.")
    assert not needs_citation_enforcement_retry("Secondo Albers (Albers, 1963) il colore …")
    assert not needs_citation_enforcement_retry("Plain prose without cites.")


def test_citation_enforcement_retry_message_is_deterministic():
    assert "autore-data" in CITATION_ENFORCEMENT_RETRY_MESSAGE.lower()
    assert "[n]" in CITATION_ENFORCEMENT_RETRY_MESSAGE
