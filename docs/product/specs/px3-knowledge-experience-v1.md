# PX-3 — Knowledge Experience

> **Product Specification v1** · Product Architect · 2026-07-04  
> **Superseded by:** [`px3-knowledge-experience-v2.md`](px3-knowledge-experience-v2.md) — use v2 for UX handoff  
> **Status:** SUPERSEDED  
> **Builds on:** PX-2 Research Workspace Experience (frozen at implementation start)  
> **Does not amend:** Product Constitution v1.0, ADR-0034…0041, META-1  
> **Does not modify:** PX-2 specification or behavior

---

## 0. Document purpose

This specification defines the **complete knowledge experience** of ThesisOS — how the
operator discovers, navigates, reads, annotates, connects, and cites **knowledge**
(concepts, sources, authors, relationships) as a unified layer above the Research
Workspace delivered in PX-2.

The operator no longer meets Knowledge and Research as stubs. They meet a **living
knowledge system** where concepts — not files — are the center of navigation.

**In scope:** Knowledge module activation, enriched Sources as knowledge objects,
semantic discovery, concept and author navigation, knowledge graph browsing,
annotations, citation depth, research workflow mediated by knowledge.  
**Out of scope:** PX-5 Research canvas (spatial graph exploration), PX-6 polish
(citation validator, multi-project), ASEP framework changes, PX-2 workspace changes.

### Milestone reframe (program note)

Product Constitution §10 originally split **Sources (PX-3)** and **Knowledge (PX-4)**.
This specification consolidates the **knowledge layer** under one milestone name:

```text
PX-3 — Knowledge Experience
```

Sources remain a module in navigation (ADR-0036) but are experienced as **knowledge
objects** linked to concepts, authors, and chapters — not a file library. Research
canvas (full-map exploration) remains a later milestone (PX-5).

---

## 1. Product thesis

ThesisOS succeeds when research feels like **thinking in concepts**, not managing files.

```text
Knowledge  →  Sources  →  Writing  →  Output
     ↑              ↑
  Explorer      Reading · Annotations · Citations
     ↑
  Discovery · Semantic search · Graph
```

**PX-2** answered: *Where do I work?*  
**PX-3** answers: *What does my research know, and how do I move through it?*

**Design north stars:**

| Product | Pattern borrowed |
|---------|------------------|
| **Obsidian** | Graph as navigation aid; backlinks |
| **ResearchRabbit** | Discovery from a seed concept |
| **Zotero** | Source metadata and citation seriousness |
| **Notion** | Structured entity pages |
| **Linear** | Fast filter, search, keyboard jump |
| **Arc** | Spatial memory — return to last concept trail |

**Core belief (ADR-0037):** One concept, one canonical node. Sources, chapters, and
decisions **bridge to concepts** — never the reverse.

---

## 2. Capabilities map

Each capability is a **user-perceived outcome**, qualification target, and scope boundary.

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-3.1** | Semantic Discovery | Operator finds sources, concepts, and passages by meaning — not only title |
| **PX-3.2** | Knowledge Explorer | Operator browses the project's knowledge landscape in one dedicated module |
| **PX-3.3** | Concept Navigation | Operator moves from any concept to definition, relations, sources, chapters, decisions |
| **PX-3.4** | Knowledge Graph | Operator sees and traverses concept relationships visually and structurally |
| **PX-3.5** | Source Relationships | Operator understands how each source connects to concepts, authors, and chapters |
| **PX-3.6** | Reading Experience | Operator reads sources with continuity, context, and knowledge overlay |
| **PX-3.7** | Annotation Workflow | Operator highlights, notes, and links passages to concepts and chapters — persisted |
| **PX-3.8** | Citation Workflow | Operator builds and inspects citations from knowledge context — not only from Writing |
| **PX-3.9** | Author Navigation | Operator explores corpus by author as a first-class lens |
| **PX-3.10** | Research Workflow | Operator conducts literature exploration that feeds Writing without leaving the knowledge layer |

```text
PX-3 Knowledge Experience
├── PX-3.1  Semantic Discovery
├── PX-3.2  Knowledge Explorer
├── PX-3.3  Concept Navigation
├── PX-3.4  Knowledge Graph
├── PX-3.5  Source Relationships
├── PX-3.6  Reading Experience
├── PX-3.7  Annotation Workflow
├── PX-3.8  Citation Workflow
├── PX-3.9  Author Navigation
└── PX-3.10 Research Workflow
```

---

## 3. Personas

### 3.1 Thesis Operator (primary)

Same as PX-2. Italian operator copy; English nav labels. Now expects concept-centric
navigation comparable to Obsidian graph + Zotero source seriousness.

### 3.2 Secondary — Returning researcher

Operator returns after days away. Needs to **re-enter the knowledge trail** — last
concept, last source, open annotations — not reconstruct from memory.

---

## 4. Information architecture (PX-3 delta)

Frozen sidebar (ADR-0036). PX-3 **activates** Knowledge and **enriches** Sources and
Research entry.

