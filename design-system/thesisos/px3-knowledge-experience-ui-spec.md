# PX-3 — Knowledge Experience UI Specification

> **Status:** FROZEN — UX handoff to Engineering (post PX-2 qualification)  
> **Product source of truth:** [`docs/product/specs/px3-knowledge-experience-v2.md`](../../docs/product/specs/px3-knowledge-experience-v2.md)  
> **Builds on:** [`px2-research-workspace-ui-spec.md`](px2-research-workspace-ui-spec.md) (frozen)  
> **Governance:** [`docs/product/UX-ALIGNMENT-REVIEW.md`](../../docs/product/UX-ALIGNMENT-REVIEW.md)  
> **Patterns:** [`product-patterns.md`](product-patterns.md)  
> **Tokens:** [`docs/product/design-system-v1.md`](../../docs/product/design-system-v1.md)

Complete UI specification for PX-3. Translates Product Specification v2 only. Does not redefine milestones, capabilities, or roadmap. Does not introduce product features.

---

## 0. UX Alignment Review — PASS

| Check | Result |
|-------|--------|
| Spec citation | `px3-knowledge-experience-v2.md` |
| Capability map PX-3.1…PX-3.10 | §2 |
| Milestone boundary | PX-3 only; PX-5/PX-6 in §24 |
| IA frozen (ADR-0036) | §3 |
| PX-2 unchanged | Explicit throughout |
| KR-1…KR-14 | §10 |
| QWO trace | §23 |

---

## 1. Design foundations

### 1.1 Visual system

Inherits frozen tokens. PX-3 adds **no new color tokens**.

| Role | Token | PX-3 usage |
|------|-------|------------|
| Page | `--color-bg` | App background |
| Surface | `--color-surface` | Cards, reader canvas, Explain regions |
| Muted surface | `--color-surface-muted` | Inspector rail, filter rail |
| Ink | `--color-ink` / `ink-muted` / `ink-subtle` | Body, meta, labels |
| Accent | `--color-accent` / `accent-subtle` | Core concepts, links, focus, active tab |
| Success | `--color-success` | `supports` edges, Validated promotion |
| Warning | `--color-warning` | `contradicts`, Candidate watermark, low-confidence search |
| Danger | `--color-danger` | Errors, Deprecated banner, Esclusa callout |

### 1.2 Layout tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--sidebar-width` | 13rem | AppShell nav |
| `--rail-width` | 20rem (320px) | Inspector rail (PP-1) |
| `--outline-width` | 15rem (240px) | Explorer / Sources filter rail |
| `--row-height-dense` | 2.25rem (36px) | List rows |
| `--content-max-width` | 72rem | Explorer max content |

### 1.3 Typography

| Role | Scale | Usage |
|------|-------|-------|
| Display | `--text-2xl` semibold | Explain H1, Research session title |
| Title | `--text-lg` semibold | Region headings, modal titles |
| Body | `--text-base` relaxed | Definitions, reader prose (max 70ch) |
| UI | `--text-sm` medium | Buttons, tabs, filters, table cells |
| Meta | `--text-xs` medium | Badges, counts, timestamps |
| Mono | `--text-xs` | DEC-IDs, locators, citation strings |

### 1.4 Iconography

Lucide, stroke 1.5px, 16px inline / 20px headers. No emojis.

| Entity | Icon |
|--------|------|
| concept | `CircleDot` |
| source | `BookOpen` |
| author | `User` |
| citation | `Quote` |
| annotation | `Highlighter` |
| passage | `TextSelect` |
| graph | `GitBranch` |

---

## 2. Screen hierarchy

```text
AppShell (ADR-0036 — unchanged)
├── Global chrome
│   ├── Sidebar: Home · Research · Writing · Sources · Knowledge · Settings
│   ├── Breadcrumbs
│   ├── ContextBar (Knowledge / Sources / Research surfaces)
│   └── Command palette (⌘K) + session chip (PX-2)
│
├── PX-3 — Knowledge module (primary)
│   ├── KnowledgeExplorer          /knowledge
│   ├── ExplainPage                /knowledge/[conceptSlug]     ← signature screen
│   ├── KnowledgeGraph             /knowledge/graph
│   ├── AuthorIndex                /knowledge/authors
│   ├── AuthorPage                 /knowledge/authors/[authorSlug]
│   ├── AuthorCompare              (modal/split from Author page)
│   └── CitationIndex              /knowledge/citations
│
├── PX-3 — Sources (enriched, not separate milestone)
│   ├── SourcesList                /sources
│   ├── SourceReader               /sources/[sourceId]
│   └── ImportModal                /sources/import (replaces /documents/upload)
│
├── PX-3 — Research workflow (guided, not PX-5 canvas)
│   ├── ResearchEntry              /research
│   └── ResearchSession            /research?trail=[id]
│
├── PX-2 — Writing (frozen; receives deep links only)
├── PX-2 — Home (frozen; + Riprendi ricerca, knowledge activity)
└── Overlays (shared)
    ├── UnifiedSearchResults       ⌘K / inline search
    ├── CitationBuilder            modal
    ├── ImportReview               modal stepped
    ├── ProposalDetail             modal (PX-2 inbox)
    ├── AiLateralPanel             320px overlay (PP-1)
    └── CoachMark                  contextual onboarding
```

