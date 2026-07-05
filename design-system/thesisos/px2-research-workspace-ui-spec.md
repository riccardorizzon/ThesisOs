# PX-2 — Research Workspace UI Specification

> **Role:** UX & Design System Lead · **Source of truth:** `docs/product/specs/px2-research-workspace-experience.md`  
> **Status:** ACTIVE — pending Execution Authorization Amendment ratification  
> **Precedence:** Frozen tokens (`docs/product/design-system-v1.md`) → this spec → page overrides (`pages/*.md`)

Transforms the Product Specification into implementation-ready UI. **No workflow or architecture changes.**

---

## 0. Design thesis

The Research Workspace is a **premium desktop writing environment**: content center, AI lateral, context always visible. Visual quality targets **Linear** (density, status, keyboard), **Notion** (hierarchy), **Cursor** (selection-aware lateral AI), **Arc** (Continua), **Figma** (inspector without leaving canvas).

| Principle | UI expression |
|-----------|---------------|
| Content center | Editor gets flex-1, max readable measure, minimal chrome |
| AI lateral | Right rail 320px; never full-screen for standard actions |
| Context assembled | ContextBar live; Inspector human-readable |
| No silent writes | Proposals queue; Applica never mutates directly |
| Calm academic | Frozen neutrals + ink-blue accent; no chat gradients |

---

## 1. Token delta (PX-2)

Extends `frontend/styles/tokens.css`. **Do not override frozen color values.**

### 1.1 Layout tokens (new)

| Token | Value | Usage |
|-------|-------|-------|
| `--outline-width` | `15rem` (240px) | Writing left panel |
| `--rail-width` | `20rem` (320px) | Writing right panel |
| `--rail-width-narrow` | `17.5rem` (280px) | Right rail at 1024–1279px |
| `--editor-min-width` | `30rem` (480px) | Center panel floor |
| `--contextbar-height` | `2.75rem` (44px) | ContextBar compact row |
| `--workspace-chrome-height` | `3rem` (48px) | Panel header bars |
| `--row-height-dense` | `2.25rem` (36px) | Outline rows, list items |

Tailwind extensions: `w-outline`, `w-rail`, `min-w-editor`, `h-contextbar`, `h-row-dense`.

### 1.2 Semantic status tokens (usage map)

| Token | PX-2 usage |
|-------|------------|
| `--color-success` | `Approvato` badge, accept actions, save OK |
| `--color-warning` | `In revisione`, ContextBar amber, binding decision |
| `--color-danger` | Errors, cite blocked, reject destructive |
| `--color-accent` | Primary CTAs, focus rings, active tab, links |
| `--color-accent-subtle` | Selected outline row, active nav chip, AI streaming bg |

### 1.3 Typography roles

| Role | Size | Weight | Leading | Usage |
|------|------|--------|---------|-------|
| **Display** | `--text-2xl` | semibold | tight | Home H1, Review selector title |
| **Title** | `--text-lg` | semibold | tight | Panel headers, modal titles |
| **Body** | `--text-base` | normal | relaxed | Editor content (max 70ch) |
| **UI** | `--text-sm` | medium | normal | Buttons, tabs, outline labels |
| **Meta** | `--text-xs` | medium | normal | Badges, counts, timestamps |
| **Mono** | `--text-xs` | normal | relaxed | Citation tokens, DEC-IDs |

Editor body: `text-base leading-relaxed`; UI elsewhere: `text-sm`.

### 1.4 Spacing rhythm

Base unit: `--space-2` (8px). Panel padding: `--space-4`. Section gaps: `--space-6`. Page gutters: `--space-6` (24px) at ≥1280px; `--space-4` at 1024–1279px.

| Context | Padding |
|---------|---------|
| Panel header | `px-4 py-3` (12px vertical) |
| Panel body | `p-4` |
| ContextBar | `px-4 py-2` |
| Modal | `p-6` |
| Card (decision, proposal) | `p-4` gap `space-y-3` |

### 1.5 Elevation & borders

- Panels: `border border-border bg-surface shadow-sm rounded-lg`
- ContextBar warning: `border-warning/30 bg-warning/5` (amber tint via `color-mix` or Tailwind `amber-50` at 5% opacity on warning token)
- Modals: `shadow-md`
- Dividers: `border-border` only — no double borders between adjacent panels (shared gap `gap-3` / `gap-4`)

---

## 2. Iconography