| Route | PX-2 state | PX-3 activation |
|-------|------------|-----------------|
| `/knowledge` | Stub | **Knowledge Explorer** home |
| `/knowledge/[conceptId]` | Stub | **Concept page** — Explain this thesis |
| `/knowledge/graph` | — | **Knowledge Graph** view (new sub-route) |
| `/knowledge/authors` | — | **Author index** |
| `/knowledge/authors/[authorId]` | — | **Author page** |
| `/sources` | List + search | Semantic search, concept filters, relationship chips |
| `/sources/[sourceId]` | Reader | Full reading + annotations + concept links + citations |
| `/research` | Stub | **Research entry** — redirects to discovery workflow (§14), not canvas |
| `/writing/*` | Workspace | Unchanged; receives deep links from knowledge |

### 4.1 Module relationship

```text
                    ┌─────────────┐
                    │  Knowledge  │  ← ontological lens (definitions, Explain)
                    │  Explorer   │
                    └──────┬──────┘
                           │ same graph
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Sources      Writing      Decisions
         (evidence)   (argument)   (constraints)
              │            ▲
              └────────────┘
                   citations · annotations · concepts
```

**Knowledge** = *what the thesis knows*  
**Sources** = *what the thesis is built from*  
**Research** (PX-3) = *how the operator explores outward* — canvas map deferred PX-5

### 4.2 Screen hierarchy

```text
AppShell
├── Home
├── Knowledge                          ← PX-3 primary surface
│   ├── Explorer (/knowledge)
│   ├── Concept page (/knowledge/[id])
│   ├── Graph (/knowledge/graph)
│   └── Authors (/knowledge/authors/…)
├── Sources                            ← enriched
├── Research                           ← discovery entry (not canvas)
├── Writing                            ← PX-2 frozen
├── AI
└── Settings
```

---

## 5. User journeys

### 5.1 Journey A — Explain this thesis (killer feature)

```text
Knowledge → search or browse → Concept "Aura benjaminiana"
  → Concept page: definition, role in thesis, linked sources,
     chapters, supporting/contradicting concepts, decisions
  → [ Spiega ] AI summary (lateral, pre-contextualized)
  → [ Vai al capitolo ] → Writing deep link
  → [ Vedi nel grafo ] → Graph focused on node
```

**Success:** Operator understands a concept's role in **under 60 seconds**.

### 5.2 Journey B — Discover from a question

```text
Home → Ricerca OR ⌘K "Cerca nel corpus…"
  → Semantic search: natural-language query
  → Results grouped: Concetti · Fonti · Passaggi · Autori
  → Open passage hit → Source reader scrolled to passage
  → Highlight → Annotazione → Link to concept
  → [ Usa in Scrittura ] → Writing with citation pre-filled
```

**Success:** Question → evidence → writing path without manual indexing.

### 5.3 Journey C — Read and annotate a source

```text
Sources → open source → Reading view
  → Read with metadata + concept chips + chapter links visible
  → Select passage → Evidenzia + Nota
  → Link nota to concept (proposed if new)
  → Annotation appears in source sidebar + concept page
  → [ Cita ] → Writing or copy citation string
```

**Success:** Reading produces **durable knowledge artifacts**, not lost highlights.

### 5.4 Journey D — Traverse the graph

```text
Knowledge → Graph
  → Pan/zoom concept network
  → Click node → Concept page preview panel
  → Double-click → full Concept page
  → Filter: mostra solo concetti con fonti / in capitoli approvati
  → Follow edge "contradicts" → rival concept
```

**Success:** Operator sees structure of argument, not a hairball.

### 5.5 Journey E — Explore by author

```text
Knowledge → Authors → Benjamin, W.
  → Author page: all sources, concepts influenced, chapters citing
  → Open source → read → annotate
  → Compare two authors (side-by-side source lists + shared concepts)
```

**Success:** Author is a **navigable lens**, not metadata filter only.

### 5.6 Journey F — Research session → Writing

```text
Research entry → set exploration scope (concept seed or question)
  → Discovery trail records visited nodes (session breadcrumb)
  → Collect sources/annotations into "Research basket" (session-scoped)
  → [ Porta in Scrittura ] → Writing chapter picker
  → Linked items appear in chapter knowledge footer
  → Trail resumable from Home "Riprendi ricerca"
```

**Success:** Exploration has **memory and handoff** — not a dead end.

### 5.7 Journey G — Import and knowledge extraction

```text
Home → Importa documento OR Sources → Importa
  → Drop PDF/markdown → processing state
  → Proposal: metadata + suggested concepts + candidata status
  → Operator approves → source indexed → concepts linked (proposed → approved)
  → Appears in Explorer, Graph, semantic search
```

**Success:** New material enters the **knowledge layer**, not a folder.

### 5.8 Journey H — Citation from knowledge context

```text
Concept page → Fonte chiave → Passage with annotation
  → [ Cita questo passaggio ]
  → Chapter picker (if not in Writing) → citation inserted
  → Citation record links: source + concept + chapter + locator
  → Visible in Knowledge citation index and Writing chapter footer
```

**Success:** Citations are **knowledge objects** with provenance, not bare strings.

---

## 6. Knowledge Explorer