### 2.1 Module relationship (visual)

```text
                    ┌─────────────┐
                    │  Knowledge  │  ontological lens
                    │  Explorer   │
                    └──────┬──────┘
                           │ same Knowledge Objects
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Sources      Writing      Decisions
         (evidence)   (argument)   (constraints)
              │            ▲
              └────────────┘
                   citations · annotations · concepts
```

---

## 3. Navigation

### 3.1 Primary navigation (frozen)

Sidebar per ADR-0036. English labels. PX-3 nav badges:

| Item | Badge |
|------|-------|
| Knowledge | Pending concept proposals (if > 0) |
| Sources | — |
| Research | Active trail indicator (dot) if session open |

### 3.2 In-module navigation

| Mechanism | Behavior |
|-----------|----------|
| **Concept chip** | Any surface → Explain Page |
| **Author link** | Any author name → Author page (KR-8) |
| **Source row** | → Source reader; optional `?passage=` locator |
| **Chapter row** | → `/writing/[id]?section=` |
| **Trail step** | Research session breadcrumb → entity page |
| **Graph node** | Click preview; double-click Explain Page |
| **Back ←** | Returns to prior module view with filters restored |
| **Browser back** | Preserves exploration trail |

### 3.3 Breadcrumbs

| Module | Pattern |
|--------|---------|
| Knowledge | `Knowledge` |
| Explain | `Knowledge / [Concept title]` |
| Graph | `Knowledge / Graph` |
| Authors | `Knowledge / Autori / [Name]` |
| Sources | `Sources / [Short title]` |
| Research | `Research / [Trail name \| Nuova]` |

Enriched semantic path when drilled from Explain:

`Knowledge / Aura / Fonti / Benjamin 1936`

### 3.4 Deep-link URL state

```text
/knowledge
/knowledge/[conceptSlug]
/knowledge/graph?focus=[slug]&depth=1
/knowledge/authors/[authorSlug]
/knowledge/citations?chapter=[id]
/sources/[sourceId]?passage=[locator]
/sources?status=…&concept=…&q=…
/research?trail=[trailId]
```

Writing return URLs preserved on cross-module links (product §19).

### 3.5 Command palette groups (⌘K)

| Group | Examples |
|-------|----------|
| Vai a… | Knowledge, Graph, Authors, Sources |
| Concetti | Jump to concept by name |
| Autori | Jump to author |
| Cerca | Unified search query passthrough |
| Azioni | Cita da…, Estrai concetti, Mostra nel grafo, Porta in Scrittura |

---

## 4. Knowledge Object UI envelope (PP-4)

Every entity page renders the shared envelope (product §3.1).

### 4.1 Card / header anatomy

```text
┌────────────────────────────────────────────────────────┐
│ [type icon]  TITLE                          [overflow]│
│ subtitle · summary snippet (1–3 lines max)              │
│ [lifecycle] [core?] [confidence] [provenance]         │
│ N fonti · N capitoli · N concetti · N citazioni       │
└────────────────────────────────────────────────────────┘
```

### 4.2 Lifecycle badges (PP-5)

| State | Label IT | Card | Graph | Search |
|-------|----------|------|-------|--------|
| Candidate | Candidato | Dashed border | Hidden default | Section "Candidati" |
| Validated | Validato | Normal | Visible if core/filter | Included |
| Linked | Collegato | Link count chips | Visible | Rank boost |
| Referenced | Citato in tesi | Emphasis badge | +20% node | Rank boost |
| Deprecated | Deprecato | Muted; filter off | Hidden | Section "Deprecati" only |

### 4.3 Corpus status (sources)

Maps per product §4.3: Candidata→Candidate, Approvata→Validated+, Esclusa→Deprecated.

### 4.4 Confidence chip

`Alta · Media · Bassa · Non valutata` — affects search rank display order and graph node size only.

### 4.5 Proposal affordance

`proposal_state = In attesa` + Candidate: dashed UI + inbox link. Approved/Rejected per product §4.5.

---

## 5. Layouts — per screen

### 5.1 Knowledge Explorer (`/knowledge`) — PX-3.2

