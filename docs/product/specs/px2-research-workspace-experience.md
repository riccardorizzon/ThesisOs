# PX-2 — Research Workspace Experience

> **Product Specification v1** · Product Architect · 2026-07-04  
> **Superseded by:** [`px2-research-workspace-experience-v2.md`](px2-research-workspace-experience-v2.md) — use v2 for Engineering  
> **Status:** SUPERSEDED  
> **Does not amend:** Product Constitution v1.0, ADR-0034…0041, META-1

---

## 0. Document purpose

This specification defines the **complete user experience** for PX-2 — the first milestone
where the operator **works** in ThesisOS, not only navigates foundation shells.

Engineering derives EWOs from **capabilities** (PX-2.1…PX-2.5), not from individual
screens. Every section ends with **acceptance criteria** Engineering can verify in
qualification (QWO-PX2-001).

**In scope:** PX-2 Research Workspace Experience  
**Out of scope:** PX-3 full source ingestion, PX-4 knowledge graph, PX-5 research canvas,
PX-6 polish, ASEP framework changes, runtime graph redesign

---

## 1. Product thesis (PX-2)

The Research Workspace is where **reading, writing, citing, reviewing, and deciding**
happen in one continuous flow. The operator never rebuilds context manually; the
Context Engine assembles it. AI sits **lateral** — like Copilot beside code — never
central.

```text
         Knowledge Engine (invisible)
                    │
    ┌───────────────┴───────────────┐
    │     Research Workspace        │
    │  read · write · cite · review │
    └───────────────┬───────────────┘
                    │
              Operator focus
         (content center, AI right)
```

**Design north stars:** Cursor (contextual AI), Linear (speed + status), Notion
(hierarchy), Arc (session continuity), Figma (inspect without leaving canvas).

---

## 2. Capabilities map

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-2.1** | Context Awareness | Binding decisions, corpus constraints, and active scope visible while working |
| **PX-2.2** | Writing Flow | Draft and revise chapter text in a focused, autosaved flow |
| **PX-2.3** | Source Interaction | Read corpus sources, cite into text, connect sources to active chapter |
| **PX-2.4** | Decision Visibility | See how project decisions constrain current work — no admin surfaces |
| **PX-2.5** | Session Continuity | Resume across sessions with preserved scope, scroll, and progress |

PX-2 **activates** PX-1 shells (Writing three-panel, Sources list, ContextBar, Review
shell, Home Continua). It does not reopen PX-1 layout contracts.

---

## 3. Personas and primary journeys

### 3.1 Persona — Thesis Operator (primary)

Academic researcher writing a governed thesis. Italian UI copy; English nav labels
(ADR-0036). Expects Scrivener-class structure with AI assistance, not a chatbot.

### 3.2 Journey A — Continue writing (daily loop)

```text
Open ThesisOS
  → Home shows progress + "Continua"
  → Lands in Writing / last chapter / last section anchor
  → ContextBar shows live scope counts
  → Writes in editor (autosave)
  → Selects paragraph → AI panel offers Rewrite / Verify / Find sources
  → Accepts AI suggestion as proposal (not silent write)
  → Ends session → Session Close bundles proposals
  → Approves bundle → returns to Home with updated progress
```

**Success:** Operator reaches productive writing within **90 seconds** of open.

### 3.3 Journey B — Read source, cite in chapter

```text
Writing / chapter open
  → Cmd+Shift+S or "Cita fonte" → Source picker (corpus-scoped)
  → Select source → Peek Reader opens (split or overlay)
  → Highlight passage → "Inserisci citazione"
  → Citation marker inserted at cursor; ContextBar citation count updates
  → Peek dismiss → return to editor with selection preserved
```

**Success:** Source used in next paragraph without leaving Writing route.

### 3.4 Journey C — Review AI revision

```text
Home → Revisione OR Writing → Review action
  → Review workspace: select chapter/section
  → Compare original vs proposed revision (side-by-side)
  → Accept section / Reject / Edit manually
  → Accepted changes persist as chapter draft (operator-approved)
```

**Success:** Operator can accept or reject revisions without `/ai` power mode.

### 3.5 Journey D — Understand a binding decision

