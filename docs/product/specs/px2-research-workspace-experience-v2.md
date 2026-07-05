# PX-2 — Research Workspace Experience

> **Product Specification v2** · Head of Product review · 2026-07-04  
> **Supersedes:** `px2-research-workspace-experience.md` (v1)  
> **Status:** PROPOSED — pending Execution Authorization Amendment ratification  
> **Does not amend:** Product Constitution v1.0, ADR-0034…0041, META-1

---

## 0. Document purpose

This specification is **self-contained** for Engineering: every workflow, state,
interaction, and edge case needed to build PX-2 without product clarification
questions.

**v2 changes (Head of Product review):** fixed inconsistencies (shortcuts, tab
mapping, Review vs Revisione), added missing workflows (first launch, proposal
inbox, candidata, AI cancel, default routes), unified proposal model, W-06
operator messaging, modal/toast catalog, command palette inventory, focus rules,
disabled/stale states, and §30 Edge-case register.

**In scope:** PX-2.1…PX-2.5  
**Out of scope:** PX-3 ingestion, PX-4 graph, PX-5 canvas, PX-6 polish, ASEP changes

---

## 1. Product thesis

The Research Workspace is where **reading, writing, citing, reviewing, and deciding**
happen in one continuous flow. Context is assembled automatically; AI is lateral.

**Design north stars:** Cursor (contextual AI), Linear (speed + status), Notion
(hierarchy), Arc (session continuity), Figma (inspect beside canvas).

**Simplification principle (v2):** One **proposal inbox** for all pending changes.
One **Review route** for all compare/accept flows. Right rail **Revisione tab** is
a queue pointer — not a second diff UI.

---

## 2. Capabilities map

| ID | Capability | Operator outcome |
|----|------------|------------------|
| **PX-2.1** | Context Awareness | Binding decisions, corpus constraints, active scope visible while working |
| **PX-2.2** | Writing Flow | Draft and revise chapter text in focused, autosaved flow |
| **PX-2.3** | Source Interaction | Read corpus sources, cite into text, connect sources to active chapter |
| **PX-2.4** | Decision Visibility | See how decisions constrain work — no admin surfaces |
| **PX-2.5** | Session Continuity | Resume across sessions with preserved scope and progress |

---

## 3. Personas

### 3.1 Thesis Operator (primary)

Academic researcher. Italian UI copy; English nav labels (ADR-0036). Expects
Scrivener-class structure with AI assistance — not a chatbot.

### 3.2 Implicit constraints

- Single operator, single active project (PX-2)
- Desktop primary; mobile read-only
- Qualified runtime v1.0 underneath; W-06 citation limitation acknowledged (§29)

---

## 4. User journeys (complete)

### 4.1 Journey A — Daily writing loop

```text
Open → Home (progress + Continua)
  → Writing / last chapter / section anchor
  → ContextBar live
  → Edit (autosave) → select text → AI action → stream → Anteprima → Applica
  → Proposal added to inbox (badge)
  → Optional: approve now OR Chiudi sessione later
  → Approve bundle → Home progress updates
```

**Success:** Productive writing within **90 seconds** of open.

### 4.2 Journey B — Cite from corpus

```text
Writing → Cita (⌘⇧C) → Source Picker
  → Select source → [optional] Apri anteprima → Peek Reader (Fonte tab)
  → Seleziona passaggio → Inserisci citazione
  → Marker at cursor; inbox unchanged unless candidata approval needed
  → Esc or Chiudi anteprima → focus returns to editor, selection preserved
```

**Success:** Source cited without leaving `/writing`.

### 4.3 Journey C — Review AI revision

```text
Writing → AI → Revisione (chapter scope)
  → Proposal queued + Revisione tab badge
  → Apri in Review → /review?chapter=[id]
  → Side-by-side compare → Accetta parziale / Accetta / Rifiuta
  → Chapter updates on accept; status unchanged unless operator promotes
```

**Success:** Compare/accept without `/ai` power mode.

### 4.4 Journey D — Binding decision conflict

```text
ContextBar amber → Contesto tab → Decision card
  → Leggi summary → [optional] Chiedi al revisore
  → Continue writing informed; no Settings navigation
```

### 4.5 Journey E — Corpus exploration

```text
Home → Ricerca → /sources?focus=search&chapter=[ctx]
  → Search → open reader → Collega al capitolo
  → Torna a Scrittura → linked source in chapter footer
```

### 4.6 Journey F — First launch (no prior session) **(v2)**

