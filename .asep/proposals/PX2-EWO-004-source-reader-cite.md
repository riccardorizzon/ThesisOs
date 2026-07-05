# Engineering WorkOrder Proposal — PX2-EWO-004

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-004-source-reader-cite`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §3.3, §6.4–6.5  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §6.4–6.6, §8

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-004 |
| **Sub-agent** | D |
| **Type** | **EWO** — Grounding |
| **EWO category** | **Grounding** |
| **Capability** | `px2-ewo-004-source-reader-cite` |
| **User capability** | **PX-2.3** Source Interaction |
| **Milestone** | PX-2 |
| **Layer** | Business |
| **Wave** | px2-parallel/wave_b |
| **Depends on** | PX2-EWO-002 |

---

## Objective

Deliver **SourcePicker**, **SourceReader** (full + peek modes), and **cite flow**
(⌘⇧C) with exclusion blocking — operator reads corpus, inserts citation markers,
and links sources to active chapter without leaving Writing.

---

## Ownership (exclusive)

```text
frontend/components/sources/SourcePicker.tsx
frontend/components/sources/SourceReader.tsx
frontend/components/library/SourcesView.tsx (extend search/filter)
frontend/components/library/SourceDetailView.tsx (extend)
frontend/lib/corpusClient.ts
frontend/lib/citationInsert.ts
frontend/app/sources/**
backend/app/graph/retriever.py (corpus query for picker — read only)
backend/app/graph/corpus_query.py (if exists)
```

**Forbidden:** `components/writing/MarkdownEditor.tsx` (consume cite API only),
`components/context/**`, decision components.

---

## Scope

### In scope

1. **SourcePicker modal** — 3 columns (Recenti / Collegate / Risultati); debounced search 200ms
2. **SourceReader** — metadata, body, highlight/copy quote, prev/next in results
3. **Peek mode** — Fonte tab in right rail; dismiss returns focus to editor (IR-8)
4. **Cite flow** — ⌘⇧C → picker → peek → insert citation marker at cursor
5. **Exclusion block** — excluded sources visible; cite blocked with plain-language reason (AC-7, IR-4)
6. **Filter chips** — candidata / approvata / esclusa on Sources route
7. **Link to chapter** — "Collega al capitolo" from Sources detail
8. **LinkedSourcesFooter** — chapter linked sources count

### Out of scope

- Full source import (PX-3)
- Annotation sync (PX-3)
- Citation validator W-06 (PX-6)
- Concept tags beyond stub (PX-4)

---

## Constraints

- IR-4: excluded corpus never citable
- IR-8: focus returns to editor after peek dismiss
- Read-only corpus — no import pipeline
- Italian operator messages for blocked cite (spec §19)

---

## Acceptance Criteria

- [ ] Source picker → peek reader → cite inserts marker at cursor (AC-6)
- [ ] Excluded source cite attempt blocked with operator message (AC-7)
- [ ] Sources route search + filter chips functional
- [ ] Peek reader opens in Fonte tab; Esc dismisses with editor focus restored
- [ ] ContextBar citation count updates after cite
- [ ] Sticky "Torna a Scrittura" when chapter context in URL
- [ ] Tests + `make ci` green

---

## Tests

- `SourcePicker.test.tsx` — search, exclusion block
- `SourceReader.test.tsx` — peek vs full, quote copy
- `citationInsert.test.ts` — marker format at cursor

---

## Regression

- `make ci`
- PX-1 Sources grid still renders
- OR-3 corpus exclusion rules preserved

---

## WO-TRACE

```text
PX2-EWO-002 → PX2-EWO-004
```
