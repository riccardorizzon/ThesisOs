# Engineering WorkOrder Proposal — PX2-EWO-002

> **Status:** ⏳ **PROPOSED** — dispatch blocked until amendment ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-002-editor-lifecycle`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §5.2–5.3, §6.1  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §5.2–5.3

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-002 |
| **Sub-agent** | B |
| **Type** | **EWO** — Alignment |
| **EWO category** | **Alignment** |
| **Capability** | `px2-ewo-002-editor-lifecycle` |
| **User capability** | **PX-2.2** Writing Flow |
| **Milestone** | PX-2 |
| **Layer** | Business + Infrastructure (M6 chapter seam) |
| **Wave** | px2-parallel/wave_a |
| **Depends on** | PX-1 complete (PX1-EWO-007 shell) |

---

## Objective

Deliver **Markdown editor with debounced autosave**, **chapter lifecycle badges**
(`Bozza → In revisione → Approvato`), and **outline integration** with section anchors —
activating the PX-1 Writing three-panel shell into a working writing flow.

---

## Ownership (exclusive)

```text
frontend/components/writing/MarkdownEditor.tsx
frontend/components/writing/WritingEditorShell.tsx (extend)
frontend/components/writing/WritingOutline.tsx (extend)
frontend/components/writing/WritingWorkspace.tsx (panel widths, tokens)
frontend/components/ui/StatusBadge.tsx
frontend/lib/chapterClient.ts
frontend/app/writing/**
backend/app/api/chapters.py (adapter only — no service rewrite)
backend/app/schemas/chapter.py (if needed for status enum)
```

**Forbidden:** `components/context/**`, `components/sources/**`, AI panel, graph nodes.

---

## Scope

### In scope

1. **MarkdownEditor** — 70ch measure, debounced autosave (3s), section anchors from headings
2. **Autosave chrome** — `Salvataggio…` / `Salvato` inline states (spec §18)
3. **Chapter lifecycle** — StatusBadge on outline rows; deterministic status transitions (ADR-0040)
4. **Outline** — 36px dense rows, filter, active section highlight
5. **Panel layout tokens** — `--outline-width`, `--editor-min-width`, `--row-height-dense`
6. **Chapter API client** — list, get, patch with `expected_version` conflict handling
7. **Multi-tab conflict dialog** — "Capitolo modificato altrove" (spec §14.3)
8. **LinkedSourcesFooter** stub slot (populated by PX2-EWO-004)

### Out of scope

- AI actions (PX2-EWO-003)
- Citation insertion (PX2-EWO-004)
- Right rail tabs (PX2-EWO-003)
- Review compare (PX2-EWO-007)

---

## Constraints

- ADR-0040 deterministic progress — status from chapter metadata, never LLM
- IR-6: progress formula unchanged from PX-1
- ChapterService is sole writer (ADR-0032); API adapter thin only
- 409 conflict on stale `expected_version` (ADR-0033)
- Below 768px: read-only banner per spec §21

---

## Acceptance Criteria

- [ ] Editor autosave persists content without data loss on chapter switch (AC-3)
- [ ] Debounced save (3s) with visible save state
- [ ] Outline shows chapters with StatusBadge (Bozza / In revisione / Approvato)
- [ ] Section anchors navigable from outline; URL `?section=` support
- [ ] Version conflict shows operator dialog — no silent overwrite
- [ ] Three-panel widths match UI spec tokens at ≥1280px
- [ ] `/writing/[chapterId]` loads chapter content from API
- [ ] Tests + `make ci` green

---

## Tests

- `MarkdownEditor.test.tsx` — autosave debounce, local draft on failure
- `WritingOutline.test.tsx` — status badges, section navigation
- `chapterClient.test.ts` — conflict handling
- Extend `WritingWorkspace.test.tsx` — panel layout

---

## Regression

- `make ci`
- PX-1 writing shell routes still render
- OR-1…OR-7 unchanged

---

## WO-TRACE

```text
PX1-EWO-007 (shell) → PX2-EWO-002 → PX2-EWO-003, PX2-EWO-004, PX2-EWO-007
```
