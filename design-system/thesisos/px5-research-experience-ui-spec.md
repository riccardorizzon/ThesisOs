# PX-5 — Research Experience UI Specification

> **Status:** DRAFT — UX handoff to Engineering (post Architect sign-off on product spec)  
> **Product source of truth:** [`docs/product/specs/px5-research-experience-v1.md`](../../docs/product/specs/px5-research-experience-v1.md)  
> **Builds on:** [`px3-knowledge-experience-ui-spec.md`](px3-knowledge-experience-ui-spec.md), [`px4`](../../docs/px4-promotion.md) delivered components  
> **Governance:** [`docs/product/UX-ALIGNMENT-REVIEW.md`](../../docs/product/UX-ALIGNMENT-REVIEW.md)  
> **Patterns:** [`product-patterns.md`](product-patterns.md)  
> **Tokens:** [`docs/product/design-system-v1.md`](../../docs/product/design-system-v1.md)

Translates Product Specification v1 only. Does not redefine milestones or introduce
features beyond §2 capabilities.

---

## 0. UX Alignment Review — PASS (draft)

| Check | Result |
|-------|--------|
| Spec citation | `px5-research-experience-v1.md` |
| Capability map PX-5.1…PX-5.6 | Product §2 |
| Milestone boundary | PX-5 only; PX-6 in product §15 |
| IA (ADR-0036) | §3 routes |
| PX-3/PX-4 unchanged | Boundary matrix product §3 |
| RR-1…RR-8 | Product §12 |
| INV-KM-5 | Product §3, §4 |

---

## 1. Design foundations

Inherits frozen tokens. PX-5 adds **canvas-specific layout tokens** only.

| Token | Value | Usage |
|-------|-------|-------|
| `--canvas-bg` | `--color-bg` | Infinite canvas background |
| `--canvas-grid` | `ink-subtle @ 8%` | Optional dot grid |
| `--canvas-node-concept` | `--color-accent` | Concept fill |
| `--canvas-node-source` | `--color-surface` + border | Source satellite |
| `--canvas-node-author` | `--color-surface-muted` | Author chip |
| `--canvas-node-decision` | `--color-warning-subtle` | Decision diamond |
| `--canvas-edge-supports` | `--color-success` | supports edge |
| `--canvas-edge-contradicts` | `--color-warning` | contradicts edge |
| `--canvas-cluster` | `--color-accent-subtle` | Aggregated cluster |

Typography, iconography: inherit PX-3 §1.3–1.4. Add canvas icons:

| Entity | Icon |
|--------|------|
| canvas | `Map` |
| lens | `ScanEye` |
| cluster | `Layers` |
| saved view | `Bookmark` |

---

## 2. Information architecture

| Route | Screen | Component root |
|-------|--------|----------------|
| `/research` | Research hub | `ResearchHubPage` |
| `/research/canvas` | Spatial canvas | `ResearchCanvasPage` |
| `/research/canvas?view={id}` | Saved view restore | same |
| `/research/[conceptId]` | Canvas focus redirect | redirect → `?focus=` |
| `/research/guided` | Guided trail (PX-3) | `ResearchGuidedPage` (stub link until PX-3.10 impl) |

Sidebar label remains **Research** (ADR-0036). Breadcrumb: `Research › Mappa`.

---

## 3. Research hub (`ResearchHubPage`)

### 3.1 Layout