```text
Open → Home with progress 0% or bootstrap value
  → Continua disabled OR links to first outline chapter
  → Coach marks (§27) → Writing first chapter
  → Empty editor state with §1 placeholder
```

### 4.7 Journey G — Approve candidata source **(v2)**

```text
Cite unapproved source → modal: "Fonte candidata — approvare per citazione?"
  → Approva → adds bibliography proposal to inbox
  → Cannot insert citation until approved (or operator cancels)
  → After approve: retry cite flow
```

### 4.8 Journey H — Import document (PX-2 stub) **(v2)**

```text
Home → Importa documento → /documents/upload (existing route)
  → Banner: "Importazione completa in arrivo (PX-3). File accettato in coda."
  → Return to Home; no workspace block
```

### 4.9 Journey I — Power mode handoff **(v2)**

```text
Writing → "Apri in AI" (footer link) → /ai?chapter=[id]&selection=[hash]
  → Full chat with same ContextPacket
  → "Torna a Scrittura" restores chapter + section; AI thread not merged into chapter
```

---

## 5. Information architecture

Frozen IA (ADR-0036). PX-2 activates behavior within routes.

| Route | PX-2 activation |
|-------|-----------------|
| `/` | Live progress, Continua, proposal inbox preview |
| `/writing`, `/writing/[chapterId]` | Full workspace (§6) |
| `/sources`, `/sources/[sourceId]` | Search, reader, link-to-chapter |
| `/review` | Compare/accept (sole diff UI) |
| `/knowledge`, `/research` | Stub: banner + link to Sources/Writing |
| `/ai` | Power mode; handoff from Writing (§4.9) |
| `/documents/upload` | Import stub (§4.8) |

### 5.1 Default routes

| URL | Redirect / default |
|-----|-------------------|
| `/writing` | → `/writing/[first-in-progress chapter]` else → `[first chapter in outline]` |
| `/writing/[invalidId]` | Toast + redirect to default chapter |
| `/sources/[invalidId]` | Toast + `/sources` |
| `/review` (no query) | Selector empty state; list chapters **In revisione** or with pending revision proposals |

### 5.2 Research / Knowledge stubs (v2)

Clicking **Research** or **Knowledge** in sidebar:

```text
┌────────────────────────────────────────────┐
│  [module] — disponibile prossimamente      │
│  Esplora fonti in Sources · Scrivi in Writing │
│  [ Vai a Sources ]  [ Vai a Writing ]      │
└────────────────────────────────────────────┘
```

No broken routes. No empty canvas.

---

## 6. Writing workspace layout

```text
┌──────────┬────────────────────────────┬──────────────────┐
│ Outline  │ Editor (center, focus)     │ Right rail       │
│ 240px    │ flex-1 min 480px         │ 320px            │
└──────────┴────────────────────────────┴──────────────────┘
         ContextBar — full width above panels
```

### 6.1 Right rail tabs (single slot)

| Tab | Key | Purpose |
|-----|-----|---------|
| **AI** | `⌘1` | Contextual actions (default) |
| **Contesto** | `⌘2` | Context Inspector |
| **Fonte** | `⌘3` | Peek Source Reader (auto-opens on peek) |
| **Revisione** | `⌘4` | Pending revision queue → opens `/review` |

**v2 simplification:** Revisione tab does **not** host a second diff viewer. It lists
pending revision proposals with **[ Apri in Review ]** per item.

**Tab auto-switch rules:**

| Event | Tab behavior |
|-------|--------------|
| Open source peek | Switch to Fonte; remember prior tab |
| Close peek (Esc) | Restore prior tab; focus editor |
| AI action starts | Stay on AI (or switch to AI if elsewhere) |
| Revision proposal created | Revisione badge +1; stay on current tab |
| ContextBar warning click | Switch to Contesto |

### 6.2 ContextBar visibility

| Route | ContextBar |
|-------|------------|
| `/writing/*` | Always live |
| `/sources/*` | Shown if `?chapter=` in URL; else minimal ("Nessun capitolo attivo") |
| `/review` | Scope chip for selected chapter |
| `/`, `/ai`, Settings | Hidden |

---

## 7. Navigation

### 7.1 Sidebar badges

| Item | Badge |
|------|-------|
| Home | Total pending proposals (inbox count) |
| Writing | Dot: amber if unsaved, blue if in-progress chapter |
| Review | Pending revision proposals count |

**v2:** No separate "Sources" badge in PX-2.

### 7.2 Continua (Home)

Priority order for target:

1. Last activity `writing/[chapterId]#section` if activity < 7 days
2. Else first chapter with status `In revisione`
3. Else first chapter with status `Bozza`
4. Else first chapter in outline
5. If no chapters: Continua **disabled**; tooltip "Aggiungi capitoli in Settings"

