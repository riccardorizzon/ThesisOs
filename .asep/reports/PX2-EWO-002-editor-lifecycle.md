# PX2-EWO-002 — Editor Lifecycle

**WorkOrder:** PX2-EWO-002  
**Sub-agent:** B  
**Type:** EWO (Alignment)  
**Date:** 2026-07-04  
**Verdict:** **IMPLEMENTED**

---

## Objective

Deliver **Markdown editor with debounced autosave**, **chapter lifecycle badges**
(`Bozza → In revisione → Approvato`), and **outline integration** with section anchors —
activating the PX-1 Writing three-panel shell into a working writing flow.

---

## Deliverables

| Artifact | Path |
|----------|------|
| MarkdownEditor (70ch, 3s debounce, section anchors) | `frontend/components/writing/MarkdownEditor.tsx` |
| Autosave chrome (Salvataggio… / Salvato / Non salvato) | `WritingEditorShell.tsx` |
| StatusBadge (Bozza / In revisione / Approvato) | `frontend/components/ui/StatusBadge.tsx` |
| Outline (36px rows, filter, section nav, ?section=) | `frontend/components/writing/WritingOutline.tsx` |
| Chapter API client (list, get, patch, 409 handling) | `frontend/lib/chapterClient.ts` |
| Conflict dialog | `WritingEditorShell.tsx` |
| Panel width tokens | `WritingWorkspace.tsx`, `tokens.css`, `tailwind.config.ts` |
| LinkedSourcesFooter stub | `frontend/components/writing/LinkedSourcesFooter.tsx` |
| Read-only banner <768px | `WritingWorkspace.tsx` |
| Routes | `frontend/app/writing/**` |
| Tests | `MarkdownEditor.test.tsx`, `WritingOutline.test.tsx`, `chapterClient.test.ts`, `WritingWorkspace.test.tsx`, `StatusBadge.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Editor autosave persists content without data loss on chapter switch (AC-3) | **PASS** — debounced PATCH via `chapterClient.update`; local draft retained on failure |
| Debounced save (3s) with visible save state | **PASS** — `SaveIndicator` + `saveStateLabel` |
| Outline shows chapters with StatusBadge | **PASS** — pill badges on dense rows |
| Section anchors navigable; URL `?section=` support | **PASS** — outline links + editor scroll-to-section |
| Version conflict shows operator dialog — no silent overwrite | **PASS** — 409 → "Capitolo modificato altrove" dialog |
| Three-panel widths match UI spec tokens at ≥1280px | **PASS** — `lg:w-outline`, `min-w-editor`, `lg:w-rail` |
| `/writing/[chapterId]` loads chapter content from API | **PASS** — `WritingEditorShell` fetches via `chapterClient.get` |
| Tests green | **PASS** — 160 frontend tests |

---

## Ownership compliance

| Path | Status |
|------|--------|
| `frontend/components/writing/**` (owned) | **COMPLIANT** |
| `frontend/components/ui/StatusBadge.tsx` | **COMPLIANT** |
| `frontend/lib/chapterClient.ts` | **COMPLIANT** |
| `frontend/app/writing/**` | **COMPLIANT** |
| `frontend/styles/tokens.css` | **UNCHANGED** — tokens already present |
| `backend/app/api/chapters.py` | **NOT TOUCHED** — adapter already complete |
| `components/context/**`, `sources/**`, `decisions/**` | **NOT TOUCHED** |
| AI panel internals | **NOT TOUCHED** — stub only |

---

## Tests run evidence

```text
cd frontend && npm run test     → 160 passed (41 files)
cd frontend && npx tsc --noEmit → PASS
```

Writing-specific new/updated tests:

- `MarkdownEditor.test.tsx` — 4 tests (debounce, draft on failure, section anchors)
- `WritingOutline.test.tsx` — 5 tests (StatusBadge, filter, ?section= links)
- `WritingWorkspace.test.tsx` — 6 tests (panel tokens, read-only banner, footer stub)
- `WritingEditorShell.test.tsx` — 2 tests (empty state, API load)
- `StatusBadge.test.tsx` — 3 tests
- `chapterClient.test.ts` — 7 tests (409 conflict)

---

## Out of scope (deferred)

- AI actions (PX2-EWO-003)
- Citation insertion / LinkedSourcesFooter population (PX2-EWO-004)
- Right rail tabs beyond AI stub (PX2-EWO-003)
- Review compare (PX2-EWO-007)
- Toolbar Cita / Find / Preview execution

---

## WO-TRACE

```text
PX1-EWO-007 (shell) → PX2-EWO-002 ✓ → PX2-EWO-003, PX2-EWO-004, PX2-EWO-007
```