```text
┌──────────┬──────────────────────────────────────────────────────────────┐
│ Sidebar  │ Breadcrumbs · ⌘K                                             │
│          ├──────────────────────────────────────────────────────────────┤
│          │ ContextBar (optional — when scoped)                            │
│          ├──────────────────────────────────────────────────────────────┤
│          │ [ Unified search ──────────────────────── ] [Grafo][Autori][+]│
│          ├──────────────┬─────────────────────────────────────────────────┤
│          │ Filter rail  │ Featured concept (thesis anchor)              │
│          │ 240px        │ Segmented: Concetti │ Lista │ Recenti │ Nucleo  │
│          │              │ Card grid (3-col @1440) or dense table          │
│          └──────────────┴─────────────────────────────────────────────────┘
```

**Featured concept:** Theory Map anchor; links to Explain Page.

**Filters:** Stato knowledge · Core · Confidenza · Capitolo · Fonte · Relazione · Decisione · toggle "Mostra candidati" (product §8.2).

**Concept card:**

```text
┌──────────────────────────────┐
│ [Core] Aura benjaminiana     │
│ Validato · Collegato         │
│ Benjamin — riproducibilità   │
│ 4 fonti · 2 capitoli         │
│ Confidenza: Alta             │
│ [ Apri ]  [ Grafo ]          │
└──────────────────────────────┘
```

### 5.2 Explain Page (`/knowledge/[conceptSlug]`) — PX-3.3

**Signature screen.** Regions A–L per product §9. KR-13: canonical concept view.

```text
┌─────────────────────────────────────────────────────────────────┐
│ A  HEADER (sticky → compact on scroll)                          │
├─────────────────────────────────────────────────────────────────┤
│ B  DEFINITION (~120 words; Mostra tutto)                        │
├──────────────────────────────┬──────────────────────────────────┤
│ C  ROLE IN THESIS            │ D  STATUS STRIP (click → scroll) │
├──────────────────────────────┴──────────────────────────────────┤
│ E  RELATED CONCEPTS — tabs: Sostiene│Contraddice│Estende│Corr. │
├─────────────────────────────────────────────────────────────────┤
│ F  AUTHORS (hidden if empty)                                    │
├─────────────────────────────────────────────────────────────────┤
│ G  SOURCES (evidence, ranked)                                   │
├─────────────────────────────────────────────────────────────────┤
│ H  CHAPTERS                                                     │
├─────────────────────────────────────────────────────────────────┤
│ I  DECISIONS (DecisionCard — PX-2 visual pattern)               │
├─────────────────────────────────────────────────────────────────┤
│ J  CITATIONS                                                    │
├─────────────────────────────────────────────────────────────────┤
│ K  LOCAL GRAPH (max 12 nodes; link to full graph)               │
├─────────────────────────────────────────────────────────────────┤
│ L  ACTION BAR (sticky footer)                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Region L actions:**

| Label | Variant | Enabled |
|-------|---------|---------|
| Vai a Scrittura | primary | always |
| Spiega (AI) | secondary | Validated+ |
| Trova fonti | secondary | Validated+ |
| Controversie (AI) | secondary | has contradicts |
| Mostra nel grafo | secondary | Validated+ |
| Collega fonte | tertiary | always |

**Per-region empty states:** per product §9.3–9.12 (CTA or hidden section).

### 5.3 Knowledge Graph (`/knowledge/graph`) — PX-3.4

Navigation graph — **not** PX-5 canvas (PP-10).

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Toolbar: L0–L4 expansion │ filters │ grouping │ node count │ [List view]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│              Canvas — concept nodes only, max 15 default                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ Preview panel 320px — selected node + Apri + Espandi vicini             │
└─────────────────────────────────────────────────────────────────────────┘
```

**Limits:** 15 default · 50 soft (banner) · 100 hard (List view mandatory).

**Grouping:** Libero · Per capitolo · Per autore · Gerarchico · Radiale.

**Node encoding:** Core=accent fill; lifecycle size deltas per product §10.6; Candidate=dashed.

**Edges:** supports (success) · contradicts (warning, dashed) · extends (accent) · related (muted, dotted). Labels on hover only.

### 5.4 Sources list (`/sources`)

```text
┌──────────────┬──────────────────────────────────────────────────────────┐
│ Filter rail  │ Unified search + view toggle (grid / list)               │
│ 240px        │ Source cards with lifecycle + corpus badges              │
│ Stato        │                                                          │
│ Tipo         │                                                          │
│ Concetti     │                                                          │
│ Capitoli     │                                                          │
└──────────────┴──────────────────────────────────────────────────────────┘
```

Sticky **Torna a Scrittura** chip when `?chapter=` in URL (PX-2 carry-over).