```text
Writing / selection conflicts with known decision
  → ContextBar shows decision indicator (amber)
  → Opens Decision Inspector (panel tab)
  → Reads human-readable decision summary + scope
  → Returns to writing with constraint understood
  → Optional: "Chiedi al revisore" AI action uses decision in packet
```

**Success:** No navigation to Settings or raw Decisions.md.

### 3.6 Journey E — Explore corpus for research (PX-2 lightweight)

```text
Home → Ricerca OR Sources with search focused
  → Search corpus by title, author, concept tag (stub tags until PX-4)
  → Open source in reader
  → "Collega al capitolo" → pick active chapter
  → Return to Writing; source appears in chapter's linked sources
```

**Success:** Research-to-writing loop without PX-5 graph.

---

## 4. Information architecture (PX-2 delta)

Frozen IA (ADR-0036) unchanged. PX-2 adds **workspace behaviors** within existing routes.

### 4.1 Route responsibilities (PX-2 activation)

| Route | PX-1 shell | PX-2 activation |
|-------|------------|-----------------|
| `/` | Home stub | Live progress, Continua deep link, pending proposals |
| `/writing`, `/writing/[chapterId]` | Three-panel shell | Editor, autosave, AI actions, peek reader, Decision Inspector tab |
| `/sources`, `/sources/[sourceId]` | Card grid stub | Reader, search, link-to-chapter (read-only corpus) |
| `/review` | Review shell | Diff compare, accept/reject flow |
| `/knowledge`, `/research` | Stubs | Cross-links only; no PX-4/PX-5 activation |
| `/ai` | Power mode | Unchanged; not default path |

### 4.2 Screen hierarchy

```text
AppShell (sidebar + top chrome)
├── Global: Project name · ContextBar · Session indicator · Command palette (⌘K)
├── Home
├── Research Workspace cluster
│   ├── Writing (primary workspace)
│   ├── Sources (corpus browser)
│   └── Review (revision mode)
├── Knowledge (stub links)
├── Research (stub links)
├── AI (power mode)
└── Settings
```

### 4.3 Writing workspace — three-panel contract (frozen)

```text
┌──────────┬────────────────────────────┬──────────────────┐
│ Outline  │ Editor (center, focus)     │ Right rail       │
│ tree     │ Markdown · autosave        │ AI | Inspect |   │
│          │                            │ Source peek      │
│ 240px    │ flex-1 min 480px           │ 320px            │
└──────────┴────────────────────────────┴──────────────────┘
         ContextBar — full width above panels
```

**Right rail modes** (single slot, tabbed — not four simultaneous panels):

| Tab | Purpose | PX-2 |
|-----|---------|------|
| **AI** | Contextual actions (default) | Active |
| **Contesto** | Context Inspector — decisions, constraints, definitions | Active |
| **Fonte** | Peek Source Reader when source open | Active |
| **Revisione** | Inline revision queue for current chapter | Active |

Default tab: **AI**. Switching tabs preserves editor selection and scroll.

---

## 5. Navigation

### 5.1 Primary navigation (sidebar)

Frozen per ADR-0036. PX-2 adds **badges**:

| Item | Badge |
|------|-------|
| Home | Pending proposals count (if > 0) |
| Writing | Active chapter status dot |
| Sources | — |
| Review | Pending revisions count (if > 0) |

### 5.2 Workspace navigation (in-flow)

| Mechanism | Behavior |
|-----------|----------|
| **Continua** (Home) | Deep link → `/writing/[lastChapterId]#section-anchor` |
| **Outline click** | Switch chapter; confirm if unsaved (see §15) |
| **Breadcrumb** | `Writing / Cap. 3 — Metodologia / §3.2` — click chapter opens outline focus |
| **Source peek back** | Returns to prior right-rail tab (usually AI) |
| **Cross-module link** | Sources → "Apri in Writing" preserves chapter context in URL state |
| **Command palette (⌘K)** | Jump to chapter, source, action, route |

### 5.3 URL state (session restorable)

Query or hash carries restorable scope:

```text
/writing/cap-03-metodologia?section=3.2&source=src-benjamin-1936&panel=fonte
```

Operator bookmarking or Continua restores panel mode and peeked source where possible.

---

## 6. Workspace organization

### 6.1 Project scope

Single active project in PX-2 (multi-project UX deferred PX-6). Project name in
AppShell header; all modules scoped implicitly.

