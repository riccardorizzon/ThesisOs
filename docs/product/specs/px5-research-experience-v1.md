# PX-5 — Research Experience

> **Product Specification v1** · 2026-07-06  
> **Status:** PROPOSED — ready for UX handoff after Architect sign-off  
> **Builds on:** PX-4 Knowledge (promoted @ `px4-complete`)  
> **Does not amend:** Product Constitution v1.0, ADR-0034…0042, PX-2/PX-3/PX-4 specifications  
> **Does not modify:** PX-3 guided research semantics or PX-4 Explain Page behavior

---

## 0. Document purpose

Self-contained product specification for **PX-5 Research** — the **spatial research
canvas**. UX may design from this document without product assumptions. Engineering
receives this artifact after UX freeze.

**PX-5 scope:** exploratory map of the research landscape — serendipitous discovery,
multi-entity spatial layout, and explicit Writing handoff. **Not** prose editing,
**not** bounded navigation graph (PX-3), **not** canonical concept detail (PX-4).

---

## 1. Product thesis

```text
PX-3 = Knowledge (guided)  →  What path should I follow?
PX-4 = Knowledge (canonical) →  What does this concept mean?
PX-5 = Research (canvas)   →  What might I discover?
```

```text
Knowledge  →  Research  →  Writing  →  Output
```

**Invariant (inherited):** Research never edits chapter prose — handoff to Writing
(PX-2) is always explicit (KR-6).

**Core belief (ADR-0037):** The canvas renders the **same concept graph** as Knowledge
— concepts remain canonical; sources, authors, and chapters appear as **linked
satellites**, not alternate identities (INV-KM-1, INV-KM-5).

---

## 2. Capabilities map

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-5.1** | Spatial Canvas | Explore concepts and linked entities on a pan/zoom map |
| **PX-5.2** | Discovery Lenses | Reframe the map by question, chapter, author, or gap |
| **PX-5.3** | Serendipity Paths | Surface non-obvious links and unread bridges |
| **PX-5.4** | Canvas Selection | Multi-select nodes for basket and Writing handoff |
| **PX-5.5** | Saved Views | Persist camera, filters, and focus for resume |
| **PX-5.6** | Cross-Module Navigation | Jump to Explain, Source reader, Writing without losing canvas state |

---

## 3. Module boundary matrix (normative)

| Surface | Milestone | Route | Intent | Node types |
|---------|-----------|-------|--------|------------|
| Guided exploration | PX-3 | `/research/guided` | Linear trail + basket | Knowledge Object refs |
| Knowledge navigation graph | PX-3/PX-4 | `/knowledge/graph` | Bounded 1-hop navigation | Concepts only |
| Explain Page | PX-4 | `/knowledge/[slug]` | Canonical concept detail | Single concept |
| **Research canvas** | **PX-5** | **`/research/canvas`** | **Spatial discovery** | **Concepts + sources + authors + decisions** |
| Research hub | PX-5 (entry) | `/research` | Choose mode; resume saved view | — |

**Route note:** ADR-0036 registers `/research` and `/research/[conceptId]`. PX-5 maps
`/research/[conceptId]` → canvas focus on that concept slug. Guided trail remains at
`/research/guided` (PX-3.10); hub at `/research` links both modes.

---

## 4. Canvas node model

All canvas nodes are **projections** of persisted Knowledge entities — no canvas-only
identity (INV-KM-2 preserved).

### 4.1 Node kinds

| Kind | Visual role | Data source | Max default visible |
|------|-------------|-------------|---------------------|
| **concept** | Primary hex/circle | PX-4 concept store | 80 |
| **source** | Satellite book tile | Source M:N links | 40 |
| **author** | Satellite person chip | Author index | 20 |
| **decision** | Diamond badge | Decision cards (PX-2.4) | 15 |
| **chapter** | Outline anchor (muted) | Chapter ↔ concept links | 10 |

**Passage** and **annotation** nodes are **out of scope** for v1 canvas — open via
Source reader from a source satellite (PX-3.6).

### 4.2 Edge kinds

| Edge | Style | Source |
|------|-------|--------|
| concept ↔ concept | Typed: supports · contradicts · extends · related | ADR-0037 relations |
| concept ↔ source | Dashed link | `concept_sources` |
| concept ↔ decision | Dotted | `concept_decisions` |
| concept ↔ chapter | Thin gray | `concept_chapters` |
| author ↔ source | Hairline | author bibliography |

Contradiction edges use warning color; supports use success (inherits PP tokens).

