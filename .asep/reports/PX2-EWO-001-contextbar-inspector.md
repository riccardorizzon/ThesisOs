# PX2-EWO-001 — ContextBar Live + Context Inspector

**WorkOrder:** PX2-EWO-001  
**Date:** 2026-07-04  
**Sub-agent:** A  
**Verdict:** **IMPLEMENTED**

---

## Deliverables

| Artifact | Path |
|----------|------|
| ContextBar (live counts, skeleton, hooks) | `frontend/components/context/ContextBar.tsx` |
| Context Inspector shell | `frontend/components/context/ContextInspector.tsx` |
| Context counts helper | `frontend/components/context/ContextSummary.tsx` |
| Context client extensions | `frontend/lib/contextClient.ts` |
| Context loader | `frontend/lib/contextLoad.ts` |
| Context API query params | `backend/app/api/projects.py` |
| Context schema extensions | `backend/app/schemas/context.py` |
| Packet flattening | `backend/app/services/context/present.py` |
| Tests | `frontend/components/context/ContextBar.test.tsx`, `frontend/components/context/ContextInspector.test.tsx`, `backend/tests/test_context_api.py` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| AC-1 ContextBar live counts from ContextPacket (fonti · decisioni · voci · citazioni) | **PASS** |
| Skeleton → populated crossfade (150ms); editor not blocked (`loading` prop) | **PASS** |
| Scope chip click → `onScopeClick` hook (outline scroll wired by EWO-002/003) | **PASS** |
| Counts click → `onOpenContestoTab` + `thesisos:open-contesto-tab` event | **PASS** |
| ContextInspector human-readable accordion (no raw JSON) | **PASS** |
| Context API `entity_id` + `selection_anchor` query params; backward compatible | **PASS** |
| `warningState` prop slot for Integration A (PX2-EWO-005) | **PASS** |
| Decision section deferred (placeholder comment for Integration A) | **PASS** |
| Frontend tests (touched files) | **PASS** — 16/16 |
| Backend context tests | **PASS** — 10/10 |

---

## Component Summary

### ContextBar (§4.2)

- Compact row: `h-contextbar`, scope chip + live counts + info affordance
- Scope chip label via `formatScopeChipLabel()` — chapter title + optional `§` anchor
- Counts label: `{n} fonti · {n} decisioni · {n} voci · {n} citazioni`
- `loading` → three skeleton chips; content fades in with `duration-150`
- `warningState?: { active, message? }` → amber border/bg + optional message strip
- `onScopeClick`, `onOpenContestoTab`, `dispatchOpenContestoTab()` for downstream wiring

### ContextInspector (§5.4)

Accordion sections (native `<details>`):

| Section | Default |
|---------|---------|
| Ambito | Open |
| Vincoli corpus | Open if any |
| Definizioni | Collapsed |
| Fonti rilevanti | Open |
| Regole di scrittura | Collapsed |

Placeholder comment for **Decisioni vincolanti** — Integration A imports `DecisionInspectorSection` from PX2-EWO-005.

### Context API

- New optional query param: `selection_anchor`
- Echoed on `ContextPacket.selection_anchor` (non-breaking; `null` when omitted)
- Existing `entity_type` / `entity_id` unchanged

### Client helpers

- `formatScopeChipLabel`, `CONTEXT_OPEN_CONTESTO_EVENT`, `dispatchOpenContestoTab`
- `ContextQuery.selectionAnchor` → `selection_anchor` query string

---

## Files Changed

```
frontend/components/context/ContextBar.tsx
frontend/components/context/ContextInspector.tsx          (NEW)
frontend/components/context/ContextSummary.tsx
frontend/components/context/ContextBar.test.tsx
frontend/components/context/ContextInspector.test.tsx     (NEW)
frontend/components/context/index.ts
frontend/lib/contextClient.ts
frontend/lib/contextLoad.ts
backend/app/api/projects.py
backend/app/schemas/context.py
backend/app/services/context/present.py
backend/tests/test_context_api.py
```

**Not modified (already present):** `frontend/styles/tokens.css` (`--contextbar-height` pre-existing)

---

## Test Results

```text
frontend: npm test -- --run components/context/ContextBar.test.tsx components/context/ContextInspector.test.tsx
  16 passed

backend: .venv/bin/python -m pytest tests/test_context_api.py -q
  10 passed
```

---

## Integration Notes

| Consumer | Hook |
|----------|------|
| PX2-EWO-003 (Right rail) | Listen for `thesisos:open-contesto-tab` or pass `onOpenContestoTab` |
| PX2-EWO-005 (Decisions) | Pass `warningState` from `useDecisionWarning`; add `DecisionInspectorSection` to ContextInspector placeholder |
| PX2-EWO-002 (Editor) | Pass `selectionAnchor`, wire `onScopeClick` to outline scroll |

---

## WO-TRACE

```text
PX-1 COMPLETE → PX2-EWO-001 → PX2-EWO-003, PX2-EWO-005
```
