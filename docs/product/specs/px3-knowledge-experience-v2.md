# PX-3 — Knowledge Experience

> **Product Specification v2** · Head of Product review · 2026-07-04  
> **Supersedes:** `px3-knowledge-experience-v1.md`  
> **Status:** PROPOSED — ready for UX handoff after Architect sign-off  
> **Builds on:** PX-2 Research Workspace Experience (frozen)  
> **Does not amend:** Product Constitution v1.0, ADR-0034…0041, META-1  
> **Does not modify:** PX-2 specification or behavior

---

## 0. Document purpose

Self-contained product specification for PX-3. UX may design from this document
**without product assumptions**. Engineering receives this artifact after UX freeze.

**v2 additions (Head of Product review):**

- §3 Knowledge Object Model — shared entity envelope + type specializations
- §4 Knowledge Lifecycle States — unified state machine + UX mapping
- §9 Explain Page — standalone full specification (killer screen)
- §11 Search — behavior per entity type + ranking rules
- §10 Knowledge Graph — expansion limits, grouping, large-graph guardrails

---

## 1. Product thesis

```text
PX-2 = Workspace     →  Where do I work?
PX-3 = Knowledge     →  What does my research know?
```

```text
Knowledge  →  Sources  →  Writing  →  Output
```

**Invariant:** Research never edits prose — explicit handoff to Writing (PX-2).

**Core belief (ADR-0037):** Concepts are canonical. Sources, chapters, and decisions
**bridge to concepts** — never the reverse.

---

## 2. Capabilities map

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-3.1** | Semantic Discovery | Find knowledge by meaning across entity types |
| **PX-3.2** | Knowledge Explorer | Browse the project knowledge landscape |
| **PX-3.3** | Concept Navigation | Move from any concept to all linked knowledge |
| **PX-3.4** | Knowledge Graph | Traverse relationships visually — bounded, not canvas |
| **PX-3.5** | Source Relationships | See how sources connect to knowledge web |
| **PX-3.6** | Reading Experience | Read with continuity and knowledge overlay |
| **PX-3.7** | Annotation Workflow | Persist highlights and notes as knowledge |
| **PX-3.8** | Citation Workflow | Citations as navigable knowledge bridges |
| **PX-3.9** | Author Navigation | Authors as first-class lens |
| **PX-3.10** | Research Workflow | Exploration with trail, basket, Writing handoff |

---

## 3. Knowledge Object Model

Every entity in the Knowledge layer conforms to a **shared envelope**. UX renders
type-specific pages; the operator mental model stays consistent: *everything is a
Knowledge Object with links and a lifecycle*.

### 3.1 Shared envelope

| Field | Operator-visible | Purpose |
|-------|------------------|---------|
| **id** | No (slug in URL) | Stable identity |
| **slug** | URL only | Unique per project (ADR-0037) |
| **type** | Badge / icon | Entity kind (see §3.2) |
| **title** | Headline | Primary label |
| **subtitle** | One line under title | Secondary label (author, year, role) |
| **summary** | Card snippet / meta | 1–3 sentences max |
| **evidence** | "Evidenze" section | Passages, annotations, locators supporting this object |
| **confidence** | Chip: Alta · Media · Bassa · Non valutata | Epistemic weight (operator-set or import default) |
| **linked_sources** | Count + list | M:N |
| **linked_chapters** | Count + list | M:N |
| **linked_concepts** | Count + chips | M:N (concepts link concepts via relations) |
| **linked_decisions** | Count + cards | M:N |
| **linked_authors** | Count + links | M:N |
| **linked_citations** | Count + list | M:N |
| **created_by** | Provenance chip | Operatore · Importazione · Estrazione · AI |
| **proposal_state** | Inbox integration | Nessuna · In attesa · Approvata · Rifiutata |
| **knowledge_state** | Status badge | Candidate · Validated · Linked · Referenced · Deprecated (§4) |
| **visibility** | Implicit | In search / in graph / muted |

### 3.2 Object types

| Type | Primary surface | Title example |
|------|-----------------|---------------|
| **concept** | Explain Page | Aura benjaminiana |
| **source** | Source reader | L'opera d'arte… (Benjamin, 1936) |
| **author** | Author page | Walter Benjamin |
| **citation** | Citation index row | (Benjamin, 1936, p. 42) |
| **annotation** | Annotation list item | Highlight + note excerpt |
| **passage** | Search result row | Excerpt from source body |

