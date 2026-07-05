# PX2-EWO-006 — Session Continuity

**WorkOrder:** PX2-EWO-006  
**Date:** 2026-07-04  
**Sub-agent:** F  
**Verdict:** **IMPLEMENTED**

---

## Deliverables

| Artifact | Path |
|----------|------|
| Session state + URL serialize | `frontend/lib/sessionState.ts` |
| Continua deep link | `frontend/lib/continuaLink.ts` |
| Session chip | `frontend/components/chrome/SessionChip.tsx` |
| Proposal bundle modal (OR-7) | `frontend/components/memory/ProposalBundleModal.tsx` |
| Home Continua + activity + badge | `frontend/components/HomeView.tsx` |
| Project context constant | `frontend/lib/projectContext.ts` |
| Bundle schemas | `backend/app/schemas/memory.py` |
| Tests | `sessionState.test.ts`, `continuaLink.test.ts`, `ProposalBundleModal.test.tsx`, `HomeView.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| AC-9 Continua restores chapter, section, panel tab | **PASS** |
| AC-10 Session close atomic proposal bundle | **PASS** |
| URL query params restore writing workspace state | **PASS** |
| SessionChip shows duration and pending count | **PASS** |
| Activity feed shows proposal/decision/source types | **PASS** |
| Nav badge for pending proposals | **PASS** (Home header + export for AppShell) |
| Tests + CI | **PASS** (see CI) |

---

## Component Summary

### sessionState.ts

- `parseWritingUrlState` / `serializeWritingUrlState` — `section`, `source`, `panel` query params + optional `#section-*` hash
- `loadSessionState` / `saveSessionState` — localStorage key `thesisos:session-state` (chapter, section, scroll, panel tab, source, startedAt)
- `readPendingProposals` — prefers `@/lib/proposalQueue.listPendingProposals()` when PX2-EWO-003 ships; else `thesisos:proposals`
- `resolveProposalBundle(action)` — OR-7 atomic clear; dispatches `thesisos:proposal-bundle-resolved` on approve

### continuaLink.ts

- `buildContinuaLink({ fallback })` — merges persisted session into Continua href/label
- `mergeContinuaTarget(fallback)` — used by HomeView client effect

### SessionChip

- Trailing chrome: `Sessione · {duration} · {count}` (count when > 0)
- Click → `ProposalBundleModal`
- Refreshes every 60s and on bundle resolve

### ProposalBundleModal

- Italian copy: "Chiudi sessione — N modifiche in sospeso"
- OR-7 guard: "Accetta o rifiuta tutte le proposte insieme"
- **Accetta tutte** / **Rifiuta tutte** — no partial apply
- Empty state when queue clear

### HomeView (PX-2 delta)

- Continua CTA uses `mergeContinuaTarget` on mount (client)
- `activityFeed` prop with kinds: `proposal_update`, `binding_decision`, `source_candidate`, `session_bundle`
- Pending proposal pill in header (`home-pending-badge`)
- `getHomeNavProposalBadgeCount()` exported for sidebar wiring

---

## Integration B Wiring (Supervisor / AppShell)

Sub-agent owns SessionChip but **not** `AppShell.tsx`. After wave merge:

### 1. AppShell breadcrumb row — SessionChip

```tsx
import { SessionChip } from "@/components/chrome/SessionChip";

// Trailing breadcrumb row (UI spec §4.1):
<div className="ml-auto flex items-center gap-2">
  <SessionChip />
</div>
```

### 2. Sidebar Home nav badge

```tsx
import { getHomeNavProposalBadgeCount } from "@/components/HomeView";

const pending = getHomeNavProposalBadgeCount();
// Render pill on Home nav item when pending > 0
```

### 3. Writing workspace — persist session on navigation

```tsx
import { saveSessionState } from "@/lib/sessionState";

saveSessionState({
  chapterId,
  chapterTitle,
  section,
  source,
  panel,
  scrollY: window.scrollY,
  route: pathname,
});
```

### 4. Proposal queue (PX2-EWO-003)

When `frontend/lib/proposalQueue.ts` lands, export `listPendingProposals()` — sessionState auto-detects via require. Until then, queue uses `thesisos:proposals` localStorage key.

---

## Backend

Added `ProposalBundle`, `ProposalBundleItem`, `ProposalBundleAction` schemas in `memory.py` for future API bundle endpoint. No MemoryService mutation path yet — frontend OR-7 flow is localStorage-first per PX-2 wave scope.

---

## Regression

- PX-1 Home layout preserved (progress ring, quick actions, activity)
- No edits to forbidden files (MarkdownEditor, SourcePicker, RightRail, ReviewCompare, proposalQueue.ts)
- OR-7 atomicity enforced in modal UI + `resolveProposalBundle`

---

## WO-TRACE

```text
PX2-EWO-002 + PX2-EWO-003 → PX2-EWO-006 → QWO-PX2-001
```