The Explorer is the **home of the Knowledge module** — not a file list.

### 6.1 Layout

```text
┌─────────────────────────────────────────────────────────────┐
│  Cerca concetti, fonti, autori…          [ Grafo ] [ Autori ]│
├──────────────┬──────────────────────────────────────────────┤
│  Filters     │  Main canvas                                  │
│  · Stato     │  · Featured concept (thesis core)               │
│  · Capitolo  │  · Concept cards grid / list                    │
│  · Fonte     │  · Recent exploration                           │
│  · Relazione │  · Open decisions touchpoints                   │
└──────────────┴──────────────────────────────────────────────┘
```

### 6.2 Explorer modes

| Mode | View | Default sort |
|------|------|--------------|
| **Concetti** | Card grid | Relevance to active thesis phase |
| **Lista** | Dense table | Alphabetical |
| **Recenti** | Activity-based | Last visited |
| **Nucleo** | Curated core map | From Theory Map / project config |

### 6.3 Concept card

```text
┌──────────────────────────────┐
│ Aura · Concetto core         │
│ Benjamin — riproducibilità   │
│ 4 fonti · 2 capitoli · 1 rivale│
│ [ Apri ]  [ Grafo ]          │
└──────────────────────────────┘
```

| Element | Content |
|---------|---------|
| Title | Canonical concept name |
| Subtitle | One-line definition snippet |
| Chips | Source count, chapter count, relation hint |
| Status | Core · In uso · Latente · Proposed (unapproved extraction) |

### 6.4 Filters (left rail)

| Filter | Options |
|--------|---------|
| Stato concetto | Core · Approvato · Proposto · Latente |
| Capitolo | Any chapter in outline |
| Fonte collegata | Pick source → concepts using it |
| Relazione | supports · contradicts · extends · related |
| Decisione | Concepts touched by binding decisions |

Filters combine (AND). Clear all restores default Explorer.

### 6.5 Featured concept

Top of Explorer shows **thesis anchor concept** (from project config or Theory Map).
Rotates by phase if configured. Always links to full Explain page.

---

## 7. Concept page — Explain this thesis

The concept page is the **canonical view of one knowledge node** (ADR-0037 singleton).

### 7.1 Page structure

```text
┌─────────────────────────────────────────────────────────────┐
│ ← Knowledge    Aura benjaminiana              [ Grafo ] [ AI ]│
├─────────────────────────────────────────────────────────────┤
│ DEFINIZIONE                                                  │
│ Canonical definition text (editable via proposal only)       │
├─────────────────────────────────────────────────────────────┤
│ RUOLO NELLA TESI                                             │
│ Why this concept matters; thesis phase relevance             │
├─────────────────────────────────────────────────────────────┤
│ RELAZIONI                                                    │
│ Supports ← → Contradicts ← → Extends ← → Related             │
├─────────────────────────────────────────────────────────────┤
│ FONTI                                                        │
│ Ranked sources with passage anchors and annotation count     │
├─────────────────────────────────────────────────────────────┤
│ CAPITOLI                                                     │
│ Chapters using this concept — jump links to Writing          │
├─────────────────────────────────────────────────────────────┤
│ DECISIONI                                                    │
│ Linked binding/open decisions — cards, not raw IDs           │
├─────────────────────────────────────────────────────────────┤
│ CITAZIONI                                                    │
│ All citations where this concept appears                     │
├─────────────────────────────────────────────────────────────┤
│ GRAFO LOCALE                                                 │
│ 1-hop neighborhood mini-graph (interactive)                  │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Concept navigation patterns

| From | Action | To |
|------|--------|-----|
| Any concept link | Click title | Concept page |
| Relation chip | Click | Target concept page |
| Source row | Click | Source reader at passage |
| Chapter row | Click | Writing `/writing/[id]?section=` |
| Decision card | Click | Contesto-style summary modal |
| Mini-graph node | Click | That concept page |
| Breadcrumb | Knowledge | Explorer |

**Back stack:** Browser back preserves exploration trail. In-app **← Knowledge**
returns to Explorer with filters restored.

### 7.3 Concept states (operator-visible)

| State | Meaning | UX |
|-------|---------|-----|
| **Core** | Thesis-critical; in Theory Map | Prominent badge |
| **Approvato** | Canonical node confirmed | Default |
| **Proposto** | Extracted/suggested; not yet approved | Dashed border; approve action |
| **Latente** | In corpus but unused in chapters | Muted; "Non ancora in uso" |

Approving a proposed concept is a **proposal flow** (same inbox model as PX-2).

### 7.4 Concept merge (alias)

If operator finds duplicates:

```text
Unisci con… → pick canonical target → proposal shows merge diff
  → Approve → aliases redirect; links consolidate
```

Rare action; available in concept page overflow menu.

---

## 8. Knowledge Graph

PX-3 delivers **graph as navigation** in the Knowledge module. PX-5 will deliver
**Research canvas** — spatial exploration at project scale. PX-3 graph is **focused,
readable, bounded**.

### 8.1 Graph layout

```text
┌─────────────────────────────────────────────────────────────┐
│  Filtri · Cerca nodo · Layout: Forza | Gerarchia | Radiale    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│              (concept nodes + typed edges)                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Preview panel: selected node summary + [ Apri ]            │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Node visual encoding