### 7.3 URL state (restorable)

```text
/writing/cap-03?section=3.2&panel=ai&peek=src-benjamin-1936
```

| Param | Values | Default |
|-------|--------|---------|
| `section` | anchor id | — |
| `panel` | `ai` \| `contesto` \| `fonte` \| `revisione` | `ai` |
| `peek` | source id | — |

Persist on navigation within workspace cluster. Cleared when peek dismissed.

### 7.4 Breadcrumb

`Writing / Cap. 3 — Metodologia / §3.2`

- Click chapter → outline scroll + focus chapter row
- Click Writing → no-op (already there)
- § segment → scroll editor to section

---

## 8. Workspace organization

### 8.1 Active scope model

| Layer | Surfaced in |
|-------|-------------|
| Project | AppShell title |
| Module | Sidebar |
| Chapter | Breadcrumb, outline, ContextBar chip |
| Section | ContextBar chip, outline leaf |
| Selection | AI panel header snippet (max 80 chars) |
| Peek source | Fonte tab title |

### 8.2 Outline

| Element | Rule |
|---------|------|
| Tree | Parts → Chapters → Sections (outline metadata) |
| Status | `Bozza` · `In revisione` · `Approvato` |
| Section done | **Manual checkbox only** in section header (PX-2); feeds progress weights when checked |
| Reorder | Read-only (PX-6) |
| Filter | Tutti / In corso / Da revisionare |
| Context menu | Apri · Segna da revisionare · Segna approvato (with confirms) |

### 8.3 Chapter footer (editor)

Collapsible strip below editor:

```text
Fonti collegate (N) · Citazioni (N) · Parole: XXX · [ Anteprima MD ] · [ Apri in AI ]
```

---

## 9. Writing workflow

### 9.1 Editor

| Rule | Value |
|------|-------|
| Format | Markdown source; preview toggle (split horizontal) |
| Focus | Auto-focus editor on enter unless modal open |
| Autosave | 3s debounce after keystroke |
| Force save | `⌘S` + blur + chapter switch |
| Save indicator | `Salvato` / `Salvataggio…` / `Non salvato` / `Errore` |
| Undo/redo | Native editor stack; AI apply does not bypass undo |
| Find | `⌘⇧F` in-chapter highlight cycle |

### 9.2 Chapter lifecycle

```text
Bozza ──→ In revisione ──→ Approvato
   ↑            │               │
   └────────────┴───────────────┘ (demote, confirm)
```

| Transition | Trigger | Confirm |
|------------|---------|---------|
| → In revisione | Outline menu, AI Review complete, Review entry | No |
| → Approvato | Outline menu, Review accept + checkbox "Segna approvato" | Yes |
| → Bozza | Demote from any state | Yes |
| Edit while Approvato | Allowed; auto-demote to **Bozza** with toast "Capitolo riaperto in bozza" | Implicit |

Progress (ADR-0040): `draft=0.4`, `review=0.7`, `approved=1.0` × weights.

### 9.3 AI actions

| ID | Label | Scope | Result type |
|----|-------|-------|-------------|
| `rewrite` | Riscrivi | Selection | Text proposal |
| `deepen` | Approfondisci | Selection | Text proposal |
| `verify` | Verifica | Selection or chapter | Report + optional text proposal |
| `find_sources` | Trova fonti | Selection or chapter | Source list (no auto-insert) |
| `summarize` | Riassumi | Selection | Text (ephemeral until Applica) |
| `draft_section` | Bozza sezione | Section | Text proposal |
| `outline_check` | Controlla struttura | Chapter | Report (ephemeral) |
| `review` | Revisione | Chapter | Revision proposal → Review queue |

**AI action states:**

```text
Idle → Running (stream) → Complete → [Anteprima] → Applica → Inbox
                    ↓
                 Cancelled (operator Esc or Annulla)
```

| State | UI |
|-------|-----|
| Running | Stream in panel; **Annulla** button; editor remains editable |
| Running + chapter switch | Confirm: "Azione in corso — annullare?" |
| Complete | Anteprima + Applica + Copia |
| Failed | Error inline + Riprova |

**Applica** always creates typed proposal (§12) — never direct persist except Copia to clipboard.

### 9.4 Find sources results (v2)

AI `find_sources` renders ranked list in AI panel:

```text
┌─────────────────────────────────────┐
│ Benjamin (1936) — Opera d'arte…     │
│ [ Anteprima ] [ Collega ] [ Cita ]  │
└─────────────────────────────────────┘
```