**Passage** is not a persisted standalone object — it is a **locator view** over source
content, addressable in search and evidence lists.

### 3.3 Type specializations

Fields beyond the shared envelope:

**Concept**

| Field | Content |
|-------|---------|
| definition | Canonical definition text |
| role_in_thesis | Why it matters for this project |
| relations | Typed edges: supports, contradicts, extends, related |
| is_core | Boolean — thesis anchor (Theory Map) |

**Source**

| Field | Content |
|-------|---------|
| author_ref | → Author object |
| year | Publication year |
| bibliography_status | Candidata · Approvata · Esclusa (corpus policy) |
| source_relations | cites, responds_to, companion (manual) |

**Author**

| Field | Content |
|-------|---------|
| name_variants | Aliases for merge |
| bio_note | Optional short prose (proposal edit) |

**Citation**

| Field | Content |
|-------|---------|
| formatted_string | (Author, Year) + locator |
| origin | Writing · Knowledge · Import |
| validation_flag | Valida · Da verificare (W-06) |

**Annotation**

| Field | Content |
|-------|---------|
| passage_locator | Start/end in source |
| highlight_color | 5 presets |
| note_text | Optional |

### 3.4 Link semantics

| Link | Direction | Created by |
|------|-----------|------------|
| concept ↔ concept | Typed relation | Operator proposal or extraction |
| concept ↔ source | Evidence link | Annotation, import, manual |
| concept ↔ chapter | Usage link | Writing, manual, citation |
| concept ↔ decision | Constraint link | Governance / manual |
| source ↔ author | Authorship | Metadata |
| citation → all above | Bridge | Cite workflow |

Links inherit the **lowest knowledge_state** of endpoints for graph inclusion rules
(e.g. Candidate concept does not appear in default graph until Validated).

### 3.5 Confidence (operator semantics)

| Level | Meaning | Default when |
|-------|---------|--------------|
| **Alta** | Central to thesis argument | Core concepts, approved sources in approved chapters |
| **Media** | Supporting evidence | Linked sources with annotations |
| **Bassa** | Tentative / exploratory | Candidate extractions |
| **Non valutata** | Not yet judged | New imports |

Operator may change confidence via proposal. Confidence affects **search ranking**
(§11) and **graph node size** (§10) — not truth claims.

---

## 4. Knowledge Lifecycle States

Unified lifecycle for all Knowledge Objects. UX **must** reflect state in badges,
filters, graph visibility, and available actions.

### 4.1 State machine

```text
Candidate  →  Validated  →  Linked  →  Referenced
     │              │           │            │
     └──────────────┴───────────┴────────────┴──→  Deprecated
```

| State | Definition | Operator label (IT) |
|-------|------------|------------------------|
| **Candidate** | Exists as proposal or extraction; not yet confirmed | Candidato |
| **Validated** | Operator approved; canonical entity | Validato |
| **Linked** | ≥1 meaningful link to another knowledge object | Collegato |
| **Referenced** | Appears in chapter prose and/or citation index | Citato in tesi |
| **Deprecated** | Superseded, merged, excluded, or archived | Deprecato |

### 4.2 Transitions

| From | To | Trigger |
|------|-----|---------|
| — | Candidate | Import, AI extraction, manual create proposal submitted |
| Candidate | Validated | Proposal approved |
| Candidate | — | Proposal rejected (object removed from active views) |
| Validated | Linked | First link created (concept-source, concept-chapter, etc.) |
| Linked | Referenced | Citation inserted in chapter OR concept mentioned in saved chapter prose |
| Any | Deprecated | Merge, exclude source, operator archive, decision supersession |
| Deprecated | Validated | Operator restore (proposal) — rare |

**Automatic promotion:** Validated → Linked and Linked → Referenced are **system-derived**
from link/citation events — no manual toggle.

### 4.3 Mapping to legacy labels

| Lifecycle | Concept (v1) | Source (corpus) |
|-----------|--------------|-----------------|
| Candidate | Proposto | Candidata |
| Validated | Approvato | Approvata |
| Linked | In uso | Collegata |
| Referenced | In uso + Citato | Usata in tesi |
| Deprecated | (merged/archived) | Esclusa |