### 4.3 Node envelope (canvas)

Each node shows:

| Field | Display |
|-------|---------|
| title | Truncated label (max 32 chars) |
| kind | Icon + badge |
| knowledge_state | Lifecycle badge (PP-5) |
| is_core | Accent ring if core concept |
| link_count | Tooltip on hover |

Double-click concept → Explain Page (KR-13). Single-click → inspector rail (PP-1).

---

## 5. Spatial layout and interaction

### 5.1 Layout engine (product requirements)

| Requirement | Rule |
|-------------|------|
| Initial layout | Force-directed from focus concept or core set |
| Focus entry | `/research/canvas?focus={slug}` centers on concept |
| Pan / zoom | Infinite canvas; min zoom 25%, max 400% |
| Minimap | Optional toggle; shows viewport rectangle |
| Cluster collapse | When > soft limit, aggregate distant nodes into cluster chips |
| Performance | Viewport culling required; never render off-screen labels at full density |

### 5.2 Default viewport

| Parameter | Value |
|-----------|-------|
| Initial nodes | Up to **80** concepts + linked satellites within 2-hop |
| Default hop depth | **2** (vs PX-3 graph default 1) |
| Soft limit | **150** rendered nodes — show performance banner |
| Hard limit | **300** — force lens filter or cluster mode; no silent drop |

**Distinction from PX-3 §10:** PX-3 graph caps at 100 with List fallback for
**navigation**. PX-5 canvas uses **spatial clustering** and **lens filters** instead
of List view — different operator intent (PP-10).

### 5.3 Expansion

Operator expands explicitly:

| Action | Effect |
|--------|--------|
| Expand node | Reveal 1-hop neighbors not yet visible |
| Expand cluster | Split aggregated cluster |
| Collapse branch | Hide descendants of node |
| Reset view | Return to focus + default depth |

Auto-expand beyond default depth requires confirmation if total would exceed soft limit.

### 5.4 Selection model

| Gesture | Behavior |
|---------|----------|
| Click | Select single node; inspector rail populates |
| `⌘`+click | Toggle multi-select |
| Shift+drag | Marquee multi-select |
| Esc | Clear selection |

Selection count visible in action bar. Multi-select enables basket add and Writing handoff.

---

## 6. Discovery lenses

Lenses reframe the canvas without changing underlying data.

| Lens ID | Label (IT) | Effect |
|---------|------------|--------|
| **L-all** | Panorama | Default — core + 2-hop |
| **L-gap** | Lacune | Concepts with <2 source links |
| **L-chapter** | Capitolo attivo | Concepts linked to active Writing chapter |
| **L-author** | Autore | Subgraph around selected author |
| **L-controversy** | Controversie | Nodes with contradicts edges |
| **L-unread** | Non letti | Sources with zero annotations |

Lens switch preserves camera when possible; otherwise animate to new centroid.

---

## 7. Serendipity paths

Ranked **suggestion strip** below canvas (not chat):

| Suggestion type | Example | Action |
|-----------------|---------|--------|
| Bridge concept | "Collega A e B via riproducibilità" | Pan to path; highlight edges |
| Unread source | "Benjamin non annotato" | Focus source satellite |
| Decision tension | "DEC-012 vs questo concetto" | Focus decision node |
| Chapter gap | "Cap. 3 non cita questo concetto" | Offer Writing handoff |

Suggestions are **deterministic** from graph topology + reading state — AI augmentation
is optional overlay (PX-2 AI panel pattern), never the primary surface.

---

## 8. Writing handoff

### 8.1 Canvas basket

Session-scoped like PX-3 basket (§14.4 v1). Items are Knowledge Object references.

| Action | Result |
|--------|--------|
| Add to basket | From selection or inspector |
| Porta in Scrittura | Navigate to Writing with basket imported to Context |
| Salva vista | Persist camera + lens + selection as named view |
| Termina | Prompt save or discard |

### 8.2 Context integration

Writing ContextBar (PX-2) shows canvas basket count chip. Import does not auto-insert
prose — operator places citations and notes explicitly (KR-6, PP-3).

---

## 9. Saved views

| Field | Persisted |
|-------|-----------|
| name | Operator label |
| focus_slug | Optional |
| camera | x, y, zoom |
| lens_id | Active lens |
| filters | State, relation types |
| selected_ids | Optional multi-select restore |

Home quick action **Riprendi mappa** opens last saved view or active canvas session
(PP-6).

---

## 10. Cross-module navigation