- **Anteprima** → Fonte tab peek
- **Collega** → chapter link proposal (inbox)
- **Cita** → cite flow §9.5

### 9.5 Citation workflow

**Format (project default):** `(Author, YYYY)` inline; bibliography keys `[@AuthorYYYY]` in markdown source optional — preview renders formatted.

1. `⌘⇧C` or toolbar **Cita**
2. Source Picker modal (see §11.2)
3. If `candidata` → candidata gate (§4.7)
4. If `esclusa` → block (§19)
5. Optional peek → select passage → **Inserisci citazione**
6. Insert at cursor; no inbox unless candidata path

**W-06 note (§29):** AI-generated prose may contain numeric cites; operator may fix manually until PX-6 validator.

### 9.6 Citation list

Chapter footer **Citazioni** opens drawer: list of markers in chapter with jump-to-cursor.

---

## 10. Review workflow

**Single diff UI:** `/review` only (v2 clarification).

### 10.1 Entry points

| From | Behavior |
|------|----------|
| Home → Revisione | `/review` |
| Writing AI → Revisione | Creates proposal → toast + Revisione tab badge |
| Revisione tab → Apri in Review | `/review?chapter=[id]` |
| Outline → Invia in revisione | Status → In revisione; no auto-diff until proposal exists |

### 10.2 Review layout

```text
┌─────────────────────────────────────────────────────────┐
│ Capitolo [v] · Sezione [v]                              │
├──────────────────────┬──────────────────────────────────┤
│ Originale            │ Proposta                         │
├──────────────────────┴──────────────────────────────────┤
│ Accetta · Accetta parziale · Rifiuta · Modifica in Writing │
└─────────────────────────────────────────────────────────┘
```

| Action | Result |
|--------|--------|
| Accetta | Full replace → saves chapter → optional mark Approvato checkbox |
| Accetta parziale | Selected paragraphs only |
| Rifiuta | Discard proposal; remove from inbox |
| Modifica in Writing | Open chapter at section; proposal remains in inbox |

### 10.3 Compare rules

- **Originale** = last saved chapter at proposal creation time (snapshot)
- **Proposta** = AI output or manual paste proposal
- If chapter edited after proposal: banner "Capitolo modificato dopo la proposta — [ Rigenera revisione ] [ Confronta comunque ]"

### 10.4 History

Last **5** revision proposals per chapter in Review selector dropdown (timestamp + source label).

---

## 11. Source interaction

### 11.1 Source reader (full page: `/sources/[id]`)

| Element | Behavior |
|---------|----------|
| Header | Title, author, year, status badge |
| Body | Readable markdown/text |
| Actions | Cita · Collega capitolo · Apri in Writing |
| Excluded | `Esclusa` badge; cite disabled; reason expanded |
| Nav | Prev/Next within current search result set |

### 11.2 Source Picker (modal)

| Section | Content |
|---------|---------|
| Search | Debounced; min 2 chars |
| Recenti | Last 10 project-wide |
| Collegate | Linked to active chapter |
| Risultati | Retrieval ranked; **excludes** `esclusa` |

Modal blocks editor but not autosave of existing content.

### 11.3 Peek reader (Fonte tab)

Same body as full reader; compact header; **Chiudi anteprima** (Esc).

**When to use which:**

| Situation | Surface |
|-----------|---------|
| Writing while reading | Peek |
| Deep read, no active chapter | Full `/sources/[id]` |
| From Home Ricerca | Full page |

### 11.4 Chapter ↔ source link

- **Collega** adds to linked list + ContextBar count
- **Scollega** → confirm dialog
- Linked list in chapter footer; max display 5 + "Mostra tutte"

---

## 12. Proposal system (unified) **(v2)**

All governed writes flow through one **Proposal Inbox**.

### 12.1 Proposal types

| Type | Operator label | On approve |
|------|----------------|------------|
| `chapter_text` | Modifica testo | Update chapter content |
| `chapter_revision` | Revisione | Update via Review accept path |
| `memory` | Aggiornamento memoria | Promote memory |
| `decision` | Decisione | Update decision record |
| `bibliography` | Fonte bibliografica | Promote source status |
| `source_link` | Collegamento fonte | Persist chapter-source link |

### 12.2 Inbox surfaces

| Surface | Behavior |
|---------|----------|
| Home card | Top 3 proposals + "Vedi tutte (N)" |
| AppShell badge | Total count |
| **Proposte** drawer | `⌘⇧O` — full list, filter by type |
| Session close | Bulk approve/reject **all** pending (OR-7 atomic) |

