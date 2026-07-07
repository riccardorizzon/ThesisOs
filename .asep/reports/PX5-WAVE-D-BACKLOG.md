# PX-5 Wave D — Backlog Definition

> **Authority:** Architect (design session)  
> **Date:** 2026-07-07  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-5 Research  
> **Scope:** Wave D — discovery rails (lens · inspector · serendipity · selection shell)

---

## Functional objective

Deliver the **discovery and inspection shell** on `/research/canvas` — upgrading the
Wave C viewport-only page to the full canvas layout with lens rail, inspector rail,
multi-select, and deterministic serendipity suggestions.

**Product source:** `docs/product/specs/px5-research-experience-v1.md` §5.4, §6, §7, §10  
**UI source:** `design-system/thesisos/px5-research-experience-ui-spec.md` §4–§8, §14

**Capabilities addressed:**

| ID | Capability | Wave D coverage |
|----|------------|-----------------|
| **PX-5.2** | Discovery Lenses | Lens rail + header dropdown + filter popover |
| **PX-5.3** | Serendipity Paths | Deterministic suggestion strip |
| **PX-5.6** | Cross-Module Navigation | Inspector deep links; Explain already wired (Wave C) |
| *(partial)* | **PX-5.4** Selection | Multi-select gestures; basket drawer **deferred Wave E** |

**Status (2026-07-07):** Wave D **authorized** — `.asep/reports/PX5-AUTHORIZATION-WAVE-D-20260707.md`

---

## Wave D DAG

```text
PX5-EWO-001  Research Experience Spec        ✓ PASS (Wave A)
      ↓
PX5-EWO-002  Research hub + route scaffolding ✓ PASS (Wave B)
      ↓
PX5-EWO-003  Canvas viewport + node layer   ✓ PASS (Wave C)
      ↓
PX5-EWO-004  Canvas shell + selection model ← Wave D (first executable)
      ↓
      ├──────────────────┬──────────────────┐
      ▼                  ▼                  │
PX5-EWO-005          PX5-EWO-006            │  (parallel after 004)
Inspector rail       Discovery lenses       │
      └──────────────────┴──────────────────┘
                         ↓
PX5-EWO-007  Serendipity strip + Wave D integration
      ↓
(future)     Basket · saved views · satellites · QWO (Wave E+)
```

| EWO | Title | Parallel after | Status |
|-----|-------|----------------|--------|
| **PX5-EWO-004** | Canvas shell + selection model | PX5-EWO-003 | **authorized** |
| **PX5-EWO-005** | Inspector rail | PX5-EWO-004 | **authorized** |
| **PX5-EWO-006** | Discovery lenses + lens rail | PX5-EWO-004 | **authorized** |
| **PX5-EWO-007** | Serendipity strip + integration | PX5-EWO-005, PX5-EWO-006 | **proposed** |

**First executable EWO (when authorized):** `PX5-EWO-004`

**Parallel dispatch:** EWO-005 and EWO-006 may run concurrently after EWO-004 PASS
(orchestrate-builders merge barrier before EWO-007).

---

## Explicit exclusions (Wave D)

| Feature | Owner | Rationale |
|---------|-------|-----------|
| Basket drawer + Writing handoff | Wave E | PX-5.4 / product §8 — session API + Context import |
| Saved views persistence | Wave E | PX-5.5 / product §9 — camera + lens store |
| Satellite nodes (source/author/decision/chapter) | Wave E | Graph API extension; AC-1 completion |
| Minimap | Wave E | UI spec §5.4 — deferred from Wave C |
| Cluster collapse + hard-limit modal | Wave E | product §5.2 — depends on satellite density |
| Discovery backend API | — | Lenses filter client-side on graph payload |
| MB2 Runtime / SoR / Constitution | px-exec | Engineering program boundary |
| QWO-PX5-001 qualification | Post Wave E | Requires basket + saved views AC-5/AC-6 |

---

## Baseline (Wave C delivered)

| Artifact | Path |
|----------|------|
| Viewport + concept layer | `frontend/components/research/canvas/ResearchCanvasViewport.tsx` |
| Canvas page (header only) | `frontend/components/research/ResearchCanvasPage.tsx` |
| Layout engine | `frontend/lib/canvasLayout.ts` |
| Graph fetch depth 2 | `frontend/app/research/canvas/page.tsx` |

**Wave C gaps Wave D closes:**

- Single-select only → multi-select (product §5.4)
- Selection chip overlay → inspector rail (UI spec §6)
- No lens rail → full shell layout (UI spec §4.1)
- No serendipity → suggestion strip (product §7)
- Page-level header → canvas header bar with lens/filters controls

