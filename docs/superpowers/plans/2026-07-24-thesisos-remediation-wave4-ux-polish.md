# ThesisOS Remediation Wave 4 — UX Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove first-use blockers, stop advertising incomplete functionality, reduce navigation noise, and make time/progress states understandable.

**Architecture:** Preserve ADR-0036 navigation. UX changes are focused component behaviors with no new top-level modules. High-cardinality lists disable speculative prefetch, while deliberate navigation remains client-side.

**Tech Stack:** React 19, Next.js 15, TypeScript, Vitest, Testing Library, Playwright.

## Global Constraints

- No new primary navigation module.
- `/research/guided` is unavailable, not “coming soon”.
- Accessibility: keyboard, focus, live regions, reduced motion.
- No production code before a failing test.
- Do not create git commits unless explicitly requested.

---

### Task 1: Non-blocking coach marks

**Files:**
- Modify: `frontend/components/onboarding/CoachMark.tsx`
- Modify: `frontend/components/onboarding/CoachMark.test.tsx`
- Modify: `tests/e2e/m7-product-flow.spec.ts`

**Interfaces:**
- Backdrop is visual only and cannot intercept unrelated pointer input.
- Popover controls remain interactive.

- [ ] **Step 1: Write failing component test**

Assert:

```ts
expect(screen.getByTestId("coach-mark-backdrop")).toHaveClass("pointer-events-none");
```

Also require focusable Skip/Next controls and Escape to dismiss through the provider.

- [ ] **Step 2: Run test RED**

```bash
cd frontend && npm test -- components/onboarding/CoachMark.test.tsx
```

- [ ] **Step 3: Implement pointer/focus behavior**

Add `pointer-events-none` to the backdrop, keep the dialog at higher z-index, and add an Escape listener that invokes `onSkip`.

- [ ] **Step 4: Add Playwright empty-state regression**

On a new ephemeral thesis, leave the coach mark open and click “Crea capitolo”. Require the create dialog to open.

- [ ] **Step 5: Run component/E2E GREEN**

Run Step 2 and the focused Playwright test.

### Task 2: Hide guided research

**Files:**
- Modify: `frontend/components/research/ResearchHubPage.tsx`
- Modify: `frontend/components/research/ResearchHubPage.test.tsx`
- Modify: `frontend/app/research/guided/page.tsx`
- Modify: `frontend/lib/routes.ts`
- Modify: `frontend/lib/routes.test.ts`
- Delete only if unused: `frontend/components/research/ResearchGuidedPlaceholder.tsx`

**Interfaces:**
- `/research/guided` redirects to `/research`.
- Research hub advertises only the conceptual map.

- [ ] **Step 1: Write failing tests**

Require:

- no “Esplorazione guidata” card or trail copy;
- product route registry omits `/research/guided`;
- route component calls `redirect("/research")`.

- [ ] **Step 2: Run tests RED**

```bash
cd frontend
npm test -- components/research/ResearchHubPage.test.tsx lib/routes.test.ts
```

- [ ] **Step 3: Implement removal and redirect**

Use Next’s server `redirect("/research")`; do not leave a placeholder view.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 3: High-cardinality prefetch suppression

**Files:**
- Modify: `frontend/components/writing/WritingOutline.tsx`
- Modify: `frontend/components/writing/WritingOutline.test.tsx`
- Modify: `frontend/components/knowledge/shared/KnowledgeObjectCard.tsx`
- Modify: `frontend/components/knowledge/shared/KnowledgeObjectCard.test.tsx`
- Modify: `frontend/components/sources/SourceKnowledgeCard.tsx`

**Interfaces:**
- Chapter and knowledge/source card links set `prefetch={false}`.

- [ ] **Step 1: Write failing link tests**

Mock Next Link or inspect rendered props and require `prefetch={false}` for every mapped chapter/section and knowledge object.

- [ ] **Step 2: Run tests RED**

```bash
cd frontend
npm test -- \
  components/writing/WritingOutline.test.tsx \
  components/knowledge/shared/KnowledgeObjectCard.test.tsx
```

- [ ] **Step 3: Add targeted `prefetch={false}`**

Do not disable prefetch globally. Keep sidebar/module navigation unchanged.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 4: Accurate session duration

**Files:**
- Modify: `frontend/lib/sessionState.ts`
- Modify: `frontend/lib/sessionState.test.ts`
- Modify: `frontend/components/chrome/SessionChip.tsx`
- Create: `frontend/components/chrome/SessionChip.test.tsx`