### 12.3 Individual vs session approve

| Action | Scope |
|--------|-------|
| Approva (single) | One proposal; immediate persist + activity |
| Rifiuta (single) | Discard one |
| Chiudi sessione | Modal: all pending; **Accetta tutto** / **Rifiuta tutto** only (no partial) |

**v2 rule:** Single approve always available — session close is optional convenience, not gate.

### 12.4 Proposal card

```text
┌─────────────────────────────────────┐
│ Modifica testo · Cap. 3             │
│ Riscrivi — 2 min fa                 │
│ [ Anteprima ] [ Approva ] [ Rifiuta ]│
└─────────────────────────────────────┘
```

Anteprima opens appropriate viewer (diff for text/revision, summary for memory).

### 12.5 Blueprint conflict (v2)

If approve would conflict with frozen blueprint artifact:

```text
"Conflitto con versione di riferimento"
[ Mostra differenze ] [ Approva comunque ] [ Annulla ]
```

No silent overwrite (ADR-0041 INV-SY-3).

---

## 13. Context interaction

### 13.1 ContextBar

```text
[ Cap. 3 · §3.2 ]  12 fonti · 4 decisioni · 34 citazioni  [ⓘ]
```

**v2:** Removed opaque "18 voci contesto" — replaced by decision + source + citation counts only (less cognitive load). Definitions visible in Contesto tab.

| Segment | Click |
|---------|-------|
| Scope chip | Outline scroll |
| Counts | Contesto tab |
| ⓘ | Tooltip: 2-sentence plain summary |
| Amber bar | Contesto tab + first conflicting decision |

### 13.2 Context Inspector (Contesto tab)

Sections (collapsible):

1. **Ambito** — chapter, section, selection snippet
2. **Decisioni** — cards sorted: Vincolante first, then relevance
3. **Vincoli corpus** — exclusion rules (plain language)
4. **Definizioni** — terminology matches
5. **Fonti rilevanti** — top 10; click → peek
6. **Regole di scrittura** — collapsed by default

**Stale indicator:** If packet older than 30s and selection changed: "Aggiornamento contesto…" spinner; AI actions wait for fresh packet.

### 13.3 Context refresh

| Event | Refresh |
|-------|---------|
| Chapter/section switch | Full |
| Selection change | 300ms debounce |
| Source link change | Full |
| Proposal approve | Full + toast |
| Autosave | No |

---

## 14. Decision visibility

### 14.1 Decision card

```text
DEC-012 · Vincolante
Benjamin: aura vs riproducibilità
Capitoli: 2, 3
[ Leggi ] [ Chiedi al revisore ]
```

| Status | Modifica |
|--------|----------|
| Vincolante | Blocked — modal explanation |
| Aperta | Read-only in PX-2 (authoring PX-6+) |

### 14.2 Multiple decisions

Show max **3** in Inspector; "Altre 2 decisioni" expands list. Amber ContextBar if **any** Vincolante relevant to selection.

### 14.3 AI banner

Before destructive apply: green "Coerente con DEC-012" or amber "Possibile conflitto con DEC-012" — informational, not blocking.

---

## 15. Memory visibility

Operator never sees tier names. Mapping:

| Internal | Operator copy |
|----------|-----------------|
| Working | Bozza di sessione |
| Ephemeral | Nota temporanea |
| Permanent proposal | Modifica proposta |

Session notes (Temporary equivalent) cleared on session close unless promoted to proposal.

---

## 16. Session continuity

### 16.1 Persisted fields

| Field | Restore |
|-------|---------|
| Last workspace route | Yes |
| Chapter + section | Yes |
| Scroll (editor, reader) | Yes |
| Right rail tab | Yes |
| Peek source | If `peek` param set |
| Selection | Yes if < 24h |
| Draft content | Autosave; local backup if offline |
| AI in-progress | **No** — cancelled on reload |

### 16.2 Session indicator

`Sessione · 2h 14m · 3 proposte`

Click → Proposte drawer. **Chiudi sessione** in drawer footer.

### 16.3 Multi-tab

On save conflict:

```text
Capitolo modificato in un'altra scheda
[ Ricarica versione salvata ] [ Usa questa scheda ]
```

Local unsaved backup preserved until operator chooses.

### 16.4 Browser close

`beforeunload` if `Non salvato` — browser native dialog only.

---

## 17. Interaction rules