### 6.2 Active scope model

The workspace always knows **where the operator is working**:

| Scope layer | Example | Surfaced in |
|-------------|---------|-------------|
| Project | STIGMATA thesis | AppShell |
| Module | Writing | Sidebar highlight |
| Entity | Chapter 3 | Breadcrumb, outline |
| Section | §3.2 | Editor scroll anchor |
| Selection | Paragraph text | AI actions, Context packet |
| Peek entity | Source Benjamin 1936 | Right rail Fonte tab |

### 6.3 Outline organization

| Element | Behavior |
|---------|----------|
| Tree | Parts → Chapters → Sections (from outline metadata) |
| Status badge | `Bozza` · `In revisione` · `Approvato` (maps ADR-0040 factors) |
| Progress mini | Section completion indicator (deterministic: word count threshold or manual checkbox — operator toggle in section header) |
| Drag reorder | PX-6; PX-2 read-only order |
| Filter | Show all / in progress / needs review |

### 6.4 Activity and proposals (Home + chrome)

Pending items appear as **action cards**, not protocol jargon:

| Engine concept | Operator copy |
|----------------|---------------|
| Memory proposal | "Aggiornamento proposto: …" |
| Frozen decision conflict | "Attenzione: decisione vincolante" |
| Bibliography candidata | "Nuova fonte da approvare" |
| Session bundle | "Chiudi sessione — N modifiche in sospeso" |

---

## 7. Writing workflow

### 7.1 Editor behavior

| Rule | Specification |
|------|---------------|
| Format | Markdown authoring; rendered preview toggle (optional split) |
| Focus | Editor is default focus on enter Writing route |
| Autosave | Debounced save every 3s after edit; explicit save on blur |
| Save indicator | `Salvato` · `Salvataggio…` · `Non salvato` in editor chrome |
| Selection | Persists across right-rail tab switches |
| Section anchors | Headings define navigable sections in outline |
| Word count | Section + chapter counts in editor footer (deterministic) |

### 7.2 Chapter lifecycle (operator-visible)

```text
Bozza → In revisione → Approvato
```

| Transition | Trigger |
|------------|---------|
| → In revisione | Operator marks ready OR AI Review completes |
| → Approvato | Operator explicit approve (Review or outline context menu) |
| ← Bozza | Operator demote (confirm dialog) |

Progress ring uses ADR-0040 formula; status changes update Home immediately.

### 7.3 AI writing actions (lateral panel)

Contextual catalog per ADR-0039. PX-2 activates:

| Action | Label (IT) | Requires |
|--------|------------|----------|
| rewrite | Riscrivi | Selection |
| deepen | Approfondisci | Selection |
| verify | Verifica | Selection or chapter |
| find_sources | Trova fonti | Selection or chapter |
| summarize | Riassumi | Selection |
| draft_section | Bozza sezione | Section scope |
| outline_check | Controlla struttura | Chapter |
| review | Revisione | Chapter |

Actions stream into panel; results offer **Applica** (opens proposal flow) not direct mutation.

### 7.4 Citation workflow

```text
1. Operator triggers "Cita" (toolbar or ⌘⇧C)
2. Source Picker modal — search corpus, recently used, chapter-linked
3. Optional: open peek reader to confirm passage
4. Insert citation token at cursor: [@AuthorYear] or project citation format
5. ContextBar citation count increments
6. Citation appears in chapter's citation list (sidebar footer collapsible)
```

No silent bibliography writes — candidata flow if source not yet approved (PX-3
deepens; PX-2 surfaces approval prompt).

---

## 8. Review workflow

Review is a **mode**, not a separate product. Entry points:

| Entry | Destination |
|-------|-------------|
| Home → Revisione | `/review` |
| Writing → AI → Revisione | `/review?chapter=[id]` or inline right-rail Revisione tab |
| Outline → context menu → Invia in revisione | Status → In revisione |

### 8.1 Review workspace layout

```text
┌─────────────────────────────────────────────────────────┐
│ Selector: Capitolo / Sezione                            │
├──────────────────────┬──────────────────────────────────┤
│ Originale            │ Proposta                         │
│ (read-only snapshot) │ (AI or manual revision)          │
├──────────────────────┴──────────────────────────────────┤
│ [ Accetta ] [ Accetta parziale ] [ Rifiuta ] [ Modifica ]│
└─────────────────────────────────────────────────────────┘
```

