# PX2-EWO-005 — Decision Cards + Context Warning Hook

**WorkOrder:** PX2-EWO-005  
**Date:** 2026-07-04  
**Sub-agent:** C  
**Verdict:** **IMPLEMENTED**

---

## Deliverables

| Artifact | Path |
|----------|------|
| Decision card | `frontend/components/decisions/DecisionCard.tsx` |
| Inspector section (standalone) | `frontend/components/decisions/DecisionInspectorSection.tsx` |
| Decision client | `frontend/lib/decisionClient.ts` |
| Warning hook | `frontend/lib/useDecisionWarning.ts` |
| DecisionBadge extension | `frontend/components/context/DecisionBadge.tsx` |
| Tests | `frontend/components/decisions/DecisionCard.test.tsx`, `frontend/lib/useDecisionWarning.test.ts` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Decision card: ID, status, summary, influenced chapters (AC-8) | **PASS** |
| Frozen/binding edit blocked with Italian explanation | **PASS** |
| `useDecisionWarning` returns amber-state payload for Integration A | **PASS** |
| DecisionInspectorSection accordion for Context Inspector | **PASS** |
| `thesisos:ask-reviewer` custom event with decision id | **PASS** |
| Tests + build | **PASS** (see CI) |

---

## Component Summary

### DecisionCard

- Renders `displayId` (mono), **Vincolante** / **Aperta** badge, 2-line summary, **Influenza: Cap. …**
- **Leggi** expands full operator-facing summary (inline accordion)
- **Chiedi al revisore** dispatches `thesisos:ask-reviewer` with `{ decisionId }` for PX2-EWO-003
- Frozen decisions: read-only hint + blocked modal on edit attempt (`Decisione vincolante — non modificabile`)
- **Modifica** hidden for Vincolante; shown only for Aperta (authoring remains out of scope)

### DecisionInspectorSection

- Accordion section **Decisioni vincolanti** — default open when binding decisions exist
- Shows top 3 relevant binding decisions via `topRelevantDecisions()`
- Empty state when none relevant
- **No ContextInspector edits** — Integration A imports this component

### decisionClient.ts

- `parseDecisionsFromPacket()` — enriches `DecisionRef` from existing ContextPacket (no backend)
- `formatDecisionDisplayId`, `parseInfluencedChapters`, `findConflictingDecision`
- `dispatchAskReviewer()` / `ASK_REVIEWER_EVENT` constant

### useDecisionWarning

Returns `{ active, message, decisionId?, decision? }`:

- `active: true` when binding decision influences active entity chapter **and** selection overlaps decision keywords
- `message: "Attenzione: decisione vincolante"` (Spec §6.4 / §11.1)

---

## Integration A Wiring (Supervisor)

Sub-agent A owns `ContextBar.tsx` and `ContextInspector.tsx`. After wave merge:

### 1. ContextInspector — Decision section

```tsx
import { DecisionInspectorSection } from "@/components/decisions/DecisionInspectorSection";

// Inside Contesto tab accordion list:
<DecisionInspectorSection packet={packet} />
```

Place after **Ambito**, before **Vincoli corpus** (UI spec §5.4).

### 2. ContextBar — Amber warning state

```tsx
import { useDecisionWarning } from "@/lib/useDecisionWarning";

// In ContextBar (or parent that passes props):
const warning = useDecisionWarning({
  packet,
  selectionText, // from editor selection state, debounced 300ms per spec §11.3
});

// Apply warning classes to bar container when warning.active:
className={cn(
  "...",
  warning.active && "border-warning/30 bg-warning/5"
)}

// Pass conflict to DecisionBadge:
<DecisionBadge decisions={packet.decisions} conflict={warning.active} />

// Optional: scope chip AlertTriangle + click → Contesto tab, scroll to decision-inspector-section
```

### 3. Ask-reviewer listener (PX2-EWO-003)

```tsx
window.addEventListener("thesisos:ask-reviewer", (e: Event) => {
  const { decisionId } = (e as CustomEvent).detail;
  // Open AI panel with decision preloaded in action packet
});
```

### 4. Editor frozen guard (optional, PX2-EWO-002 boundary)

Before inline decision edit from editor, call `attemptDecisionEdit(decision)` from `DecisionCard.tsx` exports or check `decision.frozen` via `parseDecisionsFromPacket`.

---

## Regression

- PX-1 `DecisionBadge` count unchanged when `conflict={false}` (default)
- No backend / ContextPacket schema changes
- ContextBar.test.tsx unaffected (Integration A adds warning tests)

---

## WO-TRACE

```text
PX2-EWO-001 → PX2-EWO-005 → Integration A → PX2-EWO-003 (ask-reviewer)
```