| ID | Rule |
|----|------|
| IR-1 | Content center, AI lateral |
| IR-2 | No silent permanent writes |
| IR-3 | Binding decisions in every AI ContextPacket |
| IR-4 | Excluded sources never citable |
| IR-5 | Italian copy; English nav |
| IR-6 | Deterministic progress |
| IR-7 | Destructive actions confirm |
| IR-8 | Dismiss peek → focus editor |
| IR-9 | One diff UI (`/review`) only **(v2)** |
| IR-10 | Single proposal inbox for all types **(v2)** |
| IR-11 | Approvato edit auto-demotes to Bozza **(v2)** |

### 17.1 Modal priority (stacking)

1. Session close (blocks all)
2. Save conflict / data loss
3. Candidata / blueprint conflict
4. Source Picker
5. Coach marks (lowest)

Only one category-1 modal at a time.

### 17.2 Toast catalog **(v2)**

| Event | Toast | Duration |
|-------|-------|----------|
| Save success | (none — use inline indicator) | — |
| Save error | Impossibile salvare | Persistent + Riprova |
| Proposal added | Aggiunto alle proposte | 3s |
| Proposal approved | Modifica approvata | 3s |
| Chapter demoted | Capitolo riaperto in bozza | 4s |
| Source linked | Fonte collegata | 3s |
| Context stale | Contesto aggiornato | 2s |
| Offline | Sei offline — bozza locale | Persistent |

---