```text
┌─ AppShell ────────────────────────────────────────────────────┐
│  Research                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │  Mappa concettuale       │  │  Esplorazione guidata   │   │
│  │  Icon: Map               │  │  Icon: Route            │   │
│  │  Spatial discovery       │  │  Trail + basket         │   │
│  │  [ Apri mappa → ]        │  │  [ Inizia trail → ]     │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
│  Riprendi                                                     │
│  · {last view name} — canvas                                  │
│  · {last trail name} — guided                                 │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 States

| State | UI |
|-------|-----|
| No concepts | Canvas card disabled; helper links to `/knowledge` |
| Has saved views | "Riprendi" list (max 3 recent) |
| Loading | Card skeletons |

---

## 4. Canvas shell (`ResearchCanvasPage`)

### 4.1 Layout regions

```text
┌─ Header bar ─────────────────────────────────────────────────┐
│  ← Research   Lens ▾   Filters   [ Salva vista ]  [ Basket N ]│
├──────────┬───────────────────────────────────────┬───────────┤
│  Lens    │                                       │ Inspector │
│  rail    │         CANVAS (pan/zoom)             │  rail     │
│  240px   │         + minimap (bottom-right)      │  320px    │
│          │                                       │  (PP-1)   │
├──────────┴───────────────────────────────────────┴───────────┤
│  Serendipity strip (suggestion cards, horizontal scroll)      │
├──────────────────────────────────────────────────────────────┤
│  [ Porta in Scrittura ]  [ Aggiungi al basket ]  selection  │
└──────────────────────────────────────────────────────────────┘
```

| Region | Width | Collapse |
|--------|-------|----------|
| Lens rail | `--outline-width` (240px) | `⌘[` |
| Inspector rail | `--rail-width` (320px) | `⌘\` (PP-1) |
| Canvas | flex 1 | — |

### 4.2 Header bar

| Control | Behavior |
|---------|----------|
| Back | → `/research` hub |
| Lens dropdown | L-all, L-gap, L-chapter, … (product §6) |
| Filters | Popover: stato, relation type, core only, hide deprecated |
| Salva vista | Modal: name + optional description |
| Basket badge | Opens basket drawer |

---

## 5. Canvas interaction

### 5.1 Node rendering

| Kind | Shape | Size |
|------|-------|------|
| concept | Circle | 48px default; 64px if core |
| source | Rounded rect | 56×40 |
| author | Pill | auto width |
| decision | Rotated square | 36px |
| chapter | Hex outline | 40px, muted |

Lifecycle badge: bottom-right chip (PP-5). Hover: elevation + full title tooltip.

### 5.2 Edges

| Type | Stroke | Arrow |
|------|--------|-------|
| supports | 2px success | bidirectional optional |
| contradicts | 2px warning dashed | — |
| extends | 2px accent | directed |
| related | 1px ink-subtle | — |
| concept-source | 1px dashed ink-muted | — |

Edge labels hidden until zoom ≥ 100% or hover.

### 5.3 Gestures

| Input | Action |
|-------|--------|
| Drag background | Pan |
| Scroll / pinch | Zoom (clamp 25–400%) |
| Click node | Select + inspector |
| Double-click concept | Navigate Explain |
| `⌘`+click | Multi-select toggle |
| Shift+drag | Marquee select |
| `Space`+drag | Temporary pan mode |

### 5.4 Minimap

64×64px fixed bottom-right; `--color-surface` frame; viewport rectangle draggable.

### 5.5 Cluster node

When aggregation active: stacked card icon + count label. Click → expand cluster modal
with list fallback (PP-8 tone).

---

## 6. Inspector rail (canvas context)

Reuses PP-1 tab pattern. Tabs for selected node:

| Tab | Content |
|-----|---------|
| Dettaglio | Title, lifecycle, confidence, summary snippet |
| Collegamenti | Linked sources, concepts, chapters (deep links) |
| Azioni | Apri Explain · Apri fonte · Aggiungi al basket |

Multi-select: show count + batch "Aggiungi al basket".

---

## 7. Lens rail

Vertical list of lens cards with icon + label + short description. Active lens:
accent left border 3px. Switching lens shows loading shimmer ≤300ms then animate pan.

---

## 8. Serendipity strip

Horizontal scroll row of suggestion cards (max 5 visible):

```text
┌────────────────┐ ┌────────────────┐
│ Ponte concetti │ │ Fonte non letta│
│ A ↔ B          │ │ Benjamin       │
│ [ Mostra ]     │ │ [ Apri ]       │
└────────────────┘ └────────────────┘
```

Card click: pan + pulse highlight on target nodes (2s).

---

## 9. Basket drawer

Slide-over from right (above inspector when open). Lists Knowledge Object refs with
remove per row. Footer: **Porta in Scrittura** (primary), **Salva come trail** (secondary, links to guided — future).

---

## 10. Limits UI (distinct from PX-3 graph)

| Threshold | UI (product §5.2) |
|-----------|-------------------|
| >80 nodes initial | Load progressively with spinner on minimap |
| >150 soft | Amber banner below header: "Mapa grande — applica un filtro" |
| >300 hard | Modal blocking: choose lens OR cluster mode — no dismiss without choice |

**No List view fallback** on canvas — use cluster modal instead (PP-10 boundary).

---

## 11. Saved view modal

| Field | Control |
|-------|---------|
| Nome | Text input, required, max 64 chars |
| Descrizione | Optional textarea |
| Includi selezione | Checkbox, default off |

Success toast: "Vista salvata". Home Riprendi picks up latest.

---

## 12. Empty and error states

| State | Copy (IT) |
|-------|-----------|
| Empty canvas | "Nessun concetto ancora. Crea concetti in Knowledge o importa fonti." CTA → `/knowledge` |
| Load error | "Impossibile caricare la mappa. Riprova." |
| Desktop required | "La mappa richiede desktop (≥1024px)." |
| Deprecated hidden | Filter chip: "Deprecati nascosti" |

---

## 13. Keyboard

| Key | Action |
|-----|--------|
| `Esc` | Clear selection; close drawer |
| `⌘S` | Salva vista |
| `⌘B` | Toggle basket |
| `⌘\\` | Toggle inspector |
| `+` / `-` | Zoom |
| `0` | Reset zoom to 100% |
| `F` | Fit selection in viewport |
| `⌘K` | Command palette (PP-7) |

---

## 14. Responsive

| Breakpoint | Layout |
|------------|--------|
| ≥1280px | Full shell: lens + canvas + inspector |
| 1024–1279px | Inspector overlay drawer; lens rail collapsible |
| <1024px | Full-page message: desktop required (RR-8) |

---

## 15. Component inventory (implementation waves)

| Component | Wave hint |
|-----------|-----------|
| `ResearchHubPage` | Wave A |
| `ResearchCanvasPage` | Wave B |
| `CanvasViewport` | Wave B |
| `CanvasNodeLayer` | Wave B |
| `CanvasEdgeLayer` | Wave B |
| `CanvasMinimap` | Wave B |
| `ResearchLensRail` | Wave C |
| `SerendipityStrip` | Wave C |
| `ResearchBasketDrawer` | Wave D |
| `SavedViewModal` | Wave D |

Engineering splits waves in `.asep/programs/px5-parallel.yaml` (future — post spec ratification).

---

## 16. Milestone exclusions (UI)

| Excluded | Reference |
|----------|-----------|
| Citation validator UI | PX-6 |
| Export dialog | PX-6 |
| Multi-project switcher | PX-6 |
| MB2 Program Trace | px-exec |

---

## WO-TRACE

```text
px5-research-experience-v1.md → this UI spec → PX5 implementation EWOs
```