### 5.5 Source reader (`/sources/[sourceId]`) — PX-3.5, PX-3.6, PX-3.7

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ A  Reader header: ← Sources · title · badges · Prev/Next · Focus · ⌘\ │
├──────────────────────────────┬──────────────────────────────────────────┤
│ B  READING CANVAS            │ C  INSPECTOR RAIL 320px                  │
│    max 65ch                  │    Tab bar (underline active)          │
│    concept overlay toggle    │    Meta │ Note │ Estratti │ Relazioni   │
│    scroll progress + locator │    Citazioni │ Concetti │ Capitoli     │
├──────────────────────────────┴──────────────────────────────────────────┤
│ D  Action bar: Cita · Collega concetto · Collega capitolo · AI          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Reading modes:**

| Mode | Layout |
|------|--------|
| Standard | B + C split (default) |
| Focus | B full width; C on `⌘\` or hover |
| Split | Explain source link: reader + Explain side-by-side |
| Peek | PX-2 Writing peek unchanged; annotations read-only |

**Passage toolbar (on select):** `Evidenzia · Nota · Cita · Collega a concetto · Copia`

### 5.6 Author index & page — PX-3.9

**Index** (`/knowledge/authors`): dense table — Author · Fonti · Top concept chips · Capitoli.

**Author page:**

```text
┌─────────────────────────────────────────────────────────────────┐
│ ← Autori · Walter Benjamin · badges                             │
├─────────────────────────────────────────────────────────────────┤
│ Bio note (optional, proposal edit)                              │
├─────────────────────────────────────────────────────────────────┤
│ FONTI │ CONCETTI │ CAPITOLI │ RETE (mini-graph)                  │
├─────────────────────────────────────────────────────────────────┤
│ [ Confronta autore… ]  [ Cerca in autore ]                      │
└─────────────────────────────────────────────────────────────────┘
```

**Compare:** split view; shared concepts highlighted (read-only).

### 5.7 Citation index — PX-3.8

Route: `/knowledge/citations` or Sources → Citazioni tab.

| Column | Content |
|--------|---------|
| Citation | Formatted string + locator |
| Source | Link |
| Concept | Chip |
| Chapter | Link |
| Status | Valida · Da verificare |

**Citation builder modal (stepped):**

```text
1. Fonte → 2. Passaggio → 3. Concetto (optional) → 4. Capitolo → 5. Anteprima → Inserisci
```

### 5.8 Research workflow — PX-3.10

**Entry** (`/research`):

```text
Da dove vuoi iniziare?
○ Da un concetto  ○ Da una domanda  ○ Da una fonte
[ seed picker / unified search ]
[ Inizia ricerca ]
```

**Session:**

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Title + [ Termina ]                                                     │
│ Trail: Entity A → Entity B → Entity C → …                               │
├──────────────┬──────────────────────────────────────────────────────────┤
│ Basket (N)   │ Current entity view + suggested next steps (ranked cards) │
│ · sources    │ · Concetti correlati · Fonti collegate · Passaggi simili│
│ · notes      │ · Conflitto con DEC-… (if applicable)                   │
│ · annot.     │                                                          │
├──────────────┴──────────────────────────────────────────────────────────┤
│ [ Porta in Scrittura ]  [ Salva trail ]  [ Grafo locale ]               │
└─────────────────────────────────────────────────────────────────────────┘
```

Research **never** edits prose (KR-6). Handoff opens Writing chapter picker.

### 5.9 Import modal — product §19

Stepped single modal:

```text
1. Drop zone (PDF · EPUB · DOCX)
2. Progress: Caricamento → Analisi
3. Review: metadata (editable) + concept checkboxes + Candidata default
4. [ Annulla ]  [ Approva import ] → proposal inbox
```

States: Caricamento · Analisi · Proposta pronta · Indicizzata.

---

## 6. Component hierarchy