## 18. Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` | Command palette |
| `⌘⇧P` | Command palette |
| `⌘⇧O` | Proposal inbox drawer |
| `⌘\` | Toggle outline |
| `⌘⇧\` | Toggle right rail |
| `⌘1`–`⌘4` | Right rail tabs (AI, Contesto, Fonte, Revisione) |
| `⌘S` | Force save |
| `⌘⇧C` | Cite source |
| `⌘⇧F` | Find in chapter |
| `⌘⇧R` | Start review (chapter) |
| `⌘Enter` | Applica on focused AI result |
| `Esc` | Close top modal / dismiss peek / cancel AI if focused |
| `⌘↑/↓` | Prev/next section |
| `G` `W` | Go Writing |
| `G` `S` | Go Sources |
| `G` `H` | Go Home |
| `G` `R` | Go Review |

**Fixed v1 bug:** Cite is **`⌘⇧C`** everywhere (not `⌘⇧S`).

Palette lists all commands with shortcuts. On Windows/Linux: `Ctrl` replaces `⌘`.

---

## 19. User states catalog **(v2)**

### 19.1 Empty states

| Surface | Message | CTA |
|---------|---------|-----|
| Home / no activity | Nessuna attività recente | Scrittura |
| Home / Continua disabled | Nessun capitolo disponibile | Settings |
| Outline | Nessun capitolo | Settings |
| Editor / new section | Inizia a scrivere | — |
| AI / no selection | Seleziona un passaggio o usa azioni di capitolo | (action buttons) |
| Source picker | Nessuna fonte trovata | Modifica ricerca |
| Linked sources | Nessuna fonte collegata | Cita fonte |
| Review | Nessuna revisione in sospeso | Torna a Scrittura |
| Contesto / minimal | Seleziona testo per dettagli | — |
| Proposte inbox | Nessuna proposta in sospeso | — |
| Revisione tab | Nessuna revisione in coda | Avvia revisione |
| Research/Knowledge stub | (see §5.2) | Sources / Writing |

### 19.2 Loading states

| Surface | Pattern |
|---------|---------|
| App shell | Sidebar instant; content skeleton |
| ContextBar | Skeleton chips → live ≤ 500ms |
| Editor | Skeleton → fade in; **editable while context loads** |
| AI stream | Tokens + Annulla |
| Source reader | Top progress bar |
| Review diff | Side skeleton |
| Progress ring | Animate once per session |

### 19.3 Disabled states

| Control | Disabled when | Tooltip |
|---------|---------------|---------|
| AI action buttons | Wrong scope / context loading | Per-action reason |
| Cita | No cursor position | Posiziona il cursore |
| Applica | No complete AI result | — |
| Approva (proposal) | Persist in flight | — |
| Continua | No chapters | Nessun capitolo |
| Insert citation | Source esclusa / candidata unapproved | Reason |

### 19.4 Error states

(See §19 in v1 plus v2 additions)

| Error | Message | Recovery |
|-------|---------|----------|
| Invalid chapter id | Capitolo non trovato | Redirect default |
| AI timeout (60s) | Tempo scaduto | Riprova |
| Proposal persist fail | Salvataggio proposta fallito | Riprova; local copy |
| Session bundle reject | Proposte scartate | Toast; inbox cleared |
| Blueprint conflict | Conflitto versione | §12.5 |

Never show stack traces or OR gate names.

### 19.5 Partial / stale states **(v2)**

| State | UI |
|-------|-----|
| Context stale | Spinner on ContextBar; AI queue until fresh |
| Offline editing | Persistent banner; save queue on reconnect |
| Proposal snapshot outdated | Banner in Review (§10.3) |
| Autosave lag | `Salvataggio…` > 5s → show Annulla tentativo |

---

## 20. Onboarding **(v2 expanded)**

### 20.1 Triggers

| Profile | Flow |
|---------|------|
| First PX-2 open ever | §20.2 coach marks |
| Upgrade from PX-1 (returning) | Single toast: "Scrittura attiva — riprendi da Continua" |
| Empty project | §20.3 |
| Hint dismissed forever | Stored per operator per hint id |

### 20.2 Coach marks (max 4, skippable)

1. Home → Continua
2. Writing → three panels
3. ContextBar → automatic context
4. Proposal inbox icon → governed changes

### 20.3 Empty project onboarding

Home shows:

```text
Benvenuto in ThesisOS
Inizia dalla Scrittura o importa il tuo outline in Settings.
[ Vai a Scrittura ]  [ Settings ]
```

No broken Continua.

### 20.4 Just-in-time hints (once each)

| Trigger | Hint |
|---------|------|
| First selection | Seleziona testo per azioni AI |
| First cite | 3-step cite coach |
| First proposal | Le modifiche vanno approvate |
| First session close | Chiudi sessione approva tutto insieme |
| First amber decision | Decisioni vincolanti guidano la tesi |
| First candidata | Le fonti candidata richiedono approvazione |

Skip: **Non mostrare più** per that hint id.

---

## 21. Desktop-first behavior

| Breakpoint | Layout |
|------------|--------|
| ≥1280px | Full three-panel |
| 1024–1279px | Collapsible outline rail |
| 768–1023px | Outline drawer; right rail overlay |
| <768px | Read-only preview + banner |

Target: 1440×900, 1920×1080.

Panel collapse persisted per operator. Sidebar collapse: PX-1 behavior.

---

## 22. Focus and accessibility **(v2)**

| Rule | Behavior |
|------|----------|
| Route enter | Focus editor (Writing) or first interactive (Review) |
| Modal open | Trap focus; Esc closes if dismissible |
| Modal close | Restore prior focus element |
| Peek close | Focus editor at last cursor |
| Tab order | Outline → Editor → Right rail → ContextBar |
| Screen reader | ContextBar counts in `aria-live="polite"` |
| Reduced motion | No progress ring animation |

---

## 23. Command palette inventory **(v2)**

| Command | Category |
|---------|----------|
| Vai a: Home, Writing, Sources, Review, AI, Settings | Navigate |
| Capitolo: (dynamic list) | Navigate |
| Fonte: (recent) | Navigate |
| Cita fonte | Action |
| Azioni AI: (contextual subset) | Action |
| Proposte in sospeso | Action |
| Chiudi sessione | Action |
| Mostra scorciatoie | Help |

Fuzzy search on labels. Recent commands at top (max 5).

---

## 24. Copy and localization

Unchanged from v1: Italian operator copy; English nav labels.

**Status labels:** Bozza, In revisione, Approvato  
**Source status:** Candidata, Approvata, Esclusa

---

## 25. PX-2 exclusions

Unchanged from v1 §23. Import **stub** only (§4.8).

---

## 26. Platform limitation — W-06 **(v2)**

When AI prose contains numeric bracket cites `[1]`:

- Inline editor: no auto-block (operator may edit)
- Verify action: flag "Citazione numerica — preferire (Autore, Anno)"
- Footer link: "Limitazione piattaforma — validatore in arrivo (PX-6)"

Do not claim OR-6 deterministic cites in UI copy.

---

## 27. Qualification acceptance (QWO-PX2-001)

| # | Criterion |
|---|-----------|
| AC-1 | ContextBar live counts match ContextPacket |
| AC-2 | Binding decision in Inspector on contradictory retrieval |
| AC-3 | Editor autosave + chapter switch without data loss |
| AC-4 | ≥4 AI actions stream from Writing panel |
| AC-5 | Applica creates inbox proposal — not silent write |
| AC-6 | Cite: picker → peek → marker inserted |
| AC-7 | Excluded source cite blocked |
| AC-8 | Candidata cite blocked until approved |
| AC-9 | Decision card readable; Vincolante edit blocked |
| AC-10 | Continua restores chapter, section, tab, peek |
| AC-11 | Single + session proposal approve/reject |
| AC-12 | Review accept/reject on `/review` only |
| AC-13 | Approvato edit demotes to Bozza |
| AC-14 | Home progress deterministic on status change |
| AC-15 | Research/Knowledge stubs — no broken routes |
| AC-16 | `/writing` default chapter redirect |
| AC-17 | AI cancel mid-stream — no partial proposal |
| AC-18 | Multi-tab conflict dialog |
| AC-19 | OR-1…OR-7 regression; PX-1 surfaces intact |
| AC-20 | `make ci` green |

---

## 28. EWO decomposition (recommended)

| EWO | Deliverable |
|-----|-------------|
| PX2-EWO-001 | ContextBar + Inspector + stale handling |
| PX2-EWO-002 | Editor + lifecycle + autosave |
| PX2-EWO-003 | AI panel + stream/cancel |
| PX2-EWO-004 | Proposal inbox + types + approve flows |
| PX2-EWO-005 | Source picker, peek, reader, cite |
| PX2-EWO-006 | Decision cards + warnings |
| PX2-EWO-007 | Session persist + Continua + multi-tab |
| PX2-EWO-008 | Review route activation |
| PX2-EWO-009 | Command palette, shortcuts, states, onboarding |
| PX2-EWO-010 | Stubs: Research/Knowledge/Import + W-06 messaging |

---

## 29. Edge-case register **(v2)**

| # | Scenario | Expected behavior |
|---|----------|-------------------|
| E-1 | Open app offline | Banner; load last cached chapter; queue saves |
| E-2 | AI running, operator hits Esc | Cancel stream; no proposal |
| E-3 | Two proposals same chapter | Both in inbox; independent approve |
| E-4 | Approve text proposal while Review open | Review banner if snapshot stale |
| E-5 | Cite with no chapter context | Picker works; link prompt "Collega a quale capitolo?" |
| E-6 | Empty chapter approve to Approvato | Allow; progress reflects status |
| E-7 | Session close with 0 proposals | Toast "Nessuna proposta"; no modal |
| E-8 | Context fails permanently | Editor works; AI disabled; Retry in bar |
| E-9 | Peek source deleted | Toast; close peek |
| E-10 | `/ai` edit while Writing open | Independent; no auto-sync to chapter |
| E-11 | Rapid chapter switch | Queue saves serially; no lost edits |
| E-12 | Find sources → 0 results | "Nessuna fonte suggerita" + link Sources search |
| E-13 | Operator rejects session bundle | All pending rejected; confirm dialog |
| E-14 | First visit `/review` mid-write | Chapter context pre-selected if from Writing |
| E-15 | Blueprint conflict on approve | §12.5 dialog; no silent overwrite |

---

## 30. Governance references

| Artifact | Role |
|----------|------|
| `docs/product/EXECUTION-AUTHORIZATION-PX2-AMENDMENT.md` | Authorization |
| `docs/product/specs/thesisos-product-ux-v1.md` | Baseline IA |
| ADR-0036, 0038, 0039, 0040, 0041 | Frozen invariants |
| `docs/KNOWN_LIMITATIONS.md` W-06 | Platform limitation copy |
| `design-system/thesisos/MASTER.md` | Visual patterns |

IA or three-panel changes require P8 — not this spec.

---

## 31. v1 → v2 change log

| Area | v1 issue | v2 resolution |
|------|----------|---------------|
| Shortcuts | Journey B used ⌘⇧S | Unified ⌘⇧C for cite |
| Right rail | ⌘1…9 for 4 tabs | ⌘1–⌘4 explicit |
| Review | Duplicated diff in tab + route | Single `/review` diff; tab is queue |
| Proposals | Session-only implied | Inbox + single approve anytime |
| ContextBar | "18 voci contesto" vague | Removed; counts only |
| Section done | Word count OR checkbox | Checkbox only |
| Continua | No empty fallback | Disabled + tooltip + onboarding |
| Import | Missing | Stub journey §4.8 |
| Candidata | Mentioned | Full gate §4.7 |
| AI cancel | Missing | §9.3 state machine |
| `/writing` bare | Unspecified | Default redirect §5.1 |
| Research/Knowledge | "stub links" vague | §5.2 explicit stub page |
| W-06 | Missing | §26 |
| Focus/a11y | Missing | §22 |
| Commands | Incomplete | §23 inventory |
| Edge cases | Scattered | §29 register |

---

## WO-TRACE

```text
px2-research-workspace-experience.md (v1)
  → Head of Product review → v2 (this document)
  → Architect Program Review → PX2-EWO-* → QWO-PX2-001
```