**Core** is orthogonal — a boolean flag on Validated+ concepts in Theory Map.

### 4.4 UX by state

| State | Explorer | Graph default | Search default | Primary actions |
|-------|----------|---------------|----------------|-----------------|
| Candidate | Visible; dashed card | Hidden | Separate section "Candidati" | Approva · Rifiuta |
| Validated | Normal card | Visible if core or filtered | Included | Collega · Apri |
| Linked | Chips show link counts | Visible | Rank boost | Naviga link |
| Referenced | "Citato in tesi" badge | Emphasized node | Rank boost | Vai a capitolo |
| Deprecated | Muted; filter off default | Hidden | "Deprecati" section only | Leggi · Ripristina |

### 4.5 Proposal_state × knowledge_state

| proposal_state | knowledge_state | UX |
|----------------|-----------------|-----|
| In attesa | Candidate | In inbox + dashed UI |
| Approvata | → Validated | Normal |
| Rifiutata | — | Removed from active UI |
| Nessuna | ≥ Validated | Normal |

---

## 5. Personas

Unchanged from v1 §3: Thesis Operator (primary); Returning researcher (secondary).

---

## 6. Information architecture

Unchanged from v1 §4. Key routes:

| Route | Surface |
|-------|---------|
| `/knowledge` | Explorer |
| `/knowledge/[conceptSlug]` | **Explain Page** (§9) |
| `/knowledge/graph` | Knowledge Graph (§10) |
| `/knowledge/authors/[authorSlug]` | Author page |
| `/sources/[sourceId]` | Source reader |
| `/research` | Research workflow (§16) |

Sidebar unchanged (ADR-0036).

---

## 7. User journeys

Unchanged from v1 §5. Journeys A–H remain valid. All journeys now reference
Knowledge Objects (§3) and lifecycle states (§4).

**Journey A** terminates on Explain Page (§9) — success metric: role understood in **60s**.

---

## 8. Knowledge Explorer

Explorer lists **concept** Knowledge Objects by default. Filters use lifecycle and
core flag (§4.4).

### 8.1 Concept card (updated)

```text
┌──────────────────────────────┐
│ [Core] Aura benjaminiana     │
│ Validato · Collegato         │  ← lifecycle badges
│ Benjamin — riproducibilità   │
│ 4 fonti · 2 capitoli         │
│ Confidenza: Alta             │
│ [ Apri ]  [ Grafo ]          │
└──────────────────────────────┘
```

### 8.2 Filters (updated)

| Filter | Options |
|--------|---------|
| Stato knowledge | Candidato · Validato · Collegato · Citato in tesi · Deprecato |
| Core | Solo core · Tutti |
| Confidenza | Alta · Media · Bassa · Non valutata |
| Capitolo / Fonte / Relazione / Decisione | (unchanged from v1) |

Default filter: **hide Deprecated**; show Candidate only if toggle "Mostra candidati".

---

## 9. Explain Page — Full Specification

The Explain Page is the **signature screen of PX-3** — the canonical view of one
**concept** Knowledge Object. Route: `/knowledge/[conceptSlug]`.

**Job to be done:** Answer in one place — *What is this concept, why does it matter
for my thesis, what evidence supports it, where is it used, and what constrains it?*

### 9.1 Success criteria

| Metric | Target |
|--------|--------|
| Time to comprehension | ≤ 60 seconds for returning operator |
| Clicks to Writing | ≤ 1 from any chapter row |
| Clicks to primary source | ≤ 2 from definition |
| Zero admin jargon | No OR IDs, no raw markdown filenames |

### 9.2 Page anatomy (regions)

