"""Rule-based pillar classification — internal only (Companion Loop v0 / PM-008)."""

from __future__ import annotations

import re

Pillar = str

_CONTINUE = "CONTINUE"
_UNDERSTAND = "UNDERSTAND"
_ORIENT = "ORIENT"
_WRITE = "WRITE"
_REVIEW = "REVIEW"
_SAVE = "SAVE"
_PRESERVE = "PRESERVE"
_SUPPORT = "SUPPORT"

# Bare affirmations after 09:00 / "Vuoi continuare?" — must be CONTINUE (E6 fix)
_AFFIRMATION = re.compile(
    r"(?i)^\s*(s[iì]|si|ok|okay|vai|perfetto|certo|va\s+bene|continuiamo)\s*[.!]?\s*$"
)

_RULES: list[tuple[Pillar, re.Pattern[str]]] = [
    (_CONTINUE, re.compile(r"\b(ciao|continuiamo|da ieri|da dove|riprend|bentornat|continua)\b", re.I)),
    (_PRESERVE, re.compile(r"\b(basta per oggi|chiudiamo per oggi|chiudiamo)\b", re.I)),
    # Session work-proposal (not day-close, not chapters/)
    (
        _SAVE,
        re.compile(
            r"(?i)\b("
            r"la\s+salvo|salviamola|salvala|congelala|congeliamola|"
            r"salva\s+(questa|la)\s+(proposta|frase|versione|scelta)|"
            r"congela\s+(questa|la)\s+(proposta|frase|versione)|"
            r"salva\s+il\s+punto|congela|memorizza\s+questo|traccia\s+questo"
            r")\b"
        ),
    ),
    (_UNDERSTAND, re.compile(r"\b(non capisco|significa|critica|relatrice|spieg)\b", re.I)),
    (_REVIEW, re.compile(r"\b(non mi convince|rilegg\w*|rived\w*|revision|feedback)\b", re.I)),
    (_WRITE, re.compile(r"\b(scriv|stend|paragrafo|capitolo|bozza)\b", re.I)),
    (_ORIENT, re.compile(r"\b(perso|cosa (fare|consigli)|oggi|riepilogo|dove siamo|decisioni|ricord\w*)\b", re.I)),
    (_SUPPORT, re.compile(r"\b(bloccat\w*|aiuto|motiv|stanco|ansia)\b", re.I)),
]

# Soft REVIEW stickiness: mid-dialog answers after "perché?" / options ask
_REVIEW_STICKY_ASSISTANT = re.compile(
    r"(?i)(perch[eé]\b|quale\s+frase|ti\s+convince|tre\s+possibilit|"
    r"opzione\s*[abc]|cosa\s+ti\s+convince)"
)


def is_affirmation(utterance: str | None) -> bool:
    return bool(utterance and _AFFIRMATION.match(utterance.strip()))


def classify_pillar(
    utterance: str | None,
    *,
    prior_assistant: str | None = None,
) -> Pillar:
    text = (utterance or "").strip()
    if not text:
        return _CONTINUE
    # E6: «sì» / «ok» after opening must continue the work
    if is_affirmation(text):
        return _CONTINUE
    for pillar, pattern in _RULES:
        if pattern.search(text):
            return pillar
    # REVIEW multi-turn: short answer after companion asked why / options
    if (
        prior_assistant
        and _REVIEW_STICKY_ASSISTANT.search(prior_assistant)
        and len(text) <= 120
    ):
        return _REVIEW
    return _ORIENT
