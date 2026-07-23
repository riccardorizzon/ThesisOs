"""Companion experience enforcement — SOFT→HARD (path to honest 9).

Same pattern as citation enforcement (EWO-7C): buffer first pass, one repair retry,
stream only the final text so the user never sees a derailed draft.

Root cause pattern (live 7/8 → next gate fails):
permanent collaboration habits (e.g. REV-02 "always three") outweigh ephemeral
phase hints. Each SOFT gate we leave soft gets the pressure from the previous HARD
gate. So await_choice needs the same HARD fallback as ask_why / PRESERVE.
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.graph.companion.review_state import (
    ReviewPhase,
    count_option_markers,
    has_option_list,
)
from app.llm.base import LLMClient

Emit = Callable[[dict], None]
Generate = Callable[[list[dict]], Awaitable[tuple[str, dict]]]


@dataclass(frozen=True)
class CompanionEnforceContext:
    """Which Companion contract to enforce this turn."""

    opening: bool = False
    preserve: bool = False
    save: bool = False
    review_phase: ReviewPhase | None = None
    choice_made: bool = False

    @property
    def active(self) -> bool:
        return (
            self.opening
            or self.preserve
            or self.save
            or self.review_phase is not None
        )


_DURATION_INVENTION = re.compile(
    r"(?i)\b(?:\d+|un['']?|due|tre|quattro|cinque|sei)\s*ore\b"
)
_WHY_ASK = re.compile(
    r"(?i)(perch[eé]\b|quale\s+frase|ti\s+convince\s+meno|cosa\s+ti\s+convince)"
)
# "Quale di queste direzioni ti convince" is NOT a real why-ask (options already dumped)
_FAKE_WHY_AFTER_OPTIONS = re.compile(
    r"(?i)quale\s+(di\s+queste|opzione|direzione|alternativa)"
)
_DECIDED = re.compile(r"(?i)(oggi\s+)?abbiamo\s+deciso")
_OPEN = re.compile(r"(?i)non\s+abbiamo\s+ancora")
_TOMORROW = re.compile(r"(?i)domani")
_OPTIONS_CUT = re.compile(
    r"(?i)(ecco\s+tre\s+|tre\s+possibil|tre\s+possibili|"
    r"tre\s+alternative|tre\s+opzioni|tre\s+modi|tre\s+strategie|"
    r"tre\s+strade|tre\s+vie|tre\s+direzioni|"
    r"tre\s+formulazioni|tre\s+logiche|tre\s+versioni|"
    r"ti\s+propongo\s+tre\s+|"
    r"(?:^|\n)\s*(?:[-*]\s+)?\*{0,2}\s*[ABC123][\)\.:])"
)


OPENING_RETRY = (
    "INTERNAL REPAIR: la risposta inventava una durata (ore). "
    "Riscrivi l'apertura usando SOLO i fatti di [COMPANION RESUME]. "
    "Vietato dire quante ore avete lavorato. Termina con «Vuoi continuare?»."
)

ASK_WHY_RETRY = (
    "INTERNAL REPAIR: in questa fase NON puoi proporre riscritture né tre opzioni. "
    "Rispondi in italiano: riepilogo brevissimo + chiedi quale frase e perché. "
    "Niente A/B/C. Niente **A). Niente paragrafo sostitutivo."
)

OFFER_OPTIONS_RETRY = (
    "INTERNAL REPAIR: serve ESATTAMENTE tre possibilità etichettate A) B) C), "
    "distinte e brevi, dopo un eco della ragione dell'utente. "
    "Niente unica riscrittura imposta. Chiedi quale preferisce."
)

AWAIT_CHOICE_RETRY = (
    "INTERNAL REPAIR: l'utente HA GIÀ SCELTO. "
    "REV-02 ('tre possibilità') NON si applica dopo la scelta — vale solo in esplorazione. "
    "VIETATO: nuove A/B/C, 1/2/3, «tre modi», «tre strategie», «tre formulazioni». "
    "Obbligo: (1) conferma la scelta in una frase, (2) UNA sola formulazione raffinata, "
    "(3) chiedi se la teniamo. Niente nuova terna."
)

PRESERVE_RETRY = (
    "INTERNAL REPAIR: struttura OBBLIGATORIA in italiano con queste tre intestazioni:\n"
    "Oggi abbiamo deciso:\n"
    "Non abbiamo ancora deciso:\n"
    "Domani ti consiglierei di continuare da qui:\n"
    "Una frase concreta per blocco. Niente saluto generico."
)

SAVE_RETRY = (
    "INTERNAL REPAIR: conferma in italiano che la proposta è SALVATA per continuità "
    "(artifact di sessione), NON il capitolo definitivo. "
    "Vietato: tre blocchi di «basta per oggi», claim di scrittura file/capitolo. "
    "Una frase di conferma + un passo successivo o attesa."
)

_SAVE_ACK = re.compile(
    r"(?i)(salvat|congelat|teniam|tenut|registrat|per\s+(la\s+)?continuit|"
    r"riprend|prossima\s+volta|domani)"
)
_CHAPTER_WRITE_CLAIM = re.compile(
    r"(?i)(chapters/|\.md\b|aggiornat[oa]\s+il\s+capitolo|"
    r"scritt[oa]\s+nel\s+(file|capitolo)|promoss[oa]\s+in\s+knowledge)"
)


def _valid_why_ask(body: str) -> bool:
    if has_option_list(body) or _FAKE_WHY_AFTER_OPTIONS.search(body):
        return False
    return bool(_WHY_ASK.search(body))


def companion_retry_message(text: str, ctx: CompanionEnforceContext) -> str | None:
    """If the draft violates the active Companion contract, return a repair instruction."""
    body = (text or "").strip()
    if not body or not ctx.active:
        return None

    if ctx.opening and _DURATION_INVENTION.search(body):
        return OPENING_RETRY

    if ctx.review_phase == "ask_why":
        if has_option_list(body) or not _valid_why_ask(body):
            return ASK_WHY_RETRY

    if ctx.review_phase == "offer_options":
        if count_option_markers(body) < 2:
            return OFFER_OPTIONS_RETRY

    if ctx.review_phase == "await_choice" and ctx.choice_made:
        # After an explicit pick, any fresh triad is a contract break (REV-02 bleed).
        if has_option_list(body):
            return AWAIT_CHOICE_RETRY

    if ctx.preserve:
        if not (_DECIDED.search(body) and _OPEN.search(body) and _TOMORROW.search(body)):
            return PRESERVE_RETRY

    if ctx.save:
        # Must not look like day-close; must acknowledge continuity save
        looks_like_basta = bool(
            _DECIDED.search(body) and _OPEN.search(body) and _TOMORROW.search(body)
        )
        if (
            looks_like_basta
            or _CHAPTER_WRITE_CLAIM.search(body)
            or not _SAVE_ACK.search(body)
        ):
            return SAVE_RETRY

    return None


def repair_ask_why(text: str) -> str:
    """Last-resort HARD repair: never ship premature A/B/C on ask_why."""
    body = (text or "").strip()
    if _valid_why_ask(body):
        return body
    cut = _OPTIONS_CUT.search(body)
    lead = body[: cut.start()].strip() if cut else body
    lead = re.sub(r"(?i)\s*ecco\s*$", "", lead).strip()
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", lead) if s.strip()]
    summary = " ".join(sentences[:2]).strip()
    if not summary or has_option_list(summary) or len(summary) > 500:
        summary = "Ok, restiamo sul testo."
    return f"{summary}\n\nQuale frase non ti convince, e perché?"


def repair_await_choice(text: str, *, choice_label: str = "quella") -> str:
    """Last-resort HARD repair: after a pick, never ship a new triad."""
    body = (text or "").strip()
    if not has_option_list(body):
        return body
    cut = _OPTIONS_CUT.search(body)
    lead = body[: cut.start()].strip() if cut else ""
    lead = re.sub(r"(?i)\s*ecco\s*$", "", lead).strip()
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", lead) if s.strip()]
    summary = " ".join(sentences[:2]).strip()
    if not summary or has_option_list(summary) or len(summary) > 400:
        summary = f"Perfetto — restiamo su {choice_label}."
    elif choice_label not in summary.lower() and "scelta" not in summary.lower():
        summary = f"{summary} Restiamo su {choice_label}."
    return (
        f"{summary}\n\n"
        f"La raffiniamo in una sola formulazione al prossimo passo, senza nuove terne.\n\n"
        f"La teniamo così come direzione?"
    )


def repair_preserve_structure(text: str, *, focus: str = "§3.6") -> str:
    """Last-resort HARD repair so chat always shows three blocks."""
    body = (text or "").strip()
    if _DECIDED.search(body) and _OPEN.search(body) and _TOMORROW.search(body):
        return body
    return (
        f"{body}\n\n"
        f"Oggi abbiamo deciso:\n"
        f"- (riepilogo da chiudere — riparti dal testo sopra)\n\n"
        f"Non abbiamo ancora deciso:\n"
        f"- Continuare il lavoro su {focus}\n\n"
        f"Domani ti consiglierei di continuare da qui:\n"
        f"- Riprendere da {focus}"
    )


def repair_save_ack(text: str, *, focus: str = "§3.6") -> str:
    """Last-resort HARD repair for «la salvo» session continuity."""
    body = (text or "").strip()
    looks_like_basta = bool(
        _DECIDED.search(body) and _OPEN.search(body) and _TOMORROW.search(body)
    )
    if (
        not looks_like_basta
        and not _CHAPTER_WRITE_CLAIM.search(body)
        and _SAVE_ACK.search(body)
    ):
        return body
    return (
        f"Salvata come proposta di lavoro su {focus} — per continuità, "
        f"non ancora come testo definitivo del capitolo.\n\n"
        f"Domani la riprendiamo da qui. Vuoi proseguire adesso o chiudiamo per oggi?"
    )


async def _collect(
    llm: LLMClient,
    wire: list[dict],
    *,
    emit: Emit | None,
    stream: bool,
    generate: Generate | None = None,
    params: dict | None = None,
) -> tuple[str, dict]:
    if generate is not None:
        text, usage = await generate(wire)
        if text and stream and emit is not None:
            emit({"type": "token", "text": text})
        return text, usage

    parts: list[str] = []
    usage: dict = {}
    async for chunk in llm.astream(wire, params=params):
        if chunk.text:
            parts.append(chunk.text)
            if stream and emit is not None:
                emit({"type": "token", "text": chunk.text})
        if chunk.metadata.get("usage"):
            usage = chunk.metadata["usage"]
    return "".join(parts), usage


async def generate_with_companion_enforcement(
    llm: LLMClient,
    wire: list[dict],
    *,
    ctx: CompanionEnforceContext,
    emit: Emit | None = None,
    focus: str = "§3.6",
    choice_label: str = "quella",
    generate: Generate | None = None,
    params: dict | None = None,
) -> tuple[str, dict, bool]:
    """Generate with Companion-contract check; stream live for UX, replace if repaired.

    First pass streams tokens so the UI is not blank while a strong model thinks.
    If the contract fails, repair (LLM retry and/or HARD patch) and emit ``replace``
    so the bubble shows only the accepted final text.
    """
    if not ctx.active:
        text, usage = await _collect(
            llm, wire, emit=emit, stream=True, generate=generate, params=params
        )
        return text, usage, False

    # Live first pass — high-quality models stay usable (no silent 20–40s blank)
    text, usage = await _collect(
        llm, wire, emit=emit, stream=True, generate=generate, params=params
    )
    repair = companion_retry_message(text, ctx)
    retried = False
    replaced = False

    if repair:
        retry_wire = [
            *wire,
            {"role": "assistant", "content": text},
            {"role": "user", "content": repair},
        ]
        text, usage = await _collect(
            llm,
            retry_wire,
            emit=None,
            stream=False,
            generate=generate,
            params=params,
        )
        retried = True
        replaced = True

    # Second line of defense: surgical HARD repair when retry still violates
    if companion_retry_message(text, ctx):
        if ctx.preserve:
            text = repair_preserve_structure(text, focus=focus)
        elif ctx.save:
            text = repair_save_ack(text, focus=focus)
        elif ctx.review_phase == "ask_why":
            text = repair_ask_why(text)
        elif ctx.review_phase == "await_choice" and ctx.choice_made:
            text = repair_await_choice(text, choice_label=choice_label)
        replaced = True

    if emit is not None and replaced:
        emit({"type": "replace", "text": text})

    return text, usage, retried