```text
┌─────────────────────────────────────────────────────────────────┐
│ A  HEADER BAR                                                    │
├─────────────────────────────────────────────────────────────────┤
│ B  DEFINITION BLOCK                                              │
├──────────────────────────────┬──────────────────────────────────┤
│ C  ROLE IN THESIS            │ D  STATUS STRIP                    │
├──────────────────────────────┴──────────────────────────────────┤
│ E  RELATED CONCEPTS                                              │
├─────────────────────────────────────────────────────────────────┤
│ F  AUTHORS                                                       │
├─────────────────────────────────────────────────────────────────┤
│ G  SOURCES (evidence)                                            │
├─────────────────────────────────────────────────────────────────┤
│ H  CHAPTERS                                                      │
├─────────────────────────────────────────────────────────────────┤
│ I  DECISIONS                                                     │
├─────────────────────────────────────────────────────────────────┤
│ J  CITATIONS                                                     │
├─────────────────────────────────────────────────────────────────┤
│ K  LOCAL GRAPH (1-hop)                                           │
├─────────────────────────────────────────────────────────────────┤
│ L  ACTION BAR (sticky footer)                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Region A — Header bar

| Element | Content | Behavior |
|---------|---------|----------|
| Back | ← Knowledge | Explorer with filters restored |
| Title | Concept title | H1; truncate with tooltip if long |
| Subtitle | slug hidden; optional alias | — |
| Badges | Core · lifecycle state · confidence | From §3–§4 |
| Overflow | Unisci · Depreca · Modifica confidenza | Proposal actions |
| Quick nav | [ Grafo ] [ AI ] | Graph focus node; AI lateral panel overlay |

**Header never scrolls away** on desktop; collapses to compact on scroll (title + badges only).

### 9.4 Region B — Definition block

| Element | Rule |
|---------|------|
| Body | Canonical definition — max ~120 words visible; "Mostra tutto" expand |
| Edit | Pencil → proposal flow only — not inline save |
| Empty | "Definizione non ancora approvata" + CTA Approva proposta (Candidate) |
| Evidence footnote | "Basata su: N fonti" → scroll to Region G |

### 9.5 Region C — Role in thesis

| Element | Content |
|---------|---------|
| Prose | 2–4 sentences: why concept matters for **this** thesis |
| Phase tag | Optional: e.g. "Capitolo teorico" |
| Empty | "Ruolo non ancora descritto" + CTA Aggiungi (proposal) |

### 9.6 Region D — Status strip (horizontal)

Compact chips:

```text
Validato · Collegato · 4 fonti · 2 capitoli · 3 citazioni · Confidenza: Alta
```

Click any count → scroll to region.

### 9.7 Region E — Related concepts

Grouped by relation type (tabs or sections):

| Tab | Content | Row |
|-----|---------|-----|
| **Sostiene** | Upstream supporters | Concept chip + one-line gloss |
| **Contraddice** | Tension pairs | Amber accent |
| **Estende** | Parent/child nuance | — |
| **Correlato** | Weak ties | Muted |

Max **6 visible** per tab; "Mostra tutti (N)".

| Action | Behavior |
|--------|----------|
| Click concept | Navigate to that Explain Page |
| Hover | Preview definition tooltip |

**Empty:** "Nessuna relazione approvata" + CTA Collega concetto (proposal).

### 9.8 Region F — Authors

Distinct authors from linked sources and citations.

| Row | Content |
|-----|---------|
| Name | Link → Author page |
| Source count | N fonti |
| Top concept co-occurrence | Optional chip |

Max 5; "Mostra tutti". **Empty:** section hidden (not empty state).

### 9.9 Region G — Sources (evidence)

Ranked list — rank order §11.3 (concept→source).

| Row | Content |
|-----|---------|
| Title | Link → source reader |
| Author, year | Subtitle |
| Passage count | Annotazioni / passaggi chiave |
| Locator link | "Apri passaggio" → reader scrolled |
| Lifecycle | Source badge if Candidata/Esclusa |

Sort: Referenced first → confidence → recency.

**Empty:** "Nessuna fonte collegata" + CTA Collega fonte · Cerca nel corpus.

### 9.10 Region H — Chapters

| Row | Content |
|-----|---------|
| Chapter title | Link → Writing with section anchor |
| Status | Bozza · In revisione · Approvato |
| Usage | "Menionato in §3.2" or snippet |

**Empty:** "Non ancora usato in un capitolo" + CTA Vai a Scrittura.

### 9.11 Region I — Decisions

Decision **cards** (PX-2 pattern):

| Field | Content |
|-------|---------|
| ID | DEC-NNN secondary |
| Title | Human-readable |
| Status | Vincolante · Aperta |
| Impact | One line on this concept |

Max 3 expanded; rest collapsed. **Empty:** section hidden.

### 9.12 Region J — Citations

| Row | Formatted citation + chapter link + source link |
| Sort | Recency |
| Empty | "Nessuna citazione" + CTA Cita da fonte |

### 9.13 Region K — Local graph

Embedded 1-hop graph (§10) — max **12 nodes** visible.

| Interaction | Behavior |
|-------------|----------|
| Click node | Navigate Explain Page |
| "Apri grafo completo" | `/knowledge/graph?focus=[slug]&depth=1` |

### 9.14 Region L — Action bar (sticky)

| Action | Label | When enabled |
|--------|-------|--------------|
| Primary | Vai a Scrittura | Always (chapter picker if none linked) |
| Secondary | Spiega (AI) | Validated+ |
| Secondary | Trova fonti | Validated+ |
| Secondary | Controversie (AI) | Has contradicts edge |
| Secondary | Mostra nel grafo | Validated+ |
| Tertiary | Collega fonte | Always |

AI opens **lateral panel** — not full page; Explain Page remains visible.

### 9.15 Explain Page — responsive

| Breakpoint | Layout |
|------------|--------|
| ≥1280px | Full regions; graph inline |
| 1024–1279px | Graph below fold |
| 768–1023px | Regions stack; graph link only |
| <768px | Definition + links only; "Usa desktop per grafo" |

### 9.16 Explain Page — states

| Page state | UX |
|------------|-----|
| Candidate concept | Watermark "Candidato"; Approva prominent in header |
| Deprecated | Banner "Concetto deprecato" + link to replacement |
| Loading | Region skeletons top→bottom |
| Not found | Redirect Explorer + toast |

### 9.17 Explain Page — keyboard

| Key | Action |
|-----|--------|
| `Esc` | Back to Explorer |
| `G` | Scroll to graph region |
| `S` | Scroll to sources |
| `C` | Scroll to chapters |
| `⌘⇧S` | Spiega (AI) |

---

## 10. Knowledge Graph — Usability Specification

PX-3 graph is **navigation**, not exploration canvas (PX-5). These rules prevent
scope creep.

### 10.1 Design intent

| PX-3 Graph | PX-5 Canvas |
|----------|-------------|
| "Where am I in what I know?" | "What might I discover?" |
| Bounded, legible | Expansive, serendipitous |
| Concept nodes only | Concepts + sources + authors |

### 10.2 Initial render limits

| Parameter | Value |
|-----------|-------|
| **Default visible nodes** | **15** max |
| **Default depth** | **1-hop** from focus node (or core set if no focus) |
| **Default edges** | Only typed relations among visible nodes |
| **Initial layout** | Radiale centered on focus |

If project core set ≤ 15, show all core + 1-hop neighbors.

### 10.3 Expansion levels

Operator expands explicitly — never auto-expand beyond default.

| Level | Label (IT) | Nodes added | Confirm if total > |
|-------|------------|-------------|---------------------|
| **L0** | Solo core | Core concepts only | — |
| **L1** | +1 vicino | 1-hop (default) | 30 |
| **L2** | +2 vicini | 2-hop | 50 |
| **L3** | Tutti i validati | All Validated+ concepts | 50 |
| **L4** | Includi candidati | + Candidate | Always confirm |

**Soft limit:** 50 nodes — performance warning banner.  
**Hard limit:** 100 nodes — force filter or switch to **List view** (see §10.7).

### 10.4 Filters (graph toolbar)

| Filter | Effect |
|--------|--------|
| Stato | Validated / Linked / Referenced / Candidate |
| Core only | Toggle |
| Relation type | supports · contradicts · extends · related |
| Capitolo | Concepts linked to chapter X |
| Autore | Concepts via author's sources |
| Confidenza | Alta / Media / Bassa |
| Nascondi isolati | Remove nodes with 0 edges in view |

Filters apply live; node count badge updates.

### 10.5 Grouping modes

| Mode | Visual |
|------|--------|
| **Libero** | Force-directed (default) |
| **Per capitolo** | Clusters colored by primary chapter |
| **Per autore** | Clusters around author hub nodes (author as ghost node, not persisted) |
| **Gerarchico** | Core at center, rings by distance |
| **Radiale** | Focus node center |

Grouping affects layout only — not data.

### 10.6 Node and edge encoding

(Unchanged from v1 §8.2–8.3, plus:)

| knowledge_state | Node size |
|-----------------|-----------|
| Referenced | +20% |
| Linked | baseline |
| Validated | −10% |
| Candidate | dashed, −20% |

### 10.7 Large graph behavior (>50 nodes)

Progressive degradation — never render hairball:

1. **Banner:** "Grafo ampio — applica un filtro o passa alla lista"
2. **Focus mode:** Click node → hide non-neighbors (temporary)
3. **List view toggle:** Same data as sortable table (concept · state · degree · chapter)
4. **Search highlight:** ⌘F dims non-matching nodes to 20% opacity
5. **No L4 auto-offer** above 80 nodes

### 10.8 Interactions (complete)

| Interaction | Behavior |
|-------------|----------|
| Click | Select + preview panel |
| Double-click | Explain Page |
| Shift+click | Multi-select for compare (max 3) |
| Scroll | Zoom (clamp 0.25×–2×) |
| Drag canvas | Pan |
| Drag node | Pin; "Reimposta layout" clears pins |
| Esc | Deselect / exit focus mode |

### 10.9 Preview panel

```text
┌─────────────────────────────┐
│ [Concept title]             │
│ Validato · Collegato        │
│ One-line definition         │
│ 4 fonti · 2 capitoli        │
│ [ Apri ] [ Espandi vicini ] │
└─────────────────────────────┘
```

### 10.10 Mini-graph (Explain Page)

Same rules as §10.2 but max **12 nodes**, no expansion controls — link to full graph only.

### 10.11 Session persistence

| Persisted | Scope |
|-----------|-------|
| Expansion level | Per operator per project |
| Filter set | Session |
| Node pins | Session |
| Last focus node | Session |

---

## 11. Search — Behavior Specification

"Semantic search" means: **ranked retrieval across Knowledge Object types** using
keyword match, semantic similarity, and graph proximity — not a single LLM answer.

### 11.1 Search modes

| Mode | Trigger | Searches over |
|------|---------|---------------|
| **Unified** | Default bar input | All types — grouped results |
| **Concept** | `concept:` prefix or filter | Concept title, definition, relations |
| **Author** | `author:` prefix | Author names, variants, bios |
| **Source** | `source:` prefix | Title, metadata, body keywords |
| **Citation** | `citation:` prefix | Formatted strings, locators |
| **Chapter** | `chapter:` prefix | Chapter titles, prose (saved) |
| **Passage** | `passage:` or quotes | Source body chunks (semantic) |

Natural language without prefix → **Unified** with semantic ranking on passages + concepts.

### 11.2 Unified search flow

```text
Input (≥2 chars)
  → Debounce 200ms
  → Parallel retrieval per type
  → Rank within type (§11.3)
  → Group: Concetti · Fonti · Passaggi · Autori · Capitoli · Citazioni
  → Apply visibility: hide Deprecated default; Candidate separate section
  → Render