**Library:** [Lucide](https://lucide.dev) — stroke 1.5px, 16px inline / 20px header.

| Context | Icon | Notes |
|---------|------|-------|
| AI tab | `Sparkles` | Subtle; not purple |
| Contesto tab | `Layers` | Inspector |
| Fonte tab | `BookOpen` | Peek reader |
| Revisione tab | `GitCompare` | Diff |
| Cite | `Quote` | Toolbar + ⌘⇧C |
| Continua | `Play` or `ArrowRight` | Home CTA only |
| Decision warning | `AlertTriangle` | Amber, 14px |
| Save states | `Check` / `Loader2` / `Circle` | Spinner animates unless reduced-motion |
| Command palette | `Search` | ⌘K |
| Session close | `LogOut` | AppShell trailing |
| Excluded source | `Ban` | Muted + strikethrough title |

No emojis. Icons paired with text labels on primary chrome; icon-only only with `aria-label` + tooltip.

---

## 3. Motion & transitions

| Pattern | Spec |
|---------|------|
| Default | `transition-colors duration-200` — **no layout shift** on hover |
| Panel collapse | `transition-[width,opacity] duration-200 ease-out`; width 0 when collapsed |
| ContextBar populate | Skeleton → content crossfade 150ms |
| AI stream | Token append; caret blink optional; cancel fades in 100ms |
| Toast | Slide up 200ms; auto-dismiss 5s |
| Modal | Backdrop fade 150ms; panel scale 0.98→1 over 200ms |
| Progress ring (Home) | Animate 0→value once on first load; `prefers-reduced-motion: reduce` → instant |
| Review diff | Stagger columns 100ms |

**Reduced motion:** `@media (prefers-reduced-motion: reduce)` — disable panel width animation, ring animation, modal scale; keep opacity fades ≤100ms.

---

## 4. Global chrome

### 4.1 AppShell (extends PX-1)

```text
┌──────────┬──────────────────────────────────────────────────────────────┐
│ Sidebar  │ Breadcrumbs row                                              │
│ 208px    ├──────────────────────────────────────────────────────────────┤
│          │ ContextBar (workspace routes only)                           │
│          ├──────────────────────────────────────────────────────────────┤
│          │ Workspace content                                            │
│          │                                    Session chip │ ⌘K hint   │
└──────────┴──────────────────────────────────────────────────────────────┘
```

**PX-2 additions:**

| Element | Spec |
|---------|------|
| Nav badges | Home: proposal count pill; Writing: status dot; Review: pending count |
| Session chip | Trailing in breadcrumb row: `Sessione · 2h 14m · 3 proposte` — click → Chiudi sessione |
| ⌘K affordance | Ghost button `⌘K` right of breadcrumbs on ≥1024px |

Sidebar unchanged: `--sidebar-width` (13rem). Nav labels English; tooltips Italian where helpful.

### 4.2 ContextBar (live)

Full width between breadcrumb row and workspace. Height `--contextbar-height`.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ [ Cap. 3 · §3.2 ]   12 fonti · 4 decisioni · 18 voci · 34 citazioni  ⓘ │
└─────────────────────────────────────────────────────────────────────────┘
```

| Segment | Style | Interaction |
|---------|-------|-------------|
| Scope chip | `rounded-md bg-accent-subtle px-2 py-0.5 text-sm font-medium text-accent` | Click → scroll outline to section |
| Counts | `text-sm text-ink-muted`, middot separators | Click → Right rail **Contesto** tab |
| ⓘ | `text-ink-subtle` icon button | Tooltip: plain-language packet summary |
| Warning | Full bar `bg-warning/5 border-warning/30`; scope chip gains `AlertTriangle` | Click → Contesto tab, scroll to decision |

**Loading:** Three skeleton chips (scope + 2 count groups); editor remains interactive.

**Routes:** Visible on `/writing/*`, `/sources/*` (when `?chapter=` in URL), `/review`.

### 4.3 Command palette

Modal centered, max-width `32rem`, `rounded-lg shadow-md`.

| Section | Content |
|---------|---------|
| Input | Search with `⌘K` prefix hint |
| Groups | Vai a… / Capitoli / Fonti / Azioni |
| Row | Icon + label + shortcut right-aligned |
| Empty | "Nessun risultato" |

Keyboard: `↑↓` navigate, `Enter` execute, `Esc` close. Italian action labels; English route names in "Vai a" group.

---

## 5. Writing workspace

> Page override: `design-system/thesisos/pages/writing.md`

### 5.1 Three-panel layout (frozen)

```text
ContextBar ─────────────────────────────────────────────────────────────
┌──────────────┬────────────────────────────────────┬────────────────────┐
│ Outline      │ Editor                             │ Right rail         │
│ 240px        │ flex-1 min 480px                   │ 320px tabbed       │
│              │                                    │ AI│Contesto│Fonte│Rev│
└──────────────┴────────────────────────────────────┴────────────────────┘
│ Linked sources footer (collapsible)                                    │
└────────────────────────────────────────────────────────────────────────┘
```

**Component tree:**

```text
WritingPage
├── ContextBar
├── WritingWorkspace
│   ├── WritingOutline (left)
│   ├── WritingEditorShell (center)
│   │   ├── EditorToolbar
│   │   ├── MarkdownEditor
│   │   └── EditorFooter (word count, save state)
│   └── RightRail
│       ├── RailTabs
│       └── RailPanel (single slot)
│           ├── AiPanel (default)
│           ├── ContextInspector
│           ├── SourcePeekReader
│           └── RevisionQueue
└── LinkedSourcesFooter
```

### 5.2 Outline panel

| Element | Spec |
|---------|------|
| Width | `--outline-width` (240px); collapsible via `⌘\` |
| Row height | `--row-height-dense` (36px) |
| Tree indent | 12px per level |
| Active chapter | `bg-accent-subtle text-accent font-medium` |
| Active section | Left border 2px `accent` |
| Status badge | Pill: Bozza (muted) / In revisione (warning) / Approvato (success) |
| Progress mini | 4px track + fill; deterministic only |
| Filter | Segmented control top: Tutti / In corso / Da revisionare |
| Context menu | "Invia in revisione" — outline row overflow `⋯` |

### 5.3 Editor (center)

| Zone | Spec |
|------|------|
| Toolbar | `border-b`, height 40px: Cita (⌘⇧C), Find (⌘⇧F), Preview toggle |
| Content | `max-w-[70ch] mx-auto` prose area; focus ring on container when editor focused |
| Save indicator | Meta right: `Salvato` (success subtle) / `Salvataggio…` (spinner) / `Non salvato` (warning) |
| Footer | Section + chapter word counts; `text-xs text-ink-subtle` |
| Gutter (optional) | 16px; decision conflict icon `AlertTriangle` on affected paragraphs |

**Selection:** Persists across rail tab switches; highlighted with `bg-accent-subtle/50`.

### 5.4 Right rail (tabbed single slot)

| Tab | Key | Panel content |
|-----|-----|---------------|
| AI | ⌘1 | Action list + stream output + Applica |
| Contesto | ⌘2 | Context Inspector sections |
| Fonte | ⌘3 | Peek reader (when source open) |
| Revisione | ⌘4 | Inline revision queue |

**Tab bar:** `h-10`, underline active indicator 2px accent; inactive `text-ink-muted`.

**Collapse:** `⌘⇧\` toggles; editor expands. State persisted in session.

#### AI panel

```text
┌─ Azioni AI ─────────────────────┐
│ [selection summary or chapter]  │
├─────────────────────────────────┤
│ □ Riscrivi                      │
│ □ Approfondisci                 │
│ □ Verifica                      │
│ ...                             │
├─────────────────────────────────┤
│ Stream output area              │
│ [ Annulla ]  [ Applica ]        │
└─────────────────────────────────┘
```

- Actions disabled + tooltip when preconditions missing
- Stream: `font-mono text-sm` or prose matching editor
- **Applica** → proposal preview modal → queue (never silent write)
- Conflict banner: `Questa azione rispetta DEC-012` or `Conflitto possibile` (warning strip)

#### Context Inspector (Contesto tab)

Collapsible sections (accordion):

| Section | Default |
|---------|---------|
| Ambito | Open |
| Decisioni vincolanti | Open if any |
| Vincoli corpus | Open if any |
| Definizioni | Collapsed |
| Fonti rilevanti | Open |
| Regole di scrittura | Collapsed |

Each decision → `DecisionCard` component (§6).

#### Fonte tab (peek reader)

Compact reader: title, metadata strip, scrollable body. Actions: Cita, Collega, Apri in Writing. Prev/Next when from search. Dismiss → restore prior tab (usually AI); focus returns to editor (IR-8).

#### Revisione tab

List of pending hunks for current chapter; "Apri confronto" → `/review?chapter=`.

### 5.5 Linked sources footer

Collapsible bar below three panels: "Fonti collegate (N)" — horizontal chip list; empty state CTA "Cita fonte".

### 5.6 Breadcrumb

`Writing / Cap. 3 — Metodologia / §3.2` — chapter segment focuses outline.

---

## 6. Shared components (new / extended)

### 6.1 StatusBadge

```tsx
variant: "bozza" | "in-revisione" | "approvato" | "esclusa" | "candidata"
```

| Variant | Background | Text |
|---------|------------|------|
| bozza | `surface-muted` | `ink-muted` |
| in-revisione | `warning/10` | `warning` |
| approvato | `success/10` | `success` |
| esclusa | `danger/10` | `danger` |
| candidata | `accent-subtle` | `accent` |

Pill: `rounded-full px-2 py-0.5 text-xs font-medium`.

### 6.2 DecisionCard

```text
┌─────────────────────────────────────────┐
│ DEC-012 · Vincolante          [badge]   │
│ Benjamin: aura vs riproducibilità       │
│ Influenza: Cap. 2, Cap. 3              │
│ [ Leggi ]  [ Chiedi al revisore ]      │
└─────────────────────────────────────────┘
```

- Card: `rounded-lg border border-border bg-surface p-4`
- ID: `font-mono text-xs text-ink-subtle`
- Expand "Leggi": inline accordion, max-height animate
- Modifica: not rendered for Vincolante; if triggered → blocked modal

### 6.3 ProposalCard / SessionBundleModal

Proposal queue item: title, affected artifacts list, diff summary. Session close: **atomic** — all proposals listed; single Applica tutto / Rifiuta tutto (OR-7). No partial dismiss without explicit copy.

### 6.4 SourcePicker (modal)

Width `36rem`, max-height `80vh`.

| Zone | Spec |
|------|------|
| Search | Sticky top; debounced 200ms; inline spinner |
| Tabs | Recenti (10) / Collegate / Risultati |
| Row | Title, author, year; hover `bg-surface-muted` |
| Excluded | Omitted from results; if navigated directly → blocked state |

### 6.5 SourceReader (full + peek)

| Mode | Layout |
|------|--------|
| Full (`/sources/[id]`) | Page layout with metadata strip + body |
| Peek (Fonte tab) | Right rail content area |

Metadata strip: author, year, status badge, concept tags (read-only chips). Highlight + copy quote (PX-2). Excluded: `Ban` badge + reason callout `border-danger/20 bg-danger/5`.

### 6.6 ReviewCompare

```text
┌─ Selector: Capitolo / Sezione ─────────────────────────────────────────┐
├────────────────────────────┬───────────────────────────────────────────┤
│ Originale                  │ Proposta                                  │
│ read-only                  │ AI label if applicable                    │
├────────────────────────────┴───────────────────────────────────────────┤
│ [ Accetta ] [ Accetta parziale ] [ Rifiuta ] [ Modifica ]              │
└────────────────────────────────────────────────────────────────────────┘
```

- Columns equal width; paragraph-level selectable hunks
- Added text: `bg-success/10`; removed: `bg-danger/10 line-through`
- History sidebar: last 5 revisions, timestamp + source

### 6.7 CoachMark

Single-step popover anchored to target; max 3-step chains; "Salta" always visible; dismiss persists.

### 6.8 EmptyState

Icon 20px `text-ink-subtle` + `text-sm text-ink-muted` + optional CTA button. Centered in panel content area.

### 6.9 OfflineBanner

Sticky top below ContextBar: `bg-warning/10 border-b border-warning/30`; text per spec §19.

---

## 7. Home (PX-2 delta)

> Page override: `design-system/thesisos/pages/home.md` (updated)

| PX-2 change | Spec |
|-------------|------|
| Continua | Deep link with full URL state restoration |
| Progress ring | Live from chapter statuses |
| Activity cards | Proposal types per §6.4 copy table |
| Nav badge source | Pending proposals count |
| Quick action Revisione | → `/review` |

**Continua button:** Primary `bg-accent`; sublabel sr-only with chapter + section.

**Activity card types:**

| Type | Icon | Accent |
|------|------|--------|
| Aggiornamento proposto | `FileEdit` | accent |
| Decisione vincolante | `AlertTriangle` | warning |
| Nuova fonte | `BookPlus` | accent |
| Chiudi sessione | `Package` | accent |

---

## 8. Sources module

> Page override: `design-system/thesisos/pages/sources.md`

| Element | Spec |
|---------|------|
| Search bar | Full width, sticky; focus on entry from Home Ricerca |
| Filters | Chips: candidata / approvata / esclusa |
| Grid | `EntityCard` 2–3 columns at 1440px |
| Sticky chip | "Torna a Scrittura" when `?chapter=` in URL — `fixed bottom-6 right-6` pill |
| Detail actions | Cita · Collega capitolo · Apri in Writing |

---

## 9. Review module

> Page override: `design-system/thesisos/pages/review.md`

Full-page `ReviewCompare`; no three-panel layout. ContextBar visible. Entry from Home, Writing, or outline context menu.

---

## 10. Responsive behavior

| Breakpoint | Writing layout |
|------------|----------------|
| ≥1280px | Full three-panel; ContextBar inline |
| 1024–1279px | Outline → icon rail 48px (expand on hover/click); rail `280px` |
| 768–1023px | Outline drawer overlay; rail overlay from right; toggle buttons visible |
| <768px | Read-only banner; editor preview only; no AI execution |

**Read-only banner:** `bg-surface-muted border-b px-4 py-2 text-sm` — "Usa desktop per scrivere".

---

## 11. Accessibility

| Requirement | Implementation |
|-------------|----------------|
| Contrast | ≥4.5:1 body text; ≥3:1 UI components |
| Focus | `focus-visible:outline-2 outline-offset-2 outline-accent` on all interactives |
| Keyboard | Full shortcut map §16 product spec; no browser override without `preventDefault` in workspace |
| Landmarks | `nav`, `main`, `aside` per panel; `aria-label` on icon buttons |
| Tabs | Right rail uses `role="tablist"` / `tabpanel`; `aria-selected` |
| Live regions | `aria-live="polite"` for save state, AI stream complete, toast |
| Reduced motion | See §3 |
| Touch targets | ≥44px on chrome; dense 36px rows acceptable with horizontal padding |

Screen reader: ContextBar `aria-label="Contesto attivo per le azioni AI"`; decision status announced on expand.

---

## 12. Z-index scale

| Layer | z-index |
|-------|---------|
| Base content | 0 |
| Sticky ContextBar | 10 |
| Drawer overlay backdrop | 40 |
| Drawer panel | 50 |
| Command palette / modal | 60 |
| Toast | 70 |
| Coach mark | 80 |

---

## 13. File map (engineering)

| Component | Path (proposed) |
|-----------|-----------------|
| ContextBar | `components/context/ContextBar.tsx` (extend) |
| ContextInspector | `components/context/ContextInspector.tsx` |
| RightRail | `components/writing/RightRail.tsx` |
| RailTabs | `components/writing/RailTabs.tsx` |
| WritingWorkspace | `components/writing/WritingWorkspace.tsx` (extend) |
| MarkdownEditor | `components/writing/MarkdownEditor.tsx` |
| SourcePicker | `components/sources/SourcePicker.tsx` |
| SourceReader | `components/sources/SourceReader.tsx` |
| DecisionCard | `components/decisions/DecisionCard.tsx` |
| ReviewCompare | `components/review/ReviewCompare.tsx` |
| CommandPalette | `components/chrome/CommandPalette.tsx` |
| SessionChip | `components/chrome/SessionChip.tsx` |
| StatusBadge | `components/ui/StatusBadge.tsx` |
| CoachMark | `components/onboarding/CoachMark.tsx` |
| ProposalBundleModal | `components/memory/ProposalBundleModal.tsx` |

Token additions: `frontend/styles/tokens.css` + `tailwind.config.ts` width keys.

---

## 14. EWO design checklist

| EWO | Design deliverable | Verify |
|-----|-------------------|--------|
| PX2-EWO-001 | ContextBar + Inspector specs §4.2, §5.4 | AC-1, AC-2 |
| PX2-EWO-002 | Editor + outline §5.2–5.3 | AC-3 |
| PX2-EWO-003 | AI panel §5.4, ProposalCard §6.3 | AC-4, AC-5 |
| PX2-EWO-004 | SourcePicker, Reader §6.4–6.5 | AC-6, AC-7 |
| PX2-EWO-005 | DecisionCard §6.2 | AC-8 |
| PX2-EWO-006 | Session chip, Continua, URL state §4.1, §7 | AC-9, AC-10 |
| PX2-EWO-007 | ReviewCompare §6.6 | AC-11 |
| PX2-EWO-008 | Command palette, shortcuts, all states §3–4, §17–19 | AC-12–14 |

---

## 15. Governance

| Artifact | Role |
|----------|------|
| `docs/product/specs/px2-research-workspace-experience.md` | Product behavior (source) |
| `docs/product/design-system-v1.md` | Frozen colors |
| `design-system/thesisos/MASTER.md` | Global patterns |
| This file | PX-2 UI implementation spec |
| `design-system/thesisos/pages/*.md` | Per-route overrides |

---

## WO-TRACE

```text
px2-research-workspace-experience.md → px2-research-workspace-ui-spec.md → pages/{writing,sources,review,home}.md → PX2-EWO-*
```