| Attribute | Visual |
|-----------|--------|
| Core concept | Larger node, accent fill |
| Proposed | Dashed outline |
| Latent | Smaller, muted |
| In approved chapter | Solid border ring |
| Has open decision | Amber dot |

### 8.3 Edge types (typed, labeled on hover)

| Relation | Label (IT) | Color token |
|----------|------------|-------------|
| supports | sostiene | green-muted |
| contradicts | contraddice | amber |
| extends | estende | accent |
| related | correlato | ink-muted |
| used_in | usato in | (edge to chapter — optional PX-3 show as chip list instead) |

Operator can hide edge types via filter toggles.

### 8.3 Graph interactions

| Interaction | Behavior |
|-------------|----------|
| Click node | Select + preview panel |
| Double-click | Open concept page |
| Click edge | Tooltip: relation type + short gloss |
| Scroll | Zoom |
| Drag canvas | Pan |
| Drag node | Pin position (session-persisted) |
| ⌘F | Focus search — type to highlight matching nodes |
| Esc | Deselect |

### 8.4 Graph scopes

| Scope | Entry |
|-------|-------|
| **Full project** | `/knowledge/graph` |
| **Local 1-hop** | Concept page mini-graph |
| **From selection** | Explorer: "Mostra selezione nel grafo" |
| **From author** | Author page: concepts influenced subgraph |

**Cognitive guardrail:** Full graph defaults to **core + 1-hop** expansion. Operator
explicitly expands: "Mostra concetti latenti" / "Mostra tutto" with confirm if > 50 nodes.

### 8.5 Graph vs Research canvas (PX-5)

| | PX-3 Knowledge Graph | PX-5 Research Canvas |
|---|---------------------|----------------------|
| Purpose | Navigate known concepts | Explore unknown landscape |
| Lens | Ontological | Exploratory |
| Default density | Bounded | Expansive |
| Entry | Knowledge module | Research module |

PX-3 `/research` route shows discovery workflow (§14) — not the canvas.

---

## 9. Semantic search & discovery

### 9.1 Unified search bar

Available in: Knowledge Explorer, Sources, AppShell (⌘K extension), Research entry.

| Input | Behavior |
|-------|----------|
| Keywords | Title, author, concept name match |
| Natural language | Semantic retrieval ranked by meaning |
| Scoped prefix | `concept:`, `author:`, `source:`, `passage:` |

**Example queries:**

- `concept:aura riproducibilità`
- `author:Benjamin`
- `passage: "work of art in the age of mechanical reproduction"`

### 9.2 Results layout

Grouped sections (collapsible):

```text
Concetti (3)
Fonti (8)
Passaggi (12)
Autori (2)
```

| Group | Row content |
|-------|-------------|
| Concetti | Name, definition snippet, relation hint |
| Fonti | Title, author, year, status badge |
| Passaggi | Source title + highlighted excerpt |
| Autori | Name, source count, top concepts |

Click row → navigate to entity page. `Enter` on highlighted row → primary navigation.

### 9.3 Discovery filters (post-search)

Narrow results by: status (approvata/esclusa), chapter linkage, concept relation, date,
annotation presence.

### 9.4 Empty and low-confidence search

| Case | UX |
|------|-----|
| No results | "Nessun risultato — prova una formulazione più ampia" + suggested concepts |
| Low confidence | "Risultati incerti" banner; top 3 concepts as alternative pivots |
| Excluded hits | Shown in separate "Escluse dal corpus" section — not mixed with active results |

### 9.5 Search history

Last **10** queries per operator; clearable. Recent searches influence Explorer
"Recenti" mode — not LLM personalization.

---

## 10. Source relationships

Every source is a **knowledge object**, not a file card.

### 10.1 Source page structure (enriched)

