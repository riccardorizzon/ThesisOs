# QWO-PX2-001-R1 — Evidence Bundle Index

**Run:** QWO-PX2-001-R1  
**Date:** 2026-07-05  
**Verdict:** PASS (re-confirmed)

## Artifacts

| File | Content |
|------|---------|
| `preflight.md` | Pre-flight environment declaration |
| `qwo-px2-ci.log` | Full `make ci` output (2026-07-05) |
| `qwo-px2-m4.log` | `make unit-m4-recovery` (OR-3) |
| `qwo-px2-m5.log` | `make qualify-m5` (OR-7) |
| `qwo-px2-m6.log` | `make qualify-m6` (OR-6) |
| `qwo-px2-ac-tests.log` | AC-mapped frontend unit tests (70/70) |
| `qwo-px2-e2e.log` | E2E smoke (6/7, 1 expected drift) |

## External references

| Artifact | Path |
|----------|------|
| QC Certificate | `.asep/certificates/QWO-PX2-001-R1-20260705.yaml` |
| Qualification Report | `.asep/reports/QWO-PX2-001-R1.md` |
| Integration D | `.asep/reports/PX2-INTEGRATION-D.md` |
| PX2-EWO-008 Report | `.asep/reports/PX2-EWO-008-chrome-states.md` |

## AC evidence map (unit tests)

| AC | Primary test files |
|----|-------------------|
| AC-1 | `frontend/components/context/ContextBar.test.tsx` |
| AC-2 | `frontend/lib/useDecisionWarning.test.ts`, `DecisionInspectorSection.tsx` |
| AC-3 | `frontend/components/writing/MarkdownEditor.test.tsx` |
| AC-4, AC-5 | `frontend/components/writing/WritingAiPanel.test.tsx` |
| AC-6, AC-7 | `frontend/lib/citationInsert.test.ts`, `SourcePicker.test.tsx` |
| AC-8 | `frontend/components/decisions/DecisionCard.test.tsx` |
| AC-9 | `frontend/lib/continuaLink.test.ts`, `sessionState.test.ts` |
| AC-10 | `frontend/components/memory/ProposalBundleModal.test.tsx` |
| AC-11 | `frontend/components/review/ReviewCompare.test.tsx` |
| AC-12 | `frontend/lib/progress.test.ts` |
| AC-13 | OR regression logs + E2E px1 smoke (6/7) |
| AC-14 | `qwo-px2-ci.log` |