```text
AppShell
├── GlobalChrome
│   ├── SidebarNav
│   ├── Breadcrumbs
│   ├── ContextBar                    (PX-2 + concept count delta)
│   ├── SessionChip                   (PX-2)
│   └── CommandPaletteTrigger
│
├── KnowledgeModule
│   ├── KnowledgeExplorer
│   │   ├── UnifiedSearchBar
│   │   ├── ExplorerFilterRail
│   │   ├── FeaturedConceptCard
│   │   ├── ExplorerModeToggle
│   │   └── KnowledgeObjectCard (concept)
│   │
│   ├── ExplainPage
│   │   ├── ExplainHeader             (region A)
│   │   ├── DefinitionBlock           (B)
│   │   ├── RoleInThesisBlock         (C)
│   │   ├── StatusStrip               (D)
│   │   ├── RelatedConceptsTabs       (E)
│   │   ├── AuthorListSection         (F)
│   │   ├── EvidenceSourceList        (G)
│   │   ├── ChapterUsageList          (H)
│   │   ├── DecisionCardList          (I)
│   │   ├── CitationList              (J)
│   │   ├── LocalGraphEmbed           (K)
│   │   └── ExplainActionBar          (L)
│   │
│   ├── KnowledgeGraphView
│   │   ├── GraphToolbar
│   │   ├── GraphCanvas
│   │   ├── GraphPreviewPanel
│   │   └── GraphListView             (fallback)
│   │
│   ├── AuthorIndex
│   ├── AuthorPage
│   ├── AuthorCompareView
│   └── CitationIndex
│
├── SourcesModule (enriched)
│   ├── SourcesList
│   │   ├── SourcesFilterRail
│   │   └── SourceCard
│   ├── SourceReader
│   │   ├── ReaderHeader
│   │   ├── ReadingCanvas
│   │   ├── PassageToolbar
│   │   ├── ReaderActionBar
│   │   └── SourceInspector           (see §7)
│   └── ImportModal
│
├── ResearchModule
│   ├── ResearchEntry
│   ├── ResearchSession
│   │   ├── TrailBreadcrumb
│   │   ├── ResearchBasket
│   │   ├── SuggestedNextCards
│   │   └── ResearchActionBar
│   └── TerminateResearchDialog
│
└── Shared
    ├── UnifiedSearch
    │   ├── SearchInput
    │   ├── SearchResultGroup
    │   └── SearchResultRow           (per type anatomy §11.5 product)
    ├── CitationBuilder
    ├── AiLateralPanel                (PP-1 overlay)
    ├── ProposalModal                 (PX-2)
    ├── LifecycleBadge
    ├── ConfidenceChip
    ├── ConceptChip
    ├── AuthorChip
    ├── SourceChip
    ├── ChapterChip
    ├── DecisionCard                  (PX-2 pattern)
    ├── EmptyState
    ├── SkeletonRegion
    ├── ErrorBanner
    └── CoachMark
```

---

## 7. Inspector behavior (PP-1)

Unified 320px (`--rail-width`) inspector across Source reader, Graph preview, and AI lateral overlay.

### 7.1 Anatomy

```text
┌─ Tab │ Tab │ Tab │ Tab ──────────────── ⌘\ ─┐
├──────────────────────────────────────────────┤
│ Tab content (scrollable)                     │
│                                              │
├──────────────────────────────────────────────┤
│ Optional footer actions                      │
└──────────────────────────────────────────────┘
```