```

### 11.3 Ranking rules (within type)

**Concept**

1. Exact title match
2. Core flag
3. knowledge_state: Referenced > Linked > Validated > Candidate
4. Confidence: Alta > Media > Bassa
5. Semantic similarity to query
6. Recency of last visit (operator session)

**Author**

1. Exact name match
2. Variant match
3. Source count descending
4. Referenced concept count

**Source**

1. Exact title match
2. bibliography_status: Approvata > Candidata (Esclusa only if toggle)
3. knowledge_state: Referenced > Linked > Validated
4. Semantic similarity (title + body)
5. Annotation density

**Passage**

1. Semantic similarity (primary)
2. Source Approved + Referenced boost
3. Passage has annotation boost
4. Proximity to core concepts in graph (1-hop)

**Citation**

1. Exact string match
2. Linked concept match
3. Chapter order

**Chapter**

1. Title match
2. Prose keyword/semantic match
3. Status: Approvato > In revisione > Bozza

### 11.4 Cross-type unified order

When showing "Top results" (⌘K quick view — max 8):

1. Exact concept title match
2. Referenced concept
3. Passage high semantic score
4. Approvata source
5. Author exact match
6. Others by best within-type rank

Full grouped view shows **all types** — not truncated by cross-type competition.

### 11.5 Result row anatomy (by type)

**Concept:** title · lifecycle badge · definition snippet · relation hint  
**Author:** name · N fonti · top concept chips  
**Source:** title · author year · status · snippet  
**Passage:** source title · highlighted excerpt · locator  
**Citation:** formatted string · chapter · source link  
**Chapter:** title · status · matching snippet  

### 11.6 Filters (post-search)

| Filter | Applies to |
|--------|------------|
| Stato knowledge | All |
| Solo approvati | Sources |
| Solo core | Concepts |
| Capitolo | Concepts, sources, citations |
| Con annotazioni | Sources, passages |
| Confidenza | Concepts |

### 11.7 Low confidence and empty

| Case | Threshold | UX |
|------|-----------|-----|
| No results | — | Suggested core concepts; widen query hint |
| Low confidence | Top passage score < 0.5 normalized | Banner "Risultati incerti" |
| Esclusa hits | — | Separate collapsible section |

### 11.8 Search history

Last 10 queries; clears independently of Explorer Recenti.

---

## 12. Source relationships

Unchanged from v1 §10 with lifecycle badges on all source Knowledge Objects.

Source page renders full **source** envelope (§3.3) + reading experience (§13).

---

## 13. Reading experience

Unchanged from v1 §11.

---

## 14. Annotation workflow

Unchanged from v1 §12. Annotations are **annotation** Knowledge Objects; creating one
may promote source/concept to **Linked** state.

---

## 15. Citation workflow

Unchanged from v1 §13. Successful cite flow promotes entities toward **Referenced**.

---

## 16. Research workflow

Unchanged from v1 §14. Trail items are Knowledge Object references — not copies.

---

## 17. Author navigation

Unchanged from v1 §15. Author is **author** Knowledge Object type.

---

## 18. Context integration

PX-3 adds concept neighborhood to Contesto tab (PX-2). ContextBar adds live concept
count linking to Explain Page when selection overlaps concept.

---

## 19. Import and ingestion

Unchanged from v1 §17. Import creates **Candidate** source + **Candidate** concept extractions.

---

## 20. Interaction rules

v1 §18 rules KR-1…KR-10 plus:

| ID | Rule |
|----|------|
| KR-11 | Every knowledge entity exposes lifecycle state visibly |
| KR-12 | Graph never exceeds hard limit without List view fallback |
| KR-13 | Explain Page is canonical for concepts — no duplicate concept detail elsewhere |
| KR-14 | Search respects visibility; Deprecated excluded by default |

---

## 21. Navigation, keyboard, states, onboarding, desktop

Inherited from v1 §19–§23 with lifecycle badges added to all empty/loading/error tables.

---

## 22. PX-3 exclusions

Unchanged: PX-5 canvas, PX-6 validator/export, multi-project, collaboration.

---

## 23. Qualification acceptance (QWO-PX3-001)

v1 criteria plus:

| # | Criterion |
|---|-----------|
| AC-16 | Knowledge Object lifecycle visible on concept, source, annotation |
| AC-17 | Explain Page renders all regions A–L per §9 |
| AC-18 | Graph respects 15-node default and 100-node hard limit |
| AC-19 | Search modes return correctly grouped results per §11 |
| AC-20 | Validated → Linked → Referenced promotions fire on link/cite events |

---

## 24. v1 → v2 change log

| Area | v1 gap | v2 |
|------|--------|-----|
| Entity model | Implicit | §3 Knowledge Object envelope + types |
| States | Per-type labels only | §4 unified lifecycle + UX matrix |
| Explain Page | Summary section | §9 full region specification |
| Search | "Semantic" undefined | §11 modes + ranking |
| Graph | One guardrail line | §10 limits, levels, grouping, large-graph |
| Cards/filters | Stato concetto | lifecycle + confidence |

---

## 25. Governance references

| Artifact | Role |
|----------|------|
| ADR-0037 | Concept-centric model |
| `px2-research-workspace-experience-v2.md` | Workspace boundary (frozen) |
| `px3-knowledge-experience-v1.md` | Prior draft (superseded) |

---

## WO-TRACE

```text
px3-knowledge-experience-v1.md
  → Head of Product review → v2 (this document)
  → UX design → Engineering
```
