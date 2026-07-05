"""Academic production + inference enforcement (EWO-7B / EWO-7C).

EWO-7B: production path — author-date instructions vs numeric Q&A cites.
EWO-7C: inference enforcement — few-shot, de-priming, deterministic retry guard.

Pure helpers — no DB / LangGraph imports.
"""

from __future__ import annotations

import re

from app.graph.orchestration.constants import WRITER_PHRASES, WRITER_STRUCTURE_TOKENS
from app.schemas.graph_state import Message, RetrievedChunk

_MIGRATION_TAG_RE = re.compile(r"^\[[^\]]+\]\s*")

_ACADEMIC_WRITING_RE = re.compile(
    r"scrittura accademica|modalit[aà] scrittura|paragrafo di prova|paragrafo per|"
    r"REV-006|separazione A/B|firewall persona|PRONTO PER REVISIONE|"
    r"scrivi un paragrafo|scrivi il paragrafo|redigi un paragrafo|stendi un paragrafo|"
    r"draft.*paragraph|write.*paragraph",
    re.IGNORECASE,
)

_AUTHOR_DATE_RE = re.compile(r"\([A-Za-zÀ-ÿ][\w\-']+,\s*\d{4}\)")
_AUTHOR_DATE_ALT_RE = re.compile(r"[A-Za-zÀ-ÿ][\w\-']+\s*\(\s*\d{4}\s*\)")
_NUMERIC_CITE_RE = re.compile(r"\[\d+\]")

# Frozen corpus author → reference year (Bibliography-Master v1.0).
_CORPUS_AUTHOR_YEARS: dict[str, int] = {
    "Albers": 1963,
    "Benjamin": 1936,
    "Barthes": 1957,
    "Csikszentmihalyi": 1990,
    "Hollander": 1994,
    "Lobach": 1976,
    "Löbach": 1976,
    "Seivewright": 2007,
    "Sennett": 2008,
    "Warburg": 1929,
}

NUMERIC_CITATION_INSTRUCTION = (
    "them inline with bracketed numbers like [1], [2]."
)

ACADEMIC_GROUNDING_PREAMBLE = (
    "Draft the academic paragraph using the reference sources below, retrieved from "
    "the user's uploaded documents. Ground claims in these sources and cite "
)

ACADEMIC_CITATION_INSTRUCTION = (
    "them inline using author-date format (Author surname, year) — e.g. (Albers, 1963). "
    "Use the author and year shown in each source header. "
    "Do NOT use numeric bracket citations like [1], [2] in the academic prose. "
    "Do NOT use footnotes. On first mention, use the author's full name in the text "
    "where appropriate, with (Author, year) for the citation."
)

ACADEMIC_PRODUCTION_BLOCK = """Academic writing mode (OR-4 / REL-03 / UNI-01):
- Neutral academic register; persona/chat voice OFF — no chatty preamble.
- Inline citations: author-date (Author, year) in the body — never [1], [2], never footnotes.
- Separate author theory (A) from thesis application (B) when relevant.
- Label probative status where required (FONDATO / PLAUSIBILE / etc.).
- Mark draft status explicitly (e.g. PRONTO PER REVISIONE) — do not unilaterally freeze content.
"""

ACADEMIC_FEW_SHOT = """Example of correct citation format (follow this pattern):
Secondo Josef Albers, il colore non si percepisce in isolamento (Albers, 1963).
Wrong: "…interazione cromatica [2]." — never use [n] in academic prose.
"""

ACADEMIC_INFERENCE_ENFORCEMENT = """Output constraints (inference enforcement — mandatory):
- Every source-backed claim in the paragraph MUST include at least one author-date citation.
- Forbidden in the paragraph body: [1], [2], [3], or any [digit] citation marker.
- Required pattern: (Surname, YYYY) immediately after or within the sentence citing that source.
"""

CITATION_ENFORCEMENT_RETRY_MESSAGE = (
    "REVISIONE OBBLIGATORIA — conformità citazioni accademiche.\n"
    "La bozza usa citazioni numeriche [n], vietate in modalità scrittura accademica.\n"
    "Riscrivi SOLO il paragrafo accademico sostituendo ogni [n] con il formato autore-data "
    "(Autore, anno) — es. (Albers, 1963) — usando gli autori/anni negli header delle fonti.\n"
    "Mantieni A/B, etichette FONDATO/PLAUSIBILE, stato bozza, registro accademico neutro.\n"
    "Non aggiungere preamboli conversazionali."
)


def is_academic_writing_query(query: str) -> bool:
    """True when the user turn requests thesis academic prose, not list/Q&A turns."""
    if not query.strip():
        return False
    lower = query.lower()
    if _ACADEMIC_WRITING_RE.search(query):
        return True
    if any(phrase in lower for phrase in WRITER_PHRASES):
        return True
    if any(tok in lower for tok in WRITER_STRUCTURE_TOKENS) and any(
        verb in lower for verb in ("scrivi", "redigi", "stendi", "write", "draft", "compose")
    ):
        return True
    return False


def last_user_content(messages: list[Message]) -> str | None:
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    return None


def has_author_date_citation(text: str) -> bool:
    return bool(_AUTHOR_DATE_RE.search(text) or _AUTHOR_DATE_ALT_RE.search(text))


def has_prohibited_numeric_citations(text: str) -> bool:
    return bool(_NUMERIC_CITE_RE.search(text))


def needs_citation_enforcement_retry(text: str) -> bool:
    """Deterministic: numeric [n] in prose without any author-date citation."""
    if not text.strip():
        return False
    return has_prohibited_numeric_citations(text) and not has_author_date_citation(text)


def _clean_document_title(title: str) -> str:
    return _MIGRATION_TAG_RE.sub("", title.strip())


def infer_author_year(chunk: RetrievedChunk) -> tuple[str | None, int | None]:
    """Best-effort author/year from promoted document title (Bibliography-Master)."""
    title = _clean_document_title(chunk.document_title or "")
    if not title:
        return None, None
    surname = title.split()[0].strip("_,.")
    year = _CORPUS_AUTHOR_YEARS.get(surname)
    return (surname, year) if surname else (None, None)


def format_source_header(index: int, chunk: RetrievedChunk, *, academic_writing: bool) -> str:
    title = _clean_document_title(chunk.document_title or "")
    page = f", p. {chunk.page_from}" if chunk.page_from else ""
    if academic_writing:
        author, year = infer_author_year(chunk)
        if author and year:
            return f"[Source {index}] {author} ({year}) — {title}{page}".rstrip()
        if author:
            return f"[Source {index}] {author} — {title}{page}".rstrip()
        return f"[Source {index}] {title}{page}".rstrip()
    return f"[{index}] {title}{page}".rstrip()