### 8.2 Review rules

| Rule | Behavior |
|------|----------|
| Compare source | Left = last saved chapter; Right = pending revision |
| Partial accept | Operator selects hunks (paragraph granularity) |
| Reject | Discards proposal; no chapter change |
| Accept | Writes chapter; status remains or advances per operator choice |
| AI revision | Uses Context Packet + OR-6 path; labeled "Proposta AI" |
| History | Last 5 revisions listed (timestamp + source); restore opens compare |

---

## 9. Research workflow (PX-2 lightweight)

Full Research canvas is PX-5. PX-2 delivers **corpus exploration** supporting writing:

| Activity | Surface |
|----------|---------|
| Search corpus | Sources module search bar; ⌘K "Cerca fonte" |
| Filter by status | candidata / approvata / esclusa (existing stub) |
| Read | Source reader (Sources route or Writing peek) |
| Link to chapter | Source detail → "Collega al capitolo attivo" |
| Concept tag browse | Read-only tag chips on sources (until PX-4 graph) |
| Return to writing | Sticky "Torna a Scrittura" chip when chapter context in URL |

**Research quick action (Home):** opens Sources with search focused and chapter
context preserved if coming from Writing.

---

## 10. Source interaction

### 10.1 Source reader

| Element | Specification |
|---------|---------------|
| Layout | Title, metadata strip, readable body (markdown/PDF render) |
| Navigation | Prev/Next in search results |
| Annotations | Highlight + note (local until PX-3 sync) — PX-2: highlight + copy quote |
| Link actions | Cita · Collega capitolo · Apri in Writing |
| Excluded sources | Visible in list with `Esclusa` badge; reader shows exclusion reason; cite blocked |

### 10.2 Source picker (modal)

Triggered from Writing cite flow and AI "Trova fonti" results.

| Column | Content |
|--------|---------|
| Search | Title, author, year |
| Recent | Last 10 used in project |
| Linked | Sources linked to active chapter |
| Results | Corpus retrieval ranked; excluded sources omitted |

### 10.3 Source ↔ chapter linking

Operator links source to chapter; link visible in:

- Chapter editor footer "Fonti collegate"
- ContextBar source count
- Source detail "Usata in"

Removing link requires confirm.

---

## 11. Context interaction

### 11.1 ContextBar (live)

Persistent below AppShell header on Writing, Sources (when chapter context), Review.

```text
[ Cap. 3 · §3.2 ]  12 fonti · 4 decisioni · 18 voci contesto · 34 citazioni  [ⓘ]
```

| Segment | Click behavior |
|---------|----------------|
| Scope chip | Opens outline section |
| Counts | Opens Context Inspector (Contesto tab) |
| ⓘ | Tooltip: plain-language summary of what AI sees |
| Warning state | Amber bar if binding decision affects selection |

Counts reflect **Context Packet** assembly, not static stubs.

### 11.2 Context Inspector (Contesto tab)

Human-readable breakdown:

| Section | Content |
|---------|---------|
| Ambito | Chapter, section, selection snippet |
| Decisioni vincolanti | Top 3 relevant; link to Decision cards |
| Vincoli corpus | Exclusion rules affecting retrieval |
| Definizioni | Terminology matches for selection |
| Fonti rilevanti | Retrieved sources list → open peek |
| Regole di scrittura | Active writing rules (collapsed by default) |

No raw JSON, no OR gate names.

### 11.3 Context refresh rules

| Event | Context refresh |
|-------|-----------------|
| Chapter switch | Full rebuild |
| Selection change | Debounced 300ms |
| Source link change | Full rebuild |
| Decision approve (session) | Full rebuild + toast |
| Autosave | No refresh unless entity metadata changed |

---

## 12. Decision visibility

### 12.1 Decision surfaces

| Surface | What operator sees |
|---------|-------------------|
| ContextBar | Count + warning indicator |
| Context Inspector | Decision cards with title, status (Vincolante / Aperta), 2-line summary |
| Inline editor marker | Optional gutter icon on paragraphs touching frozen decisions |
| AI panel banner | When action may conflict: "Questa azione rispetta DEC-…" or "Conflitto possibile" |