```text
┌─────────────────────────────────────────────────────────────┐
│ ← Sources    Benjamin (1936) — L'opera d'arte…    [ Stato ] │
├──────────────────────┬──────────────────────────────────────┤
│  Metadata            │  Reading body                         │
│  · Author → link     │                                       │
│  · Year · Type       │                                       │
│  · Concetti (N)      │                                       │
│  · Capitoli (N)      │                                       │
│  · Citazioni (N)     │                                       │
│  · Annotazioni (N)   │                                       │
│  · Relazioni fonte   │                                       │
├──────────────────────┴──────────────────────────────────────┤
│  [ Cita ] [ Collega concetto ] [ Collega capitolo ] [ AI ]  │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Relationship types (source ↔ source)

| Relation | Operator label | Example |
|----------|------------------|---------|
| cites | Cita | A cites B |
| responds_to | Risponde a | Critique response |
| same_author | Stesso autore | Cluster (also via Author page) |
| shared_concept | Concetti condivisi | Implicit badge — N concepts |
| companion | Lettura consigliata | Manual link by operator |

Manual relations via overflow → "Collega a un'altra fonte" → proposal.

### 10.3 Source ↔ concept links

| Link state | Meaning |
|------------|---------|
| **Proposed** | AI/import suggested |
| **Confirmed** | Operator approved |
| **Rejected** | Removed from concept (audit retained) |

Concept chips on source page are clickable → concept page. Unlinked extracted terms
show as "Concetti suggeriti" with batch approve.

### 10.4 Source ↔ chapter links

Inherited from PX-2; enriched with:

- Passages cited in chapter (locators)
- Annotations referenced in chapter
- Concept bridge count per chapter

### 10.5 Source status (unchanged semantics)

```text
Candidata → Approvata → Esclusa
```

| Status | Knowledge UX |
|--------|--------------|
| Candidata | Visible; semantic search with badge; cite requires approval (PX-2 rule) |
| Approvata | Full participation in graph and citations |
| Esclusa | Visible; reason shown; excluded from default search; not citable |

---

## 11. Reading experience

Reading is a **first-class mode** — calm, anchored, knowledge-aware.

### 11.1 Reading layout modes

| Mode | When |
|------|------|
| **Standard** | Source page split (metadata rail + body) |
| **Focus** | Body only; metadata on hover / Esc |
| **Split** | Source + concept page side-by-side (from concept source link) |
| **Peek** | PX-2 Writing peek unchanged — PX-3 adds annotation read-only in peek |

### 11.2 Reading chrome

| Element | Behavior |
|---------|----------|
| Progress | Scroll percent in chapter/source |
| Locator | Visible passage ID for citation |
| Concept overlay | Toggle: highlight concept mentions in body |
| Previous visits | "Visitato 3 giorni fa — riprendi da §2" |
| Typography | Max ~70ch; comfortable line height (design system) |

### 11.3 Passage selection

Select text → floating toolbar:

```text
Evidenzia · Nota · Cita · Collega a concetto · Copia
```

| Action | Result |
|--------|--------|
| Evidenzia | Color highlight persisted |
| Nota | Margin note linked to passage |
| Cita | Citation workflow (§13) |
| Collega a concetto | Pick or create concept proposal |
| Copia | Plain text + optional citation string |

### 11.4 Reading continuity

When operator returns to source:

- Restore scroll position
- Restore open annotation panel
- Show "Nuove annotazioni" if changed elsewhere (single-tab default)

### 11.5 PDF vs markdown sources

Operator sees **consistent reading chrome**. Long PDFs show section sidebar from
document headings. Page numbers visible for citation locators.

---

## 12. Annotation workflow

PX-2 allowed local highlight; PX-3 **persists and links** annotations.

### 12.1 Annotation object

| Field | Operator-visible |
|-------|------------------|
| Passage | Highlighted text |
| Note | Optional free text |
| Color | 5 preset colors |
| Concepts | 0–N linked concepts |
| Chapters | 0–N linked chapters |
| Created | Timestamp |

### 12.2 Annotation lifecycle

```text
Create → (optional) Link concept/chapter → Saved
  → Edit note / recolor → Saved
  → Delete → Confirm
```

Bulk actions in source sidebar: filter by color, concept, chapter.

### 12.3 Annotation surfaces

| Surface | View |
|---------|------|
| Source page | Margin list synced to scroll |
| Concept page | "Passaggi annotati" section |
| Chapter (Writing) | Footer: annotations feeding this chapter |
| Knowledge Explorer | Filter "Con annotazioni" |
| Research basket | Add annotation to session collection |

### 12.4 Annotation proposals

AI-suggested annotations from import or "Estrai concetti" arrive as **proposed**
highlights. Operator approves individually or batch from source page.

### 12.5 Annotation ↔ citation

Annotation can generate citation string without re-selecting passage. Citation
record points to annotation locator.

---

## 13. Citation workflow (knowledge layer)

Extends PX-2 cite flow with **knowledge-native** citations.

### 13.1 Citation entry points

| From | Flow |
|------|------|
| Writing (PX-2) | Unchanged — ⌘⇧C, picker, peek |
| Source reader | Passage toolbar → Cita |
| Concept page | Fonte → passage → Cita |
| Annotation | Cita da annotazione |
| Citation index | Browse all → jump to source/passage/chapter |

### 13.2 Citation index

New sub-view: **Knowledge → Citazioni** or Sources → Citazioni tab.

| Column | Content |
|--------|---------|
| Citation | Formatted string (Author, Year) + locator |
| Source | Link |
| Concept | Primary concept link |
| Chapter | Link to Writing |
| Status | Valida · Da verificare · Esclusa (source) |

Filter by chapter, concept, author, source.

### 13.3 Citation record (operator mental model)

A citation is not only inline text — it is a **bridge object**:

```text
Citation
  ├── source + locator (passage or page)
  ├── optional concept (why this evidence)
  ├── chapter + position in prose
  └── annotation (optional origin)
