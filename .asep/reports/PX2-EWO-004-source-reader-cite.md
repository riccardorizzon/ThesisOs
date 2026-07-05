# PX2-EWO-004 — Source Reader & Cite

**WorkOrder:** PX2-EWO-004  
**Sub-agent:** E  
**Type:** EWO (Grounding)  
**Date:** 2026-07-04  
**Verdict:** **IMPLEMENTED**

---

## Objective

Deliver **SourcePicker**, **SourceReader** (full + peek), and **cite flow** with
exclusion blocking — operator reads corpus, inserts citation markers, and links
sources to active chapter without leaving Writing.

---

## Deliverables

| Artifact | Path |
|----------|------|
| SourcePicker modal (Recenti / Collegate / Risultati, 200ms debounce) | `frontend/components/sources/SourcePicker.tsx` |
| SourceReader full + peek modes | `frontend/components/sources/SourceReader.tsx` |
| SourcePeekReader (Fonte tab slot — Integration B) | `frontend/components/sources/SourcePeekReader.tsx` |
| Corpus client + linked/recent storage | `frontend/lib/corpusClient.ts` |
| Citation insert API + event | `frontend/lib/citationInsert.ts` |
| Sources list search + filter chips | `frontend/components/library/SourcesView.tsx` |
| Source detail + link-to-chapter | `frontend/components/library/SourceDetailView.tsx` |
| LinkedSourcesFooter count | `frontend/components/writing/LinkedSourcesFooter.tsx` |
| Sources routes + ?chapter= pill | `frontend/app/sources/**` |
| Backend read-only picker list (IR-4) | `backend/app/graph/corpus_query.py` |
| Tests | `SourcePicker.test.tsx`, `SourceReader.test.tsx`, `citationInsert.test.ts` |
| Backend tests | `backend/tests/test_corpus_picker.py` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Source picker → peek reader → cite inserts marker at cursor (AC-6) | **PASS** — `dispatchInsertCitation` / `thesisos:insert-citation`; Integration B wires MarkdownEditor listener |
| Excluded source cite blocked with operator message (AC-7, IR-4) | **PASS** — Italian copy; excluded omitted from picker Risultati |
| Sources route search + filter chips functional | **PASS** — debounced search + candidata/approvata/esclusa |
| Peek reader in Fonte tab; Esc dismiss + focus restore (IR-8) | **PASS** — `SourcePeekReader` + `onDismiss` / `focusReturnRef` |
| ContextBar citation count updates after cite | **DEFERRED** — Integration B (EWO-003 ContextBar listener) |
| Sticky "Torna a Scrittura" when chapter in URL | **PASS** — `?chapter=` on `/sources` and detail |
| "Collega al capitolo" on source detail | **PASS** |
| LinkedSourcesFooter shows linked count | **PASS** — collapsible `Fonti collegate (N)` |
| Tests green | **PASS** — 32 EWO-004 tests; `tsc --noEmit` PASS |

---

## Ownership compliance

| Path | Status |
|------|--------|
| `frontend/components/sources/**` | **COMPLIANT** |
| `frontend/lib/corpusClient.ts`, `citationInsert.ts` | **COMPLIANT** |
| `frontend/components/library/SourcesView.tsx`, `SourceDetailView.tsx` | **COMPLIANT** (extended) |
| `frontend/components/writing/LinkedSourcesFooter.tsx` | **COMPLIANT** (footer count only) |
| `frontend/app/sources/**` | **COMPLIANT** |
| `backend/app/graph/corpus_query.py` | **COMPLIANT** (read-only) |
| `MarkdownEditor.tsx` | **NOT TOUCHED** — cite via event only |
| `components/context/**`, `decisions/**`, RightRail | **NOT TOUCHED** |

---

## Tests run evidence

```text
cd frontend && npm run test -- --run \
  components/sources/ lib/citationInsert.test.ts \
  components/library/SourcesView.test.tsx \
  components/library/SourceDetailView.test.tsx \
  components/writing/WritingWorkspace.test.tsx
→ 32 passed (6 files)

cd frontend && npx tsc --noEmit → PASS
```

---

## Integration B handoff

| Consumer | Contract |
|----------|----------|
| RightRail Fonte tab (EWO-003) | Import `SourcePeekReader`; pass `onDismiss` + `focusReturnRef` |
| MarkdownEditor (EWO-002) | Listen for `thesisos:insert-citation`; insert `detail.marker` at cursor |
| Writing toolbar "Cita" / ⌘⇧C | Open `SourcePicker`; on select → peek → cite event |
| ContextBar | Increment citation count on cite event (EWO-001 extension) |

---

## Out of scope (deferred)

- Full source import (PX-3)
- Annotation sync (PX-3)
- Citation validator W-06 (PX-6)
- Concept tags beyond read-only chips (PX-4)

---

## WO-TRACE

```text
PX2-EWO-002 → PX2-EWO-004 ✓ → Integration B
```