### 12.2 Decision card

```text
┌─────────────────────────────────────┐
│ DEC-012 · Vincolante                │
│ Benjamin: aura vs riproducibilità   │
│ Influenza: Cap. 2, Cap. 3           │
│ [ Leggi ] [ Chiedi al revisore ]    │
└─────────────────────────────────────┘
```

| Action | Behavior |
|--------|----------|
| Leggi | Expands full operator-facing summary (not raw markdown file) |
| Chiedi al revisore | AI action with decision in packet |
| Modifica | **Blocked** for Vincolante — explain in modal (OR-5) |

### 12.3 Non-goals (PX-2)

- Decision authoring UI (Settings/blueprint path)
- Reopening frozen decisions from product UI

---

## 13. Memory visibility

Memory protocol stays invisible; **proposals** are visible.

| State | UX |
|-------|-----|
| Pending proposals | Home card + AppShell badge |
| Proposal detail | Modal: what will change, affected artifacts, approve/reject |
| Session close bundle | Single modal listing all pending items — atomic accept/reject (OR-7) |
| Approved | Activity feed entry: "Decisione aggiornata" / "Memoria aggiornata" |
| No silent writes | Any AI "Applica" → proposal queue, not immediate persist |

Operator never sees "Permanent/Ephemeral/Working" tier names — use:

| Tier (internal) | Operator copy |
|-----------------|---------------|
| Working | "Bozza di sessione" |
| Ephemeral | "Nota temporanea" |
| Permanent proposal | "Modifica proposta" |

---

## 14. Session continuity

### 14.1 Persisted session state

| Field | Restored on Continua |
|-------|----------------------|
| Last route | Writing preferred if recent activity was writing |
| Chapter + section | Yes |
| Scroll position | Editor + reader |
| Right rail tab | Last active tab |
| Peeked source | If was open |
| Selection | Optional restore if within 24h |
| Unsaved edits | Autosave recovers; prompt if conflict |

### 14.2 Session indicator

AppShell trailing: `Sessione · 2h 14m · 3 proposte in sospeso`

| Action | Behavior |
|--------|----------|
| Chiudi sessione | Opens OR-7 bundle modal |
| Resume later | Implicit — state persisted on navigation away |

### 14.3 Multi-tab policy

Last-write-wins with conflict detection on chapter save. Second tab shows:
"Capitolo modificato altrove — Ricarica / Sovrascrivi con questa scheda"

---

## 15. Interaction rules

### 15.1 Global rules

| ID | Rule |
|----|------|
| IR-1 | Content center, AI lateral — never full-screen AI on standard actions |
| IR-2 | No silent permanent writes from AI |
| IR-3 | Binding decisions always in Context Packet for AI actions |
| IR-4 | Excluded corpus sources never citable |
| IR-5 | Operator language: Italian; nav labels: English |
| IR-6 | Deterministic progress — never LLM-estimated |
| IR-7 | Destructive actions require confirm |
| IR-8 | Focus returns to editor after dismissing peek reader |

### 15.2 Unsaved changes

| Scenario | Behavior |
|----------|----------|
| Switch chapter | Save autosave; if failing, blocking dialog |
| Leave Writing | Autosave; badge if pending |
| Close browser | Autosave best-effort |

### 15.3 Proposal apply flow

```text
AI result → Anteprima → Applica
  → Adds to proposal queue (not immediate)
  → Operator reviews in Session Close or Proposals panel
  → Approve → persist + activity log
```

### 15.4 Selection-aware AI

Empty selection → chapter-scoped actions.  
Selection → selection-scoped actions.  
Action buttons disabled with tooltip when preconditions missing.

---

## 16. Keyboard shortcuts (desktop-first)

