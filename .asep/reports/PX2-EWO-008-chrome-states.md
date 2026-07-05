# PX2-EWO-008 — Chrome States Report

> **WorkOrder:** PX2-EWO-008  
> **Sub-agent:** H (Wave D)  
> **Status:** ✅ Complete  
> **Date:** 2026-07-04

---

## Summary

Integrated global command palette (⌘K / ⌘⇧P), Linear-style navigation chords (G→W/S/H), AppShell chrome badges and ⌘K affordance, offline banner, PX-2 contextual coach marks (max 3 steps), and centralized shortcut discoverability. All owned tests pass; `tsc --noEmit` clean.

---

## Deliverables

### 1. CommandPalette (`frontend/components/chrome/CommandPalette.tsx`)

| Requirement | Status |
|-------------|--------|
| Opens on ⌘K and ⌘⇧P globally | ✅ via `useKeyboardShortcuts` + `thesisos:open-command-palette` |
| Searchable actions: routes, chapters, shortcuts §16 | ✅ groups Vai a… / Capitoli / Azioni / Scorciatoie |
| z-index 60 | ✅ `z-[60]` |
| Italian action labels; English route names | ✅ |
| `useCommandPalette()` + event export | ✅ |

### 2. useKeyboardShortcuts (`frontend/hooks/useKeyboardShortcuts.ts`)

| Requirement | Status |
|-------------|--------|
| G→W, G→S, G→H (1s timeout) | ✅ |
| ⌘K / ⌘⇧P palette open | ✅ |
| No duplicate ⌘1-4, ⌘⇧R, ⌘⇧C handlers | ✅ delegated to feature modules / palette events |
| Editable-target guard | ✅ skips chords in inputs |

### 3. AppShell updates (`frontend/components/AppShell.tsx`)

| Requirement | Status |
|-------------|--------|
| ⌘K affordance (Search + hint, ≥1024px) | ✅ `data-testid="command-palette-trigger"` |
| Home proposal count pill | ✅ from `listPendingProposals()` |
| Writing status dot (draft / in_review) | ✅ from `chapterClient.list()` |
| Review pending footer note | ✅ sidebar settings area (Review not in ADR-0036 nav) |
| CommandPalette + shortcuts + OfflineBanner + CoachMarkProvider mounted | ✅ |
| SessionChip, Breadcrumbs, six-module nav preserved | ✅ |

### 4. CoachMark (`frontend/components/onboarding/CoachMark.tsx`)

| Step | Target | Copy |
|------|--------|------|
| 1 | `[data-testid="continua-link"]` | Riprendi da dove hai lasciato |
| 2 | `[data-testid="writing-workspace"]` | Tre pannelli di scrittura |
| 3 | `[data-testid="context-bar"]` | L'AI vede questo contesto automaticamente |

- Max 3 steps ✅  
- Skip always visible ✅  
- Dismiss forever: `localStorage` key `thesisos-onboarding-px2` ✅  
- z-index 80 ✅  

### 5. OfflineBanner (`frontend/components/chrome/OfflineBanner.tsx`)

- Shows when `navigator.onLine === false` ✅  
- Copy: "Sei offline — modifiche salvate localmente" ✅  
- Optional dismiss ✅  

### 6. useReducedMotion (`frontend/hooks/useReducedMotion.ts`)

- Returns boolean from `prefers-reduced-motion: reduce` ✅  

### 7. Tokens / Tailwind

- `frontend/styles/tokens.css` — PX-2 layout tokens verified present (`--outline-width`, `--rail-width`, `--contextbar-height`, etc.)  
- `frontend/tailwind.config.ts` — width/height extensions verified present  

### 8. Empty / loading / error states

Existing feature empty states (Writing, Review, Sources, ContextBar) unchanged per wire-only constraint. Chrome surfaces add palette empty state "Nessun risultato" and offline banner per spec §19.

### 9. Responsive read-only banner (<768px)

**Deferred to Integration D** — not in exclusive ownership list; documented below as integration hook.

---

## Files

### Created

```
frontend/components/chrome/CommandPalette.tsx
frontend/components/chrome/CommandPalette.test.tsx
frontend/components/chrome/OfflineBanner.tsx
frontend/components/onboarding/CoachMark.tsx
frontend/components/onboarding/CoachMark.test.tsx
frontend/hooks/useKeyboardShortcuts.ts
frontend/hooks/useKeyboardShortcuts.test.tsx
frontend/hooks/useReducedMotion.ts
```

### Modified

```
frontend/components/AppShell.tsx
frontend/components/AppShell.test.tsx
```

### Unchanged (verified)

```
frontend/app/layout.tsx          # AppShell already wraps children
frontend/styles/tokens.css       # tokens present
frontend/tailwind.config.ts      # extensions present
```

---

## Tests

```bash
cd frontend && npm run test -- --run components/chrome components/onboarding hooks/useKeyboardShortcuts components/AppShell.test.tsx
```

| Suite | Tests |
|-------|-------|
| CommandPalette.test.tsx | 3 |
| CoachMark.test.tsx | 3 |
| useKeyboardShortcuts.test.tsx | 2 |
| AppShell.test.tsx | 6 |
| **Total** | **14 passed** |

```bash
cd frontend && npx tsc --noEmit
```

**Result:** ✅ exit 0

---

## Integration hooks for Integration D

Palette and shortcut discoverability dispatch custom events that feature workspaces must listen for:

| Event | Intended consumer | Notes |
|-------|-------------------|-------|
| `thesisos:toggle-outline` | WritingWorkspace | ⌘\ panel collapse |
| `thesisos:toggle-right-rail` | WritingWorkspace | ⌘⇧\ rail collapse |
| `thesisos:force-save` | WritingEditorShell | ⌘S |
| `thesisos:find-in-chapter` | WritingEditorShell | ⌘⇧F |
| `thesisos:apply-ai-suggestion` | WritingAiPanel | ⌘Enter |
| `thesisos:outline-prev-section` | WritingOutline | ⌘↑ |
| `thesisos:outline-next-section` | WritingOutline | ⌘↓ |
| `thesisos:rail-tab-{1-4}` | RightRail | Optional event bridge alongside existing ⌘1-4 keydown in `rightRailIntegration.ts` |

**Already wired (no Integration D action):**

| Event | Owner |
|-------|-------|
| `thesisos:open-command-palette` | CommandPalette / AppShell |
| `thesisos:open-review` | `reviewIntegration.ts` |
| `thesisos:insert-citation` | `citationInsert.ts` |

**Responsive (<768px read-only banner):** Add `ReadOnlyBanner` in AppShell or writing route shell showing "Usa desktop per scrivere" per spec §21.1 — not implemented in EWO-008 owned scope.

**CoachMark step 2/3:** Require WritingWorkspace and ContextBar mounted on target routes (already present from EWO-001…007).

---

## Constraints verified

- ADR-0036 six primary routes unchanged ✅  
- IR-5 Italian operator copy / English nav labels ✅  
- `prefers-reduced-motion` honored in CoachMark and CommandPalette ✅  
- No feature-internal edits (writing/sources/review modules) ✅  

---

## WO-TRACE

```text
PX2-EWO-001…007 → PX2-EWO-008 ✅ → QWO-PX2-001
```