---

## Candidate EWOs

### PX5-EWO-004 — Canvas shell + selection model

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  category: A
  program_mode: product
```

| Field | Value |
|-------|-------|
| **Category** | Infrastructure |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX5-EWO-003 PASS |

**Objective:** Replace the Wave C single-column page with the **three-region canvas
shell** and upgrade selection to product §5.4.

**Deliverables:**

- Refactor `ResearchCanvasPage` → shell layout (lens rail slot | canvas | inspector slot)
- Header bar: back, lens dropdown (disabled until EWO-006), filters popover stub, basket badge (count 0, disabled)
- Lift viewport transform + selection state to page/shell context
- Multi-select: `⌘`+click toggle, Shift+drag marquee, Esc clear
- Action bar footer: selection count; handoff buttons disabled until Wave E
- Responsive breakpoints per UI spec §14 (desktop-required message `<1024px`)
- `ResearchCanvasShell.test.tsx`

**Acceptance:**

- [ ] Shell matches UI spec §4.1 region widths (240px lens, flex canvas, 320px inspector slot)
- [ ] Multi-select updates selection set; single click replaces when no modifier
- [ ] Esc clears selection
- [ ] Viewport pan/zoom/selection coexist — node click does not trigger pan
- [ ] `<1024px` shows desktop-required message (RR-8)
- [ ] `make ci` green; Wave C viewport regression preserved

**Forbidden:** Lens filter logic, inspector content, serendipity, basket persistence

---

### PX5-EWO-005 — Inspector rail

| Field | Value |
|-------|-------|
| **Category** | Alignment |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX5-EWO-004 |

**Objective:** Populate the inspector rail (PP-1 tab pattern) for selected concept nodes.

**Deliverables:**

- `frontend/components/research/canvas/ResearchInspectorRail.tsx`
- Tabs: **Dettaglio** · **Collegamenti** · **Azioni** (UI spec §6)
- Dettaglio: title, lifecycle badge, confidence, summary snippet from concept envelope
- Collegamenti: linked sources/concepts/chapters as deep links (reuse knowledge client)
- Azioni: Apri Explain · Aggiungi al basket (basket action disabled/stub until Wave E)
- Multi-select mode: count + batch action stub
- `⌘\` toggle inspector (UI spec §13)
- Unit tests for empty/single/multi states

**Acceptance:**

- [ ] Single concept select populates all three tabs
- [ ] Apri Explain navigates to `/knowledge/[slug]` (KR-13)
- [ ] Collegamenti links resolve to existing routes (sources, graph, writing)
- [ ] Multi-select shows batch summary, not per-node tabs
- [ ] No duplicate concept detail page — inspector is summary only (RR-6)
- [ ] `make ci` green

**Data sources:** Existing concept detail/header APIs; `linked_counts` on envelope.
No new backend endpoints required.

---

### PX5-EWO-006 — Discovery lenses + lens rail

| Field | Value |
|-------|-------|
| **Category** | Alignment |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX5-EWO-004 |

**Objective:** Implement discovery lenses (product §6) reframing the visible subgraph
without duplicate nodes (RR-2).

**Deliverables:**

- `frontend/lib/canvasLenses.ts` — lens definitions + filter predicates
- `frontend/components/research/canvas/ResearchLensRail.tsx` (UI spec §7)
- Header lens dropdown mirrors rail selection
- Filter popover: stato, relation type, core only, hide deprecated (UI spec §4.2)
- Lens catalog:

| Lens ID | Label | Filter rule |
|---------|-------|-------------|
| L-all | Panorama | No filter (default) |
| L-gap | Lacune | Concepts with `linked_counts.sources < 2` |
| L-chapter | Capitolo attivo | Concepts linked to active Writing chapter (Context) |
| L-author | Autore | Subgraph around selected author (picker when multiple) |
| L-controversy | Controversie | Nodes incident to `contradicts` edges |
| L-unread | Non letti | Source satellites with zero annotations |

- Filtered graph passed to viewport; lens switch preserves camera when centroid unchanged
- Loading shimmer ≤300ms on lens switch (UI spec §7)
- Unit tests per lens predicate

**Acceptance:**

- [ ] All six lenses selectable; active lens indicated (accent border)
- [ ] L-controversy and L-gap produce deterministic subgraphs on stub + live graph
- [ ] L-chapter reads active chapter from Context packet when available; graceful empty when not
- [ ] L-author and L-unread: **stub with catalog/dev fallback** if backend lacks author/annotation index — documented in EWO report (not blocking PASS)
- [ ] Filter popover composes with active lens (AND semantics)
- [ ] Deprecated hidden by default; toggle restores (RR-3)
- [ ] No duplicate nodes after reframe (RR-2)
- [ ] `make ci` green

**Risk mitigation:** L-author / L-unread may ship as **partial** with dev-catalog
evidence; full data wiring deferred to Wave E satellite work.

---

### PX5-EWO-007 — Serendipity strip + Wave D integration

| Field | Value |
|-------|-------|
| **Category** | Release |
| **Layer** | Business (Product Plane) |
| **Depends on** | PX5-EWO-005, PX5-EWO-006 |

**Objective:** Deterministic serendipity suggestions (product §7) + merged Wave D
integration gate.

**Deliverables:**

- `frontend/lib/canvasSerendipity.ts` — ranked suggestions from graph topology + reading state
- `frontend/components/research/canvas/SerendipityStrip.tsx` (UI spec §8)
- Suggestion types: bridge concept, unread source, decision tension, chapter gap
- Card action: pan viewport + 2s pulse highlight on target nodes/edges
- Hub `ResearchHubPage`: acknowledge canvas rails in copy (no saved-view restore yet)
- `.asep/reports/PX5-INTEGRATION-D.md` — integration checklist
- `.asep/reports/PX5-EWO-007-serendipity-integration.md`

**Acceptance:**

- [ ] Strip renders ≤5 suggestion cards; horizontal scroll
- [ ] Suggestions are deterministic (same graph → same cards) — RR-7
- [ ] Bridge/controversy suggestions use edge topology only
- [ ] Card click pans and highlights targets
- [ ] Full shell: lens rail + canvas + inspector + serendipity + action bar
- [ ] PX5-INTEGRATION-D.md PASS
- [ ] `make ci` green; PX-2/PX-3/PX-4 regression preserved

**Forbidden:** AI-generated suggestions as primary surface (RR-7)

---

## Wave D exit criteria (PASS)

Wave D is **PASS** only when **all** of:

1. **PX5-EWO-004**, **005**, **006**, **007** each report PASS  
2. **PX5-INTEGRATION-D** verdict PASS  
3. Product §6 lenses operable (L-all, L-gap, L-controversy minimum; L-chapter with Context)  
4. Inspector rail populated for concept selection  
5. Serendipity strip renders deterministic suggestions  
6. `make ci` green; no PX-2/PX-3/PX-4 regression  

```text
Qualification preview (QWO-PX5-001 — not Wave D scope):
  AC-4 partial ✓ (lenses)
  AC-5 ✗ (basket — Wave E)
  AC-6 ✗ (saved views — Wave E)