| Shortcut | Action |
|----------|--------|
| `⌘K` | Command palette |
| `⌘⇧P` | Command palette (alias) |
| `⌘\` | Toggle outline panel |
| `⌘⇧\` | Toggle right rail |
| `⌘1…9` | Right rail tab: AI / Contesto / Fonte / Revisione |
| `⌘S` | Force save |
| `⌘⇧C` | Cite source |
| `⌘⇧F` | Find in chapter |
| `⌘⇧R` | Start review for current chapter |
| `⌘Enter` | Apply focused AI suggestion (opens proposal) |
| `Esc` | Close modal / dismiss peek / clear selection |
| `⌘↑/↓` | Previous/next section in outline |
| `G then W` | Go to Writing (Linear-style chord) |
| `G then S` | Go to Sources |
| `G then H` | Go to Home |

All shortcuts shown in command palette discoverability list. Shortcuts do not override
browser defaults without `preventDefault` on focused workspace.

---

## 17. Empty states

| Surface | Empty state | CTA |
|---------|-------------|-----|
| Home activity | "Nessuna attività recente" | Continua / Scrittura |
| Outline | "Nessun capitolo" | Importa outline (Settings) |
| Editor | "Inizia a scrivere §1" | Template paragraph optional |
| AI panel (no selection) | "Seleziona un passaggio o usa un'azione di capitolo" | Action list |
| Source picker | "Nessuna fonte trovata" | Modifica ricerca / Sources |
| Chapter linked sources | "Nessuna fonte collegata" | Cita fonte |
| Review | "Nessuna revisione in sospeso" | Avvia revisione |
| Context Inspector | "Contesto minimo — seleziona testo per arricchire" | — |
| Proposals | "Nessuna proposta in sospeso" | — |

Tone: inviting, not apologetic. No illustration required PX-2; use Lucide icon + copy.

---

## 18. Loading states

| Surface | Pattern |
|---------|---------|
| App initial load | AppShell skeleton; sidebar immediate from cache |
| ContextBar | Skeleton chips → populate within 500ms target |
| Editor chapter | Skeleton lines; fade in content |
| Autosave | Inline `Salvataggio…` non-blocking |
| AI action | Streaming tokens in panel; cancel button |
| Source reader | Progress bar top; stagger metadata then body |
| Source picker search | Debounced 200ms; inline spinner in field |
| Review diff | Side-by-side skeleton → content |
| Home progress ring | Animate from 0 to value on first load only |

Never block editor typing while context loads — editor interactive; ContextBar pending.

---

## 19. Error states

| Error | Operator message | Recovery |
|-------|------------------|----------|
| Save failed | "Impossibile salvare. Riprova." | Retry button; local draft preserved |
| Context assembly failed | "Contesto non disponibile" | Retry; AI actions disabled with explanation |
| AI action failed | "Azione non completata" | Retry; copy error id for support (collapsed) |
| Source not found | "Fonte non trovata o esclusa" | Back to picker |
| Citation blocked (excluded) | "Fonte esclusa dal corpus" | Link to exclusion reason |
| Conflict (multi-tab) | "Conflitto di versione" | Ricarica / Sovrascrivi |
| Network offline | "Sei offline — modifiche salvate localmente" | Banner; queue sync on reconnect |
| Frozen decision edit | "Decisione vincolante — non modificabile" | Dismiss |
| Session bundle partial | "Accetta o rifiuta tutte le proposte insieme" | OR-7 atomicity |

Errors never expose stack traces, OR IDs, or protocol names in primary copy.

---

## 20. Onboarding (PX-2 first-run)

PX-2 delivers **contextual onboarding**, not a marketing tour.

### 20.1 First open after PX-2

| Step | Format |
|------|--------|
| 1 | Home: single coach mark on **Continua** — "Riprendi da dove hai lasciato" |
| 2 | Writing: coach mark on three panels — outline / editor / AI |
| 3 | ContextBar: "L'AI vede questo contesto automaticamente" |
| 4 | Dismiss forever stored per operator |

### 20.2 Just-in-time hints

| Trigger | Hint |
|---------|------|
| First selection | "Seleziona testo per azioni AI" |
| First cite | Walkthrough cite flow (3 steps max) |
| First session close | Explain proposal bundle |
| First binding decision warning | Explain Decision Inspector |

No forced modal chain > 3 steps. Skip always visible.

---

## 21. Desktop-first behavior

### 21.1 Breakpoints

| Breakpoint | Layout |
|------------|--------|
| ≥1280px | Full three-panel Writing; ContextBar inline |
| 1024–1279px | Outline collapsible icon rail; right rail 280px |
| 768–1023px | Outline drawer; single right rail overlay |
| <768px | Read-only preview PX-2; banner "Usa desktop per scrivere" |

Primary target: **1440×900** and **1920×1080**.

### 21.2 Panel collapse

| Panel | Collapse |
|-------|----------|
| Outline | `⌘\` toggles; state persisted |
| Right rail | `⌘⇧\` toggles; editor expands |
| Sidebar | Collapse to icons (PX-1 behavior) |

### 21.3 Pointer and density

- Linear-like row height 36px outline items
- Hover: color transition only — no layout shift
- Click targets ≥ 44px touch equivalent on interactive chrome

---

## 22. Copy and localization

| Context | Language |
|---------|----------|
| Navigation labels | English (Home, Writing, Sources, …) |
| Operator content | Italian |
| AI action labels | Italian |
| Error/toast | Italian |
| Decision IDs | Visible but secondary (DEC-012), not headline |

---

## 23. PX-2 exclusions (explicit)

| Deferred | Milestone |
|----------|-----------|
| Full source import / PDF parse | PX-3 |
| Annotation sync to backend | PX-3 |
| Concept graph / Explain panel | PX-4 |
| Research canvas | PX-5 |
| Citation validator (W-06) | PX-6 |
| Multi-project switcher | PX-6 |
| Outline drag reorder | PX-6 |
| Separate Reviewer/Planner agents | PX-6 / ADR supersession |

---

## 24. Qualification acceptance (QWO-PX2-001 draft)

Engineering must demonstrate on live stack:

| # | Criterion |
|---|-----------|
| AC-1 | **PX-2.1** ContextBar live counts match Context Packet for active chapter + selection |
| AC-2 | **PX-2.1** Binding decision appears in Inspector when retrieval would contradict |
| AC-3 | **PX-2.2** Editor autosave + chapter switch without data loss |
| AC-4 | **PX-2.2** At least 4 AI actions execute with streaming from Writing panel |
| AC-5 | **PX-2.2** AI apply creates proposal — not silent chapter write |
| AC-6 | **PX-2.3** Source picker → peek reader → cite inserts marker |
| AC-7 | **PX-2.3** Excluded source cite attempt blocked with operator message |
| AC-8 | **PX-2.4** Decision card readable; frozen decision edit blocked |
| AC-9 | **PX-2.5** Continua restores chapter, section, and panel tab |
| AC-10 | **PX-2.5** Session close presents atomic proposal bundle |
| AC-11 | Review accept/reject changes chapter with operator confirm |
| AC-12 | Home progress updates on chapter status change (deterministic) |
| AC-13 | OR-1…OR-7 regression green; PX-1 qualification surfaces unchanged |
| AC-14 | `make ci` green |

---

## 25. EWO decomposition (recommended)

Non-binding until program review. Maps capabilities → delivery slices:

| EWO | Capability | Deliverable theme |
|-----|------------|-------------------|
| PX2-EWO-001 | PX-2.1 | ContextBar live + Context Inspector |
| PX2-EWO-002 | PX-2.2 | Editor, autosave, chapter lifecycle |
| PX2-EWO-003 | PX-2.2 | AI panel actions + proposal queue |
| PX2-EWO-004 | PX-2.3 | Source reader, picker, peek, cite |
| PX2-EWO-005 | PX-2.4 | Decision cards + warnings |
| PX2-EWO-006 | PX-2.5 | Session persistence + Continua |
| PX2-EWO-007 | PX-2.2/3 | Review workspace activation |
| PX2-EWO-008 | All | Command palette, shortcuts, states |

---

## 26. Governance references

| Artifact | Role |
|----------|------|
| `docs/product/EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md` | Authorization gate |
| `docs/product/specs/thesisos-product-ux-v1.md` | Baseline IA + modules |
| ADR-0036 | Information architecture |
| ADR-0038 | Context Engine |
| ADR-0039 | AI interaction model |
| ADR-0040 | Product state |
| `design-system/thesisos/MASTER.md` | Visual patterns |
| `docs/product/design-system-v1.md` | Frozen tokens |

Amendments to IA or three-panel contract require Product Constitution P8 — not this spec.

---

## WO-TRACE

```text
PX-1 COMPLETE → EXECUTION-AUTHORIZATION-PX2-AMENDMENT → px2-research-workspace-experience.md
  → Architect Program Review → PX2-EWO-* → QWO-PX2-001
```