| From canvas | Target | Behavior |
|-------------|--------|----------|
| Double-click concept | `/knowledge/[slug]` | Explain Page |
| Open source | `/sources/[id]` | Source reader |
| Open chapter | `/writing/[chapterId]` | Writing workspace |
| Open graph (bounded) | `/knowledge/graph?focus=slug` | PX-3 navigation graph |
| Command palette | `⌘K` → Concetti | Same as PX-2/PX-3 |

Returning from Explain preserves canvas session in background tab state (PP-6).

---

## 11. Research hub (`/research`)

Entry screen when operator clicks sidebar **Research**:

```text
┌─────────────────────────────────────────────────────────────┐
│  Research                                                    │
├──────────────────────────┬──────────────────────────────────┤
│  Mappa concettuale       │  Esplorazione guidata            │
│  (PX-5 canvas)           │  (PX-3 trail)                    │
│  [ Apri mappa ]          │  [ Inizia trail ]                │
├──────────────────────────┴──────────────────────────────────┤
│  Riprendi: ultima vista · ultimo trail                      │
└─────────────────────────────────────────────────────────────┘
```

Hub replaces current PX-5 stub. Does not implement trail logic — links only.

---

## 12. Interaction rules

| ID | Rule |
|----|------|
| RR-1 | Canvas never edits chapter prose |
| RR-2 | Concept identity is slug from PX-4 store — no duplicate nodes |
| RR-3 | Deprecated concepts hidden by default; toggle in filter rail |
| RR-4 | Canvas state restores on return (PP-6) |
| RR-5 | Hard node limit requires explicit lens/cluster — no silent omission |
| RR-6 | Explain Page remains canonical for concept detail (KR-13) |
| RR-7 | AI suggestions are overlay only — graph structure is deterministic |
| RR-8 | Mobile: read-only message; canvas requires desktop (≥1024px) |

---

## 13. States

| State | UX |
|-------|-----|
| Empty project | Hub → canvas with onboarding: "Importa fonti o crea concetti in Knowledge" |
| Loading | Skeleton canvas + minimap placeholder |
| Over soft limit | Amber banner: "Mapa grande — usa un filtro o raggruppa" |
| Over hard limit | Modal: choose lens or cluster mode |
| Error | Toast + retry; preserve last good viewport |
| No PX-4 data | Hub disables canvas card; links to Knowledge |

---

## 14. Context integration

| Surface | Integration |
|---------|-------------|
| ContextBar | Active chapter lens default when entering from Writing |
| Home | Riprendi mappa + activity feed entry |
| Command palette | "Apri mappa concettuale", "Salva vista corrente" |
| Activity feed | "Mappa: {view name}" |

---

## 15. PX-5 exclusions

| Feature | Owner |
|---------|-------|
| Citation validator | PX-6 |
| Export / print | PX-6 |
| Multi-project switch | PX-6 |
| Real-time collaboration | Out of roadmap v2 |
| Full PDF parse pipeline | PX-3 ingestion scope |
| MB2 Runtime / Program Trace | px-exec |

---

## 16. Qualification acceptance (QWO-PX5-001 draft)

| # | Criterion |
|---|-----------|
| AC-1 | `/research/canvas` renders concept + satellite nodes from PX-4 API |
| AC-2 | Pan/zoom + focus deep link `/research/[conceptId]` works |
| AC-3 | Soft/hard limits enforced with banner/modal (§5.2) |
| AC-4 | Lens filters reframe graph without duplicate nodes |
| AC-5 | Selection → basket → Porta in Scrittura imports Context |
| AC-6 | Saved view restores camera + lens |
| AC-7 | Double-click concept opens Explain; no duplicate concept page |
| AC-8 | `/research` hub links canvas + guided without scope bleed |
| AC-9 | INV-KM-5: canvas blocked if concept CRUD absent (regression guard) |
| AC-10 | `make ci` green; PX-2/PX-3/PX-4 regression preserved |

---

## 17. Governance references

| Artifact | Role |
|----------|------|
| ADR-0036 | IA routes |
| ADR-0037 | Concept-centric model; INV-KM-5 |
| ADR-0038 | Context Engine |
| `px3-knowledge-experience-v2.md` | Guided research §16; graph limits §10 |
| `docs/px4-promotion.md` | PX-4 delivered baseline |
| `thesisos-product-ux-v1.md` | §5.2 Research baseline |

---

## WO-TRACE

```text
PX-4 PROMOTED → AUTHORIZE PX-5 → PX5-EWO-001 (this document)
  → UX freeze → PX5-EWO-* implementation → QWO-PX5-001
```