**Interfaces:**
- Produces:

```ts
export function ensureSessionState(now?: Date): SessionPersistedState;
```

- First minute label: `<1m`.
- Invalid/missing persisted timestamp is initialized, not reported as `0m`.

- [ ] **Step 1: Write failing formatter tests**

Assert:

```ts
expect(formatSessionDuration(start, new Date(startMs + 10_000))).toBe("<1m");
expect(formatSessionDuration(start, new Date(startMs + 60_000))).toBe("1m");
expect(formatSessionDuration(start, new Date(startMs + 3_660_000))).toBe("1h 1m");
```

Invalid timestamps return `null` (or a typed unavailable result), not `0m`.

- [ ] **Step 2: Write failing SessionChip fake-timer test**

With no session storage, render the chip, require `<1m`, advance 60 seconds, require `1m`.

- [ ] **Step 3: Run tests RED**

```bash
cd frontend
npm test -- lib/sessionState.test.ts components/chrome/SessionChip.test.tsx
```

- [ ] **Step 4: Implement initialization and minute-boundary refresh**

Call `ensureSessionState()` on mount. Use a one-minute interval after the initial refresh and clean it up.

- [ ] **Step 5: Run tests GREEN**

Run Step 3. Expected: PASS.

### Task 5: Consistent writing-AI progress and cancellation

**Files:**
- Modify: `frontend/components/writing/WritingAiPanel.tsx`
- Modify: `frontend/components/writing/WritingAiPanel.test.tsx`
- Modify: `frontend/lib/aiActions.ts`

**Interfaces:**
- Streaming copy is “Generazione in corso…”.
- Cancel is visible throughout streaming.
- Abort resets the panel without an error proposal or empty draft.

- [ ] **Step 1: Write failing component tests**

Use a pending mocked stream. Require accessible progress text and an enabled “Interrompi” action; click it and assert the passed signal is aborted.

- [ ] **Step 2: Run test RED**

```bash
cd frontend && npm test -- components/writing/WritingAiPanel.test.tsx
```

- [ ] **Step 3: Implement consistent stream footer**

Keep “Applica” unavailable during streaming. Replace ambiguous “…” with live text and rename the streaming cancel button to “Interrompi”; retain “Annulla” for completed output dismissal if needed.

- [ ] **Step 4: Run test GREEN**

Run Step 2. Expected: PASS.

### Task 6: Product-safe status copy

**Files:**
- Modify: `frontend/components/DocumentErrorBanner.tsx`
- Modify: `frontend/components/writing/DocumentIndexStatusBanner.tsx`
- Modify: `frontend/components/ui/ApiDegradedBanner.tsx`
- Modify relevant tests beside each component.

**Interfaces:**
- Stable code→copy mapping; no backend `error_message` rendered verbatim.

- [ ] **Step 1: Write failing copy tests**

Pass errors containing:

```text
index_failed: LLM wired in M1
pymupdf could not open PDF
Unexpected token '<'
```

Require user copy that explains retry/re-upload and contains none of those strings.

- [ ] **Step 2: Run tests RED**

Run the three focused component suites.

- [ ] **Step 3: Implement code-based mapping**

Map known codes/statuses. Unknown errors use:

```text
Operazione non riuscita. Riprova; se il problema continua, ricarica il documento.
```

Technical details remain in server logs only.

- [ ] **Step 4: Run tests GREEN**

Run Step 2. Expected: PASS.

### Task 7: Wave 4 integration gate

- [ ] **Step 1: Run frontend suite and typecheck**

```bash
cd frontend
npm test
npx tsc --noEmit
npm run build
```

- [ ] **Step 2: Rebuild stack and run UX Playwright**

```bash
docker compose up --build -d
cd tests/e2e
npx playwright test m7-product-flow.spec.ts px1-ui-smoke.spec.ts
```

Require:

- first-use CTA clickable with tutorial visible;
- no guided feature in hub and redirect works;
- no burst of chapter/knowledge prefetch requests;
- session advances under controlled clock/unit evidence;
- chat and writing generation can be interrupted;
- no technical exception strings appear.

- [ ] **Step 3: Inspect scope**

```bash
git diff --check
git status --short
```

Proceed to cleanup only after all Wave 4 evidence is green.
