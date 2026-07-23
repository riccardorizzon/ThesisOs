"""REVIEW dialog phases — enforce non mi convince script (PM-008 → score ≥9)."""

from __future__ import annotations

import re
from typing import Literal

ReviewPhase = Literal["ask_why", "offer_options", "await_choice"]

# Shared option detector — A/B/C, **A), 1/2/3, and "tre modi/strategie"
_OPTION_MARK = re.compile(
    r"(?i)(?:^|\n)\s*(?:[-*]\s+)?(?:\*{0,2}\s*)?[ABC][\)\.:\*]|"
    r"(?:^|\n)\s*(?:[-*]\s+)?(?:\*{0,2}\s*)?[123][\)\.]"
)
_OPTION_CUES = re.compile(
    r"(?i)(tre\s+possibilit|tre\s+possibili(\s+direzioni)?|"
    r"tre\s+alternative|tre\s+opzioni|tre\s+modi|tre\s+strategie|"
    r"tre\s+strade|tre\s+vie|tre\s+direzioni|"
    r"tre\s+formulazioni|tre\s+logiche|tre\s+versioni)"
)
_CHOICE_USER = re.compile(
    r"(?i)\b(preferisco\s+la\s+(prima|seconda|terza)|opzione\s*[abc123]|"
    r"la\s+[abc]\b|la\s+(prima|seconda|terza))\b"
)
# Fresh dissatisfaction — must restart REVIEW even if prior still shows an old triad
_REVIEW_RESTART = re.compile(r"(?i)\bnon\s+mi\s+convince\b")
# Companion why-ask only — question forms, not thesis prose / casual mentions.
_WHY_IN_ASSISTANT = re.compile(
    r"(?i)("
    r"quale\s+frase|"
    r"cosa\s*,?\s*(?:in\s+particolare\s*,?\s*)?(non\s+)?ti\s+(convince|torna)|"
    r"(?:cosa|che\s+cosa|quale(?:\s+\w+)?)[^.?\n]{0,60}ti\s+convince\s+meno|"
    r"ti\s+convince\s+meno\s*\?|"
    r"non\s+ti\s+torna|"
    r"a\s+cosa\s+ti\s+riferisci|"
    r"che\s+cosa\s+non|"
    r"l'idea\s+di\s+fondo|"
    r"un\s+termine\s+specifico|"
    r"e\s+perch[eé]\s*\?|"
    r"perch[eé]\s*\?"
    r")"
)
# Bare «non mi convince questa frase» is NOT a reason — still ask_why.
_BARE_DISLIKE = re.compile(
    r"(?i)^\s*non\s+mi\s+convince\b"
    r"(?:\s+(?:questa|questo|quella|quel)\s+\w+)?\s*[.!]?\s*$"
)


def has_option_list(text: str) -> bool:
    """True if assistant (or draft) proposes multi-alternative lists."""
    body = text or ""
    if _OPTION_CUES.search(body):
        return True
    return count_option_markers(body) >= 2


def count_option_markers(text: str) -> int:
    return len(_OPTION_MARK.findall(text or ""))


def choice_made(utterance: str | None) -> bool:
    return bool(utterance and _CHOICE_USER.search(utterance.strip()))


def choice_label(utterance: str | None) -> str:
    """Human label for HARD repair copy."""
    text = (utterance or "").strip().lower()
    if re.search(r"\b(seconda|b\b|2)\b", text):
        return "la seconda"
    if re.search(r"\b(prima|a\b|1)\b", text):
        return "la prima"
    if re.search(r"\b(terza|c\b|3)\b", text):
        return "la terza"
    return "quella"


def infer_review_phase(
    *,
    pillar: str,
    utterance: str | None,
    prior_assistant: str | None,
) -> ReviewPhase | None:
    """Return REVIEW sub-phase when in a review dialog; else None."""
    if pillar != "REVIEW":
        return None
    text = (utterance or "").strip()
    prior = prior_assistant or ""

    # Root: CONTINUE/resume often re-surfaces an old A/B/C triad. A fresh
    # «non mi convince» must restart the script (ask_why → offer_options),
    # not stay stuck in await_choice because prior still lists options.
    # Bare dislike (no reason yet) always ask_why — even if prior text
    # casually mentions «ti convince meno» outside a real why-ask.
    if _REVIEW_RESTART.search(text) and not choice_made(text):
        if _BARE_DISLIKE.match(text):
            return "ask_why"
        if _WHY_IN_ASSISTANT.search(prior):
            return "offer_options"
        return "ask_why"

    if has_option_list(prior) or choice_made(text):
        return "await_choice"
    if _WHY_IN_ASSISTANT.search(prior):
        return "offer_options"
    # User already volunteered the reason in the same REVIEW turn
    if re.search(r"(?i)perch[eé]\s+\w{3,}", text) and len(text) > 40:
        return "offer_options"
    return "ask_why"


REVIEW_PHASE_HINTS: dict[ReviewPhase, str] = {
    "ask_why": """[INTERNAL — REVIEW phase: ASK_WHY]
MANDATORY this turn:
1. One short summary of current § state (1–2 sentences) if you have text.
2. Ask which phrase / what does not convince — and WHY.
FORBIDDEN this turn:
- Do NOT propose rewrites
- Do NOT list three options yet
- Do NOT paste replacement paragraphs
- Do NOT use A) B) C) or **A) **B) **C)
Keep under 6 sentences. End with a question.""",
    "offer_options": """[INTERNAL — REVIEW phase: OFFER_OPTIONS]
User explained why. MANDATORY this turn:
1. One-sentence echo of their reason
2. Exactly THREE distinct options labeled A) B) C) (short, different strategies)
FORBIDDEN:
- Single imposed rewrite
- Pasting a full replacement paragraph as fait accompli
- Skipping to final text
End by asking which option they prefer.""",
    "await_choice": """[INTERNAL — REVIEW phase: AWAIT_CHOICE]
User is choosing OR already chose among options that were on the table.

REV-02 EXCEPTION (critical): after a choice, REV-02 does NOT mean "three new phrasings".
That rule applies only while exploring — not after «preferisco la seconda» / A / B / C.

If they pick A/B/C or «preferisco la seconda»:
1. Confirm the choice in ONE sentence (name it).
2. Refine ONLY that direction into ONE formulation (blockquote ok).
3. Ask yes/no approval.
FORBIDDEN this turn:
- New A) B) C) / 1. 2. 3. / «tre modi» / «tre strategie» / «tre formulazioni»
- Restarting exploration as if they had not chosen
- Editing the thesis file

If unclear which option: ask which of the EXISTING A/B/C — do not invent a new triad.""",
}