```

### 13.4 Citation builder (modal)

For manual or corrective citations:

```text
1. Pick source
2. Pick passage (scroll or search within source)
3. Pick concept (optional but encouraged)
4. Pick chapter (if not in Writing)
5. Preview format → Inserisci
```

### 13.5 Bibliography view

Sources → **Bibliografia** tab: approved sources in academic order. Export deferred
PX-6; view-only in PX-3.

### 13.6 W-06 platform limitation

Inherited from PX-2: AI may emit numeric cites. Knowledge layer flags "Da verificare"
on suspicious formats. Full validator deferred PX-6. Operator can edit from citation
index.

---

## 14. Research workflow (PX-3)

PX-3 **Research** is a **guided exploration mode** — not the spatial canvas (PX-5).

### 14.1 Research entry (`/research`)

```text
┌─────────────────────────────────────────────────────────────┐
│  Da dove vuoi iniziare?                                       │
│  ○ Da un concetto    ○ Da una domanda    ○ Da una fonte     │
├─────────────────────────────────────────────────────────────┤
│  [ seed picker or search ]                                   │
│  [ Inizia ricerca ]                                          │
└─────────────────────────────────────────────────────────────┘
```

### 14.2 Exploration session

Once started, Research shows **trail UI**:

```text
┌─────────────────────────────────────────────────────────────┐
│  Ricerca: "aura e riproducibilità"          [ Termina ]      │
│  Trail: Concetto A → Fonte B → Concetto C → …               │
├──────────────┬──────────────────────────────────────────────┤
│  Basket (N)  │  Current entity (concept/source/passage)      │
│  · sources   │  + suggested next steps                       │
│  · notes     │  · Concetti correlati                         │
│  · annot.    │  · Fonti collegate                            │
│              │  · Passaggi simili                            │
├──────────────┴──────────────────────────────────────────────┤
│  [ Porta in Scrittura ]  [ Salva trail ]  [ Grafo locale ]  │
└─────────────────────────────────────────────────────────────┘
```

### 14.3 Suggested next steps

Ranked cards — not AI chat:

| Suggestion type | Example |
|-----------------|---------|
| Related concept | "Vedi anche: Tecniche riproducibili" |
| Shared source | "Stessa fonte in Cap. 2" |
| Contradiction | "Conflitto con DEC-012" |
| Unread passage | "Passaggio non annotato in Benjamin" |

Click adds to trail and navigates.

### 14.4 Research basket

Session-scoped collection. Items persist until:

- Porta in Scrittura (links to chapter)
- Salva trail (named saved research — resumable from Home)
- Termina (prompt: save or discard)

### 14.5 Home integration

| Element | Behavior |
|---------|----------|
| Quick action Ricerca | Opens Research entry |
| Riprendi ricerca | Last saved trail or active session |
| Activity feed | "Esplorazione: aura e riproducibilità" |

### 14.6 Research vs Writing boundary

Research **never edits chapter prose**. Handoff to Writing is explicit. ContextBar
in Writing shows items imported from basket.

---

## 15. Author navigation

Authors are **first-class entities** — not only source metadata fields.

### 15.1 Author index (`/knowledge/authors`)

| Column | Content |
|--------|---------|
| Author | Name (sorted) |
| Fonti | Count |
| Concetti | Top 3 concept chips |
| Capitoli | Count citing this author |

Search by name variant. Merge duplicates (proposal) — e.g. "Benjamin, W." vs "Walter Benjamin".

### 15.2 Author page

```text
┌─────────────────────────────────────────────────────────────┐
│ ← Autori    Walter Benjamin                                  │
├─────────────────────────────────────────────────────────────┤
│ BIOGRAFIA (optional short note — proposal edit)              │
├─────────────────────────────────────────────────────────────┤
│ FONTI (N)          │ sorted by year                           │
│ CONCETTI (N)       │ concepts influenced                      │
│ CAPITOLI (N)       │ chapters citing                          │
│ RETE               │ mini-graph: author → sources → concepts  │
├─────────────────────────────────────────────────────────────┤
│ [ Confronta autore… ]  [ Cerca in autore ]                   │
└─────────────────────────────────────────────────────────────┘
```

### 15.3 Author compare

Pick second author → split view:

| Left | Right |
|------|-------|
| Author A sources | Author B sources |
| Shared concepts (highlighted) | |
| Unique concepts | |

Read-only analysis — no auto-generated prose in PX-3.

### 15.4 Author → navigation

Click author name **anywhere** (source metadata, citation, concept page) → Author page.

---

## 16. Context integration (product behavior)

PX-3 enriches what the operator sees in **ContextBar** and **Contesto tab** when
surfacing knowledge — without changing PX-2 Writing layout.

| Surface | PX-3 addition |
|---------|---------------|
| ContextBar | Concept count live; click → Knowledge concept page |
| Contesto tab | Concept neighborhood (1-hop summaries) |
| Writing AI | New actions when selection has concept overlap |
| Source peek (Writing) | Show concept chips + annotation count on peeked source |
| Home | Knowledge activity in feed |

### 16.1 New AI actions (knowledge context)

Available in Writing AI panel and Concept page — lateral, not new home:

| Action | Label (IT) | Surface |
|--------|------------|---------|
| explain | Spiega | Concept page |
| find_related | Concetti correlati | Concept / selection |
| extract_concepts | Estrai concetti | Source / selection |
| compare_sources | Confronta fonti | Two sources selected |
| controversies | Controversie | Concept |

All follow PX-2 proposal rules — no silent writes.

---

## 17. Import and ingestion (product flow)

Part of knowledge entry — not a separate admin task.

### 17.1 Import entry

| Entry | Destination |
|-------|-------------|
| Home → Importa documento | Import modal |
| Sources → Importa | Import modal |
| Drag-drop on Sources | Import modal |

### 17.2 Import states (operator)

```text
Caricamento → Analisi → Proposta pronta → (approva) → Indicizzata
```

| State | UX |
|-------|-----|
| Caricamento | Progress bar |
| Analisi | "Estrazione metadati e concetti…" |
| Proposta pronta | Review metadata + suggested concepts + candidata |
| Indicizzata | Source fully in knowledge layer |

### 17.3 Import proposal

Operator sees:

- Title, author, year (editable)
- Suggested concepts (checkbox select)
- Status: Candidata (default)
- **Approva import** → proposal → inbox

Reject discards upload. Partial approve not allowed for import bundle.

---

## 18. Interaction rules

| ID | Rule |
|----|------|
| KR-1 | Concepts are canonical — sources link to concepts, not concepts hidden in files |
| KR-2 | One concept slug per project — duplicates merge via proposal |
| KR-3 | Annotations persist and appear on concept + source + chapter |
| KR-4 | Semantic search excludes `esclusa` from default results |
| KR-5 | Graph defaults bounded — expand explicit for large graphs |
| KR-6 | Research mode never edits chapter prose |
| KR-7 | All knowledge mutations go through proposal inbox (PX-2 model) |
| KR-8 | Author names are navigable everywhere they appear |
| KR-9 | Citations link back to source + passage + optional concept |
| KR-10 | Reading focus mode available on every long source |

### 18.1 Proposal types (PX-3 additions)

| Type | Operator label |
|------|----------------|
| `concept_create` | Nuovo concetto |
| `concept_merge` | Unione concetti |
| `concept_link` | Collegamento concetto–fonte |
| `annotation` | Annotazione |
| `source_import` | Importazione fonte |
| `source_relation` | Relazione tra fonti |
| `author_merge` | Unione autori |

Inherited from PX-2: `bibliography`, `chapter_text`, etc.

---

## 19. Navigation and deep linking

### 19.1 Cross-module links

| From | To | Preserves |
|------|-----|-----------|
| Concept → Writing | chapter + section | concept context in URL |
| Source → Writing | chapter | source peek param |
| Research basket → Writing | chapter | basket items |
| Writing → Concept | concept page | return URL to Writing |
| Graph → Concept | concept page | graph viewport state in session |

### 19.2 URL patterns (conceptual)

```text
/knowledge
/knowledge/[conceptSlug]
/knowledge/graph?focus=[conceptSlug]&depth=1
/knowledge/authors/[authorSlug]
/sources/[sourceId]?passage=[locator]
/research?trail=[trailId]
```

### 19.3 Breadcrumbs

| Module | Pattern |
|--------|---------|
| Knowledge | Knowledge / [Concept name] |
| Sources | Sources / [Short title] |
| Graph | Knowledge / Graph |
| Authors | Knowledge / Autori / [Name] |
| Research | Research / [Trail name or "Nuova"] |

---

## 20. Keyboard shortcuts (desktop-first)

Inherited PX-2 global shortcuts plus:

| Shortcut | Action |
|----------|--------|
| `⌘⇧K` | Knowledge search (semantic) |
| `G` `K` | Go Knowledge Explorer |
| `G` `G` | Go Graph |
| `G` `A` | Go Authors |
| `⌘⇧A` | Toggle annotation panel (source reading) |
| `⌘⇧L` | Link selection to concept |
| `⌘Enter` | Confirm annotation or citation builder step |
| `J` / `K` | Next/previous search result |
| `F` | Reading focus mode toggle |
| `[` / `]` | Prev/next source in filtered list |

Command palette gains: Concetti, Autori, Cita da…, Estrai concetti, Mostra nel grafo.

---

## 21. User states

### 21.1 Empty states

| Surface | Message | CTA |
|---------|---------|-----|
| Explorer / no concepts | Nessun concetto — importa fonti o approva estrazioni | Importa |
| Graph / empty | Grafo vuoto | Explorer |
| Author index / empty | Nessun autore — aggiungi fonti | Importa |
| Citation index / empty | Nessuna citazione | Vai a Scrittura |
| Annotations / none | Nessuna annotazione — seleziona un passaggio | — |
| Research / no trail | Inizia una nuova esplorazione | Scegli seed |
| Search / no results | (see §9.4) | |
| Concept / proposed only | Concetto in attesa di approvazione | Approva |

### 21.2 Loading states

| Surface | Pattern |
|---------|---------|
| Semantic search | Inline spinner; results fade in |
| Graph layout | Skeleton nodes → animate in ≤ 1s |
| Source import | Step progress |
| Concept page | Section skeletons |
| Passage jump | Scroll + brief highlight flash |
| PDF render | Page progressive load |

### 21.3 Error states

| Error | Message | Recovery |
|-------|---------|----------|
| Import failed | Importazione non riuscita | Riprova |
| Search unavailable | Ricerca non disponibile | Keyword fallback |
| Graph too large | Troppi nodi — restringi filtri | Auto-suggest filter |
| Annotation save failed | Annotazione non salvata | Retry; local draft |
| Concept not found | Concetto non trovato | Explorer |
| Merge conflict | Unione non possibile | Show reason |

---

## 22. Onboarding (PX-3)

### 22.1 First Knowledge open

Three coach marks (skippable):

1. Explorer — "I concetti sono il centro della tesi"
2. Concept page — "Spiega questa tesi — tutto in un luogo"
3. Graph — "Naviga le relazioni"

### 22.2 Just-in-time

| Trigger | Hint |
|---------|------|
| First semantic search | Puoi scrivere una domanda, non solo parole chiave |
| First annotation | Le annotazioni collegano lettura e scrittura |
| First graph expand | Espandi solo ciò che ti serve |
| First research trail | Il trail si salva e riprende da Home |
| First concept proposal | Approva i concetti estratti per usarli nel grafo |

### 22.3 Upgrade from PX-2

Single toast on first open: "Knowledge è attivo — esplora concetti e annotazioni."

---

## 23. Desktop-first behavior

| Breakpoint | Knowledge UX |
|------------|--------------|
| ≥1280px | Explorer filter rail + canvas; source split reading |
| 1024–1279px | Filter drawer; graph full width |
| 768–1023px | List modes default; graph view-only |
| <768px | Read-only Knowledge browse; "Usa desktop per annotare" |

Graph interaction requires ≥1024px; below shows list representation of same data.

---

## 24. PX-3 exclusions

| Deferred | Milestone |
|----------|-----------|
| Research spatial canvas (full-map) | PX-5 |
| Citation format validator (W-06) | PX-6 |
| Bibliography export (BibTeX/Word) | PX-6 |
| Multi-project knowledge isolation | PX-6 |
| Collaborative annotations | PX-6+ |
| Auto-literature review generation | Out of scope |
| Concept authoring from Settings/blueprint file editor | Admin path unchanged |

---

## 25. Qualification acceptance (QWO-PX3-001 draft)

| # | Criterion |
|---|-----------|
| AC-1 | Knowledge Explorer lists concepts with filters |
| AC-2 | Concept page shows definition, relations, sources, chapters, decisions |
| AC-3 | Knowledge Graph renders typed edges; bounded default scope |
| AC-4 | Semantic search returns grouped concepts, sources, passages |
| AC-5 | Source page shows relationship chips and concept links |
| AC-6 | Annotations persist and appear on source + concept |
| AC-7 | Import flow produces approvable source + concept proposals |
| AC-8 | Citation index lists citations with cross-links |
| AC-9 | Author index and author page navigable from all author links |
| AC-10 | Research trail saves, resumes, and handoffs to Writing |
| AC-11 | Explain (concept) AI action works from concept page |
| AC-12 | Proposed concepts require approval before graph inclusion |
| AC-13 | Esclusa sources excluded from default search |
| AC-14 | PX-2 qualification surfaces unchanged (regression) |
| AC-15 | OR-1…OR-7 regression green |

---

## 26. Capability → deliverable map (for program planning)

| Capability | Primary surfaces |
|------------|------------------|
| PX-3.1 Semantic Discovery | Unified search, Research entry |
| PX-3.2 Knowledge Explorer | `/knowledge` |
| PX-3.3 Concept Navigation | Concept page, breadcrumbs, links |
| PX-3.4 Knowledge Graph | `/knowledge/graph`, mini-graph |
| PX-3.5 Source Relationships | Source page, relation UI |
| PX-3.6 Reading Experience | Source reader, focus mode |
| PX-3.7 Annotation Workflow | Passage toolbar, annotation list |
| PX-3.8 Citation Workflow | Citation builder, index |
| PX-3.9 Author Navigation | Author index + page |
| PX-3.10 Research Workflow | `/research`, basket, trail |

---

## 27. Governance references

| Artifact | Role |
|----------|------|
| `docs/product/VISION.md` | Knowledge before documents |
| ADR-0036 | IA — Knowledge module |
| ADR-0037 | Concept-centric model |
| ADR-0038 | Context Engine — concept neighborhood |
| ADR-0039 | AI lateral actions |
| ADR-0040 | Product state — concepts, sources |
| ADR-0041 | Blueprint sync — concept/source proposals |
| `docs/product/specs/px2-research-workspace-experience-v2.md` | Prior milestone (frozen) |
| `docs/product/specs/thesisos-product-ux-v1.md` | Baseline modules |

IA changes beyond sub-routes require P8. This spec adds sub-routes under Knowledge —
not sidebar changes.

---

## WO-TRACE

```text
PX-2 COMPLETE → PX-3 Authorization (pending)
  → px3-knowledge-experience-v1.md
  → Architect Program Review → PX3-EWO-* → QWO-PX3-001
```
