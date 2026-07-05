# PX2-EWO-003 — AI Proposal Queue

**WorkOrder:** PX2-EWO-003  
**Sub-agent:** D  
**Type:** EWO (Alignment)  
**Date:** 2026-07-04  
**Verdict:** **IMPLEMENTED**

---

## Objective

Activate **Writing AI panel** with selection-aware actions, **streaming responses**,
and **proposal queue** — Applica never silent-writes; all AI mutations go through
proposal flow per ADR-0039 and IR-2.

---

## Deliverables

| Artifact | Path |
|----------|------|
| RightRail (tabbed single slot) | `frontend/components/writing/RightRail.tsx` |
| RailTabs (⌘1–4, role=tablist) | `frontend/components/writing/RailTabs.tsx` |
| WritingAiPanel (streaming + Applica) | `frontend/components/writing/WritingAiPanel.tsx` |
| AI action catalog + stream client | `frontend/lib/aiActions.ts` |
| Proposal queue (in-memory) | `frontend/lib/proposalQueue.ts` |
| Source peek placeholder | `frontend/components/writing/SourcePeekSlot.tsx` |
| Event wiring hook | `frontend/components/writing/rightRailIntegration.ts` |
| Writer panel entry | `backend/app/graph/writer.py` (`run_panel_action`) |
| Action prompts | `backend/app/graph/orchestration/writer_prompt.py` |
| Writing actions SSE endpoint | `backend/app/api/writing_actions.py` |
| Tests | `WritingAiPanel.test.tsx`, `RailTabs.test.tsx`, `test_writing_actions_api.py` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| ≥4 AI actions with streaming (Riscrivi, Verifica, Trova fonti, Espandi) | **PASS** |
| Applica → proposal queue; chapter unchanged until approved (AC-5) | **PASS** — `addProposal()` only |
| Right rail tabs ⌘1–4; default AI | **PASS** — `useRightRailEvents` / `RailTabs` |
| Selection changes action set; disabled tooltips (§15.4) | **PASS** — Italian `title` attrs |
| Cancel stops stream; partial discarded | **PASS** |
| Contesto tab renders ContextInspector (EWO-001) | **PASS** |
| Listen `thesisos:open-contesto-tab`, `thesisos:ask-reviewer` | **PASS** |
| Tests green | **PASS** |

---

## Component Summary

### RightRail + RailTabs (§5.4)

- Tabs: **AI | Contesto | Fonte | Revisione** — single content slot per tab
- `role="tablist"` / `role="tab"` / `role="tabpanel"` with `aria-selected`
- Keyboard: `⌘1…4` via `useRightRailEvents` / `bindRightRailEvents`
- Default tab: AI

### WritingAiPanel

- Four actions from `aiActions.ts` with selection/chapter-aware enablement
- Streams via `POST /writing/actions` SSE; falls back to mock tokens when LLM unavailable
- **Applica** → Anteprima → **Aggiungi alla coda** → `proposalQueue.addProposal()`
- Conflict banner when binding decision touches selection
- `aria-live="polite"` on stream complete

### Proposal queue (IR-2)

- `getPendingProposals()`, `addProposal()`, `getPendingProposalCount()`
- In-memory store; EWO-006 reads count via exported API

### Backend seam

- `LLMWriter.run_panel_action()` + `compose_writing_panel_wire()` per action
- Context packet summary passed on every request (IR-3)
- No graph topology change — panel entry only

---

## Ownership compliance

| Path | Status |
|------|--------|
| Owned frontend paths | **COMPLIANT** |
| `WritingWorkspace.tsx` layout | **NOT TOUCHED** — Integration B wires `RightRail` |
| ContextBar / Inspector internals | **NOT TOUCHED** — import only |
| MarkdownEditor, SourcePicker, ProposalBundleModal | **NOT TOUCHED** |

---

## Tests run evidence

```text
cd frontend && npm run test -- components/writing/WritingAiPanel.test.tsx components/writing/RailTabs.test.tsx
  → 7 passed

cd frontend && npx tsc --noEmit
  → PASS

backend/.venv/bin/pytest backend/tests/test_writing_actions_api.py -q
  → 3 passed
```

---

## Integration notes (Wave B)

- **Integration B** should replace `<WritingAiPanel />` in `WritingWorkspace` with `<RightRail />`, passing `contextPacket`, `selectionText`, `chapterContent`
- **PX2-EWO-004** fills `SourcePeekSlot` in Fonte tab
- **PX2-EWO-006** consumes `getPendingProposalCount()` for session close bundle
- **PX2-EWO-007** replaces Revisione placeholder

---

## WO-TRACE

```text
PX2-EWO-001 + PX2-EWO-002 → PX2-EWO-003 → PX2-EWO-006, PX2-EWO-007
```