```

---

## Wave E preview (not authorized)

Spawn after Wave D PASS + Architect review:

| EWO (draft) | Title | Capabilities |
|-------------|-------|--------------|
| PX5-EWO-008 | Satellite node layer | PX-5.1 completion; graph API extension |
| PX5-EWO-009 | Basket + Writing handoff | PX-5.4; product §8 |
| PX5-EWO-010 | Saved views persistence | PX-5.5; product §9 |
| PX5-EWO-011 | Minimap + cluster + hard-limit modal | product §5.2–§5.3 |
| QWO-PX5-001 | Milestone qualification | product §16 AC-1…AC-10 |

---

## Execution model

Engineering program (not conformance). Product code only in `frontend/` and
`backend/app/` per program constraints.

```text
PX5-EWO-003 PASS (Wave C)
      ↓
Architect review this backlog
      ↓
AUTHORIZE PX-5 Wave D → PX5-EWO-004
      ↓
(optional parallel) EWO-005 + EWO-006
      ↓
PX5-EWO-007 integration
      ↓
Spawn Wave E backlog
```

**Authorization command (when ready):**

```text
AUTHORIZE PX-5 Wave D
```

Equivalent: `ASEP: AUTHORIZE PX5-EWO-004`

---

## Known risks

| Risk | Mitigation |
|------|------------|
| L-author / L-unread lack backend indices | Stub on catalog; partial PASS documented; complete in Wave E |
| L-chapter needs Writing session context | Read Context packet; empty state when no active chapter |
| Marquee select + pan gesture conflict | Pointer capture rules in EWO-004; test coverage |
| Lens filter + performance banner interaction | Recompute limits on filtered node count |
| UI spec Wave C/D component hints outdated | This backlog supersedes §15 wave hints for lens/serendipity |

---

## WO-TRACE

```text
PX5-EWO-003 PASS (Wave C)
  → ASEP: design PX-5 Wave D backlog (this document)
  → Architect review → AUTHORIZE Wave D → PX5-EWO-004…007
  → Wave E (basket · saved views · satellites · QWO)
```
