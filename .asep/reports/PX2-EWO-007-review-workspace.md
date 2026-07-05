# PX2-EWO-007 — Review Workspace

**WorkOrder:** PX2-EWO-007  
**Sub-agent:** G  
**Type:** EWO (Alignment)  
**Date:** 2026-07-04  
**Verdict:** **IMPLEMENTED**

---

## Objective

Activate **Review workspace** with side-by-side **ReviewCompare**, paragraph-level
hunk accept/reject, and operator-confirmed persistence — distinct from `/ai` power mode.

---

## Deliverables

| Artifact | Path |
|----------|------|
| ReviewCompare (side-by-side + hunk selection) | `frontend/components/review/ReviewCompare.tsx` |
| ReviewMode (extended — ContextBar, chapter selector, compare flow) | `frontend/components/review/ReviewMode.tsx` |
| ReviewComparePanel (wrapper) | `frontend/components/review/ReviewComparePanel.tsx` |
| RevisionQueuePanel (pending list → `/review?chapter=`) | `frontend/components/review/RevisionQueuePanel.tsx` |
| Paragraph hunk diff | `frontend/lib/reviewDiff.ts` |
| Entry hook `dispatchOpenReview` | `frontend/components/review/reviewIntegration.ts` |
| Review route (full-width + ContextBar) | `frontend/app/review/page.tsx` |
| Proposal queue extensions | `frontend/lib/proposalQueue.ts` |
| Tests | `ReviewCompare.test.tsx`, `ReviewMode.test.tsx`, `reviewDiff.test.ts` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Review accept/reject changes chapter with operator confirm (AC-11, IR-2) | **PASS** — confirm dialog before `chapterClient.update` |
| Side-by-side compare with paragraph-level partial accept | **PASS** — `reviewDiff` + hunk selection in `ReviewCompare` |
| Entry from Home, Writing (`dispatchOpenReview`), outline context | **PASS** — event hook exported; URL `?chapter=` supported |
| `/review` full-width layout with ContextBar | **PASS** — `WritingContextBar` in `ReviewMode` |
| Revisione tab shows pending revisions (Integration C) | **PASS** — `RevisionQueuePanel` exported |
| Tests + tsc green | **PASS** — 20 tests, `tsc --noEmit` clean |

---

## Component Summary

### ReviewCompare (§6.6)

- Equal columns: **Originale** (read-only) vs **Proposta** (AI label)
- Paragraph hunks with diff styling (`bg-success/10`, `bg-danger/10 line-through`)
- Selectable hunks on proposed side (`ring-accent` when selected)
- Actions: **Accetta tutto**, **Accetta parziale**, **Rifiuta**, **Modifica** (→ Writing)
- Operator confirm dialog (IR-2) before persist or reject
- Side-by-side loading skeleton with stagger

### reviewDiff

- `splitParagraphs`, `applyProposalToContent`, `computeParagraphDiff`
- LCS-based paragraph alignment; `mergeAcceptedHunks` for partial accept

### RevisionQueuePanel

- Lists pending proposals from `proposalQueue`
- Links to `/review?chapter=[id]&proposal=[id]`
- Empty state: "Nessuna revisione in sospeso" + "Avvia revisione"

### Entry hooks

- `dispatchOpenReview(chapterId?)` → `thesisos:open-review` custom event
- `ReviewMode` listens and navigates to `/review?chapter=`

---

## Data flow

```text
proposalQueue (pending) + chapterClient.get (original)
  → applyProposalToContent → computeParagraphDiff
  → operator selects hunks → confirm
  → chapterClient.update (accept) | approveProposal/rejectProposal
```

---

## Regression

| Check | Result |
|-------|--------|
| Owned tests (20) | **PASS** |
| `tsc --noEmit` | **PASS** |
| `/ai` route | **UNCHANGED** |
| RightRail.tsx | **UNCHANGED** (Integration C wires RevisionQueuePanel) |

---

## WO-TRACE

```text
PX2-EWO-002 + PX2-EWO-003 → PX2-EWO-007 → PX2-EWO-008
```
