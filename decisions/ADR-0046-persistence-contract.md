# ADR-0046: Companion Persistence Contract (NO WRITE = NO SAVE)

**Status:** Accepted  
**Date:** 2026-07-23  
**Plane:** Product  
**Related:** ADR-0045 (Companion-first entry), ADR-0044, PM-008

## Context

ThesisOS saves intellectual work, not messages. Before this decision the Companion could
*confirm* a save («la salvo», «basta per oggi») while zero bytes were written: the pillar
prompts and output enforcement produced a convincing confirmation, but
`save_session_close` and `save_work_artifact` had no callers in the chat path. The system
also lacked a formal definition of *what* may become persistent, so continuity logic was
scattered across pillars.

## Decision

### 1. Persistence taxonomy (the only four tiers)

Defined in `backend/app/services/workspace/persistence.py` (`PersistenceTier`):

| Tier | Example | Store |
|------|---------|-------|
| `NONE` | «spiegami Derrida» | message log only, never memory |
| `SESSION_STATE` | «basta per oggi» → work-close | `companion_session` memory key |
| `WORK_ARTIFACT` | «la salvo» → approved proposal | `companion_work_artifact` memory key |
| `PERSISTENT_MEMORY` | confirmed collaboration rule, binding decision | learning loop / decisions |

Nothing else is persisted from chat. Definitive chapters still change only through
Writing/Review gates (ADR-0045 INV-COMP-5).

### 2. NO WRITE = NO SAVE

A saved-confirmation may reach the user **only after the corresponding write succeeded**.
The conversation node classifies the turn (`classify_persistence`), executes the write
(`persist_turn`), and on failure replaces the reply with an honest failure message
(`persistence_failure_text`) and records `persistence_failed:<tier>` in graph errors.
It is structurally impossible for the Companion to lie about a save.

### 3. Resume is the single source of truth

The `[COMPANION RESUME]` block rendered by `render_companion_resume` is authoritative for
where work resumes. The persistence layer parses focus and next action back from that same
block (`focus_from_resume`, `next_action_from_resume`); the frontend continuation button
uses `continue_prompt` from the resume packet, not hardcoded copy. One Resume — frontend
shows it, backend uses it, Companion speaks from it.

### 4. Unified session workflow

All pillars share one continuity workflow: open session → load resume → work → update
state → persist what the taxonomy allows → resume next session. Pillar hints remain
prompt/enforcement concerns; persistence decisions live only in the persistence module.

### 5. No silent errors

`except: pass` is forbidden in the product plane. Learning-loop and knowledge fallback
failures are logged with full traceback; persistence failures are logged *and* surfaced to
the user honestly. A session may continue after an error, but the error is always recorded.

## Invariants

- **INV-PERS-1:** Only the four tiers above may be persisted from chat.
- **INV-PERS-2:** NO WRITE = NO SAVE — no confirmation without a successful write.
- **INV-PERS-3:** The Resume packet is the single source of truth for continuity, on both
  planes (frontend and backend).
- **INV-PERS-4:** Persistence failures are visible to the user and recorded in run errors.

## Compliance

- `backend/tests/test_persistence_contract.py` — taxonomy, resume parsing, outcome honesty.
- `backend/tests/test_companion_chat_wiring.py` — «basta per oggi» and «la salvo» write
  through the graph; failed writes never confirm; failed session close never shows the
  three-block close.
- `frontend/components/AiChatView.test.tsx` — continuation copy comes from the packet.