| Property | Rule |
|----------|------|
| Width | 320px fixed desktop |
| Background | `--color-surface-muted` |
| Tab bar height | 40px |
| Active tab | 2px accent underline |
| Collapse | `⌘\` — canvas expands |
| Persist | Active tab per source/session |

### 7.2 Source reader tabs

| Tab | Content | Scroll sync |
|-----|---------|-------------|
| **Meta** | Envelope + approval banner + bibliography_status | — |
| **Note** | Annotation list + composer | Bidirectional with canvas |
| **Estratti** | Curated passages | Jump to locator |
| **Relazioni** | Source↔source manual links | — |
| **Citazioni** | Citations from this source | Jump |
| **Concetti** | Linked + suggested concepts | → Explain |
| **Capitoli** | Linked chapters | → Writing |

### 7.3 Graph preview panel

Selected node only: title · lifecycle · one-line definition · counts · [ Apri ] [ Espandi vicini ].

### 7.4 AI lateral overlay

Opens from Explain header, Source action bar, Research session. **Does not replace** parent view — 320px slides over right edge; parent remains visible at ≥1280px. Dismiss: `Esc` or close control. Streams with cancel (PX-2 pattern).

### 7.5 Annotation panel (Note tab) — PX-3.7

```text
┌─ Note (N) ──────────────────────┐
│ [ Cerca nelle note… ]           │
│ Filtra: Tutte · per colore · …  │
├─────────────────────────────────┤
│ ▌Highlight quote                │
│   Nota testo…                   │
│   [ Vai al passaggio ]          │
└─────────────────────────────────┘
```

| Interaction | Behavior |
|-------------|----------|
| Click row | Scroll canvas to locator + brief highlight flash |
| Hover row | Subtle `bg-surface-muted` |
| Create | Selection toolbar → composer inline in tab |
| Delete | Confirm dialog |
| Bulk approve | Proposed annotations batch from import |

Highlight colors: 5 presets — left border 3px; not semantic status colors.

---

## 8. Interaction rules

Product KR-1…KR-14. UI must enforce visually.

| ID | UI enforcement |
|----|----------------|
| KR-1 | Concepts primary in nav chips; sources subordinate in evidence lists |
| KR-2 | Merge via overflow only; alias redirect — no duplicate Explain routes |
| KR-3 | Annotation appears in source Note tab + Explain evidence + chapter footer |
| KR-4 | Esclusa excluded from default search; separate collapsible section |
| KR-5 | Graph L0–L4 explicit expand; confirm thresholds |
| KR-6 | Research has no editor; Porta in Scrittura only handoff |
| KR-7 | All mutations show proposal preview — no optimistic permanent UI |
| KR-8 | All author names are link styled + keyboard focusable |
| KR-9 | Citation rows link source + passage + concept + chapter |
| KR-10 | Focus mode (`F`) on every long source |
| KR-11 | Lifecycle badge on every Knowledge Object card/header |
| KR-12 | Graph List view at 100 nodes — no canvas-only trap |
| KR-13 | No concept detail outside Explain Page |
| KR-14 | Deprecated hidden default in Explorer, graph, search |

### 8.1 Selection & hover

- Hover: `transition-colors duration-200` only — no layout shift
- Click targets ≥ 44px on chrome; 36px dense rows with horizontal padding
- `cursor-pointer` on all navigable cards, chips, rows

### 8.2 Proposal flows

| Type | Label IT |
|------|----------|
| concept_create | Nuovo concetto |
| concept_merge | Unione concetti |
| concept_link | Collegamento concetto–fonte |
| annotation | Annotazione |
| source_import | Importazione fonte |
| source_relation | Relazione tra fonti |
| author_merge | Unione autori |

Inherited PX-2 proposal types unchanged.

### 8.3 Automatic lifecycle promotion (display only)

Validated → Linked → Referenced: badge updates on link/cite events. **No manual toggle** in UI.

---

## 9. Keyboard behavior

Inherits PX-2 global shortcuts where not conflicting. Active only when Knowledge workspace focused.

### 9.1 Global

| Shortcut | Action |
|----------|--------|
| `⌘K` | Command palette / unified search |
| `⌘⇧K` | Focus Knowledge semantic search |
| `G` `K` | Go Knowledge Explorer |
| `G` `G` | Go Graph |
| `G` `A` | Go Authors |
| `G` `S` | Go Sources |
| `G` `H` | Go Home |
| `Esc` | Close overlay / modal / deselect graph / exit focus mode |

### 9.2 Explorer & search

| Shortcut | Action |
|----------|--------|
| `⌘F` | Focus search (module-local) |
| `J` / `K` | Next / previous search result |
| `/` | Focus filter search in rail |

### 9.3 Explain Page

| Shortcut | Action |
|----------|--------|
| `Esc` | Back to Explorer |
| `G` | Scroll to Region K (graph) |
| `S` | Scroll to Region G (sources) |
| `C` | Scroll to Region H (chapters) |
| `⌘⇧S` | Spiega (AI) lateral |

### 9.4 Source reader

| Shortcut | Action |
|----------|--------|
| `F` | Toggle Focus mode |
| `⌘\` | Toggle inspector rail |
| `⌘⇧A` | Jump to Note tab |
| `⌘⇧L` | Link selection to concept |
| `⌘⇧C` | Cite (PX-2) |
| `[` / `]` | Prev / next source in list |
| `⌘Enter` | Confirm annotation or citation builder step |

### 9.5 Graph

| Shortcut | Action |
|----------|--------|
| `⌘F` | Graph search highlight |
| `Shift+click` | Multi-select (max 3) |
| `Esc` | Deselect / exit focus mode |
| `+` / `-` | Zoom in / out |

### 9.6 Research session

| Shortcut | Action |
|----------|--------|
| `⌘Enter` | Accept suggested next step |
| `Backspace` | Remove last trail step (confirm) |

All shortcuts listed in command palette discoverability.

---

## 10. Responsive behavior

Primary targets: **1440×900**, **1920×1080**.

### 10.1 Breakpoint matrix

| Breakpoint | Explorer | Explain | Graph | Source reader | Research |
|------------|----------|---------|-------|---------------|----------|
| ≥1280px | Filter rail + grid | All regions A–L; K inline | Canvas + preview | Split + inspector | Basket rail + entity |
| 1024–1279px | Filter drawer | K below fold | Preview overlay | Inspector overlay | Basket collapsible |
| 768–1023px | List default | Stacked regions | List view default | Focus default | Trail only |
| <768px | List read-only | Definition + links | "Usa desktop per grafo" | Read-only banner | Entry only |

### 10.2 Graph interaction floor

Interactive canvas requires ≥1024px. Below: List view of same data.

### 10.3 Explain Page (product §9.15)

| Breakpoint | Change |
|------------|--------|
| ≥1280px | Full |
| 1024–1279px | Graph below fold |
| 768–1023px | Graph → link only |
| <768px | Definition + links; desktop banner |

### 10.4 Inspector collapse

Below 1280px: inspector defaults closed; `⌘\` opens as overlay drawer with backdrop `z-50`.

---

## 11. Accessibility

### 11.1 Contrast & focus

- Body text ≥ 4.5:1 on surfaces
- UI components ≥ 3:1
- `focus-visible:outline-2 outline-offset-2 outline-accent` on all interactives
- Never color-only state: lifecycle = badge text + icon

### 11.2 Landmarks & labels

| Region | Landmark |
|--------|----------|
| Explorer | `main` |
| Explain regions | `section` + `aria-labelledby` |
| Inspector | `aside` + `aria-label` |
| Graph canvas | `role="img"` + `aria-label="Grafo concetti"` |
| Graph List view | `table` — primary a11y path for graph |

### 11.3 Keyboard & screen reader

- Graph List view mandatory at hard limit (KR-12)
- Tab order: header → content → action bar → inspector
- `aria-live="polite"`: search result counts, save confirmation, proposal queue
- `aria-current="page"` on Explorer selected concept
- Author/concept links: announce lifecycle in sr-only suffix

### 11.4 Reduced motion

`prefers-reduced-motion: reduce`:
- Graph layout: instant positioning
- Explain skeleton: opacity only, no stagger
- Passage highlight flash: skipped
- Modal: opacity fade ≤100ms only

### 11.5 Touch

Chrome targets ≥44px. Dense lists 36px row + 8px vertical padding.

---

## 12. Empty states

Italian copy; inviting tone; Lucide icon 20px `text-ink-subtle`. Per product §21 + region specs.

| Surface | Message | CTA |
|---------|---------|-----|
| Explorer / no concepts | Nessun concetto — importa fonti o approva estrazioni | Importa |
| Explorer / filter empty | Nessun concetto con questi filtri | Reset filtri |
| Graph / empty | Grafo vuoto — aggiungi concetti validati | Explorer |
| Graph / all filtered | Nessun nodo corrisponde ai filtri | Reset filtri |
| Author index | Nessun autore — aggiungi fonti | Importa |
| Author page / no sources | Nessuna fonte per questo autore | Cerca nel corpus |
| Citation index | Nessuna citazione | Vai a Scrittura |
| Source / no annotations | Nessuna annotazione — seleziona un passaggio | — |
| Source / no concepts | Nessun concetto collegato | Collega concetto |
| Explain / no relations (E) | Nessuna relazione approvata | Collega concetto |
| Explain / no sources (G) | Nessuna fonte collegata | Collega fonte · Cerca nel corpus |
| Explain / no chapters (H) | Non ancora usato in un capitolo | Vai a Scrittura |
| Explain / no citations (J) | Nessuna citazione | Cita da fonte |
| Explain / Candidate | Concetto in attesa di approvazione | Approva |
| Research / no trail | Inizia una nuova esplorazione | Scegli seed |
| Research / empty basket | Il cesto è vuoto — esplora e aggiungi | — |
| Search / no results | Nessun risultato — prova una formulazione più ampia | Concetti core suggeriti |
| Search / low confidence | Risultati incerti | Widen query hint |
| Import / no file | Trascina un documento per iniziare | Sfoglia |
| Inspector tab empty | Nessun elemento in questa sezione | Contextual CTA per tab |

**Hidden sections (not empty):** Explain F (Authors), I (Decisions) when zero items.

---

## 13. Loading states

Non-blocking where possible. Per product §21.2.

| Surface | Pattern |
|---------|---------|
| Unified search | Inline spinner in field; results crossfade 150ms |
| Explorer | Card skeletons 3×2 grid |
| Explain Page | Region skeletons top→bottom (A→L order) |
| Graph layout | 15 skeleton nodes → fade in ≤1s |
| Graph expand | Spinner on toolbar; existing nodes persist |
| Source reader body | Top progress bar; metadata then body stagger |
| PDF page | Progressive page placeholders |
| Passage jump | Scroll then 300ms highlight flash |
| Import | Stepped progress: Caricamento → Analisi |
| Annotation save | Inline spinner on row; optimistic highlight tint |
| Citation builder step | Button spinner on confirm |
| Research suggestions | Card skeletons 3 rows |
| Author index | Table row skeletons |

**Rule:** Reader canvas interactive while Note tab loads.

---

## 14. Error states

Italian plain language; retry where applicable; no stack traces or OR IDs.

| Error | Message | Recovery |
|-------|---------|----------|
| Import failed | Importazione non riuscita | Riprova |
| Search unavailable | Ricerca non disponibile | Keyword fallback mode banner |
| Graph too large | Troppi nodi — restringi i filtri | Auto-suggest filter; offer List view |
| Annotation save failed | Annotazione non salvata | Riprova; draft preserved locally |
| Concept not found | Concetto non trovato | Redirect Explorer + toast |
| Source not found | Fonte non trovata | ← Sources |
| Merge conflict | Unione non possibile | Modal with reason; dismiss |
| Citation blocked (esclusa) | Fonte esclusa dal corpus | Link to exclusion reason |
| Proposal rejected display | (object removed) | Toast only |
| Network offline | Sei offline — modifiche in coda | Banner; sync on reconnect |
| Graph render failed | Grafo non disponibile | List view automatic |
| Trail save failed | Trail non salvato | Riprova |
| AI action failed | Azione non completata | Riprova (PX-2 pattern) |

---

## 15. Animations & motion

### 15.1 Principles

- Calm, purposeful — no decorative motion
- `transition-colors duration-200` default for hover/focus
- No layout-shifting hover scales on dense lists
- `prefers-reduced-motion` honored globally

### 15.2 Named transitions

| Context | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Search results appear | Opacity 0→1 | 150ms | ease-out |
| Explorer card hover | Background color | 200ms | ease |
| Explain region expand ("Mostra tutto") | max-height | 200ms | ease-out |
| Inspector collapse | width + opacity | 200ms | ease-out |
| AI panel slide-in | translateX | 200ms | ease-out |
| Graph node appear (initial) | opacity + scale 0.95→1 | 300ms | ease-out |
| Graph node expand (L1+) | opacity fade-in | 200ms | ease-out |
| Passage highlight flash | background tint pulse | 300ms | ease — once |
| Passage jump scroll | smooth scroll | 400ms | ease-in-out |
| Modal open | backdrop opacity + panel scale 0.98→1 | 200ms | ease-out |
| Toast | slide up | 200ms | ease-out; auto-dismiss 5s |
| Lifecycle badge change | color crossfade | 150ms | ease |
| Trail step add | fade + slide left 8px | 150ms | ease-out |
| Coach mark | opacity + translateY 4px | 200ms | ease-out |

### 15.3 Reduced motion overrides

| Normal | Reduced |
|--------|---------|
| Graph node scale-in | Instant opacity |
| Inspector width animate | Instant show/hide |
| Passage flash | Solid outline 1s |
| Modal scale | Opacity only |
| Smooth scroll | Instant jump |

### 15.4 Z-index scale

| Layer | z-index |
|-------|---------|
| Base content | 0 |
| Sticky Explain header / action bar | 10 |
| ContextBar | 10 |
| Inspector overlay backdrop | 40 |
| Inspector drawer | 50 |
| Graph toolbar | 20 |
| Modal / Import | 60 |
| AI lateral overlay | 55 |
| Passage toolbar | 30 |
| Toast | 70 |
| Coach mark | 80 |

---

## 16. Context integration (PX-2 delta)

PX-2 surfaces unchanged in layout. PX-3 adds:

| Surface | Addition |
|---------|----------|
| ContextBar | Live concept count; chip → Explain when overlap |
| Contesto tab (Writing) | Concept neighborhood 1-hop summaries |
| Writing AI panel | explain · find_related · extract_concepts · compare_sources · controversies when context applies |
| Source peek (Writing) | Concept chips + annotation count (read-only) |
| Home activity | Knowledge events; Riprendi ricerca |
| Linked sources footer | Annotation count per source |

---

## 17. Onboarding

Contextual coach marks — not marketing tour. Max 3-step chains; always skippable.

### 17.1 First Knowledge open

1. Explorer — "I concetti sono il centro della tesi"
2. Explain Page — "Spiega questa tesi — tutto in un luogo"
3. Graph — "Naviga le relazioni"

### 17.2 Just-in-time

| Trigger | Hint |
|---------|------|
| First semantic search | Puoi scrivere una domanda, non solo parole chiave |
| First annotation | Le annotazioni collegano lettura e scrittura |
| First graph expand | Espandi solo ciò che ti serve |
| First research trail | Il trail si salva e riprende da Home |
| First concept proposal | Approva i concetti estratti per usarli nel grafo |

### 17.3 PX-2 upgrade

Single toast first open: "Knowledge è attivo — esplora concetti e annotazioni."

---

## 18. PX-3 exclusions (UI)

| Deferred | Milestone |
|----------|-----------|
| Research spatial canvas | PX-5 |
| Citation format validator (W-06 full) | PX-6 |
| Bibliography export | PX-6 |
| Multi-project knowledge isolation | PX-6 |
| Collaborative annotations | PX-6+ |
| Concept file editor (Settings) | Admin path |

---

## 19. Qualification UI trace

Maps to QWO-PX3-001 (product §23):

| AC | UI verification |
|----|-----------------|
| AC-1…AC-15 | Per v1 criteria — Explorer, Explain, Graph, search, source, annotation, import, citation, author, research, AI, proposals, search exclusion, PX-2 regression |
| AC-16 | Lifecycle badge on concept, source, annotation surfaces |
| AC-17 | Explain regions A–L all render |
| AC-18 | Graph 15 default; 100 hard → List view |
| AC-19 | Search seven modes; grouped results |
| AC-20 | Badge promotes on link/cite (no manual control) |

---

## WO-TRACE

```text
px3-knowledge-experience-v2.md (FROZEN)
  → UX Alignment Review PASS
  → px3-knowledge-experience-ui-spec.md (FROZEN)
  → Engineering (post PX-2 qualification)
```
