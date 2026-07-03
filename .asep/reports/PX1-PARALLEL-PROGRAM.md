# PX1 Parallel Engineering Program

> **Status:** ACTIVE (2026-07-03)  
> **Supervisor mode:** Engineering Supervisor — coordinates, does not implement  
> **Program:** `.asep/programs/thesisos-product-v2.yaml` + `.asep/programs/px1-parallel.yaml`

---

## Purpose

PX-1 Foundation completes through **parallel sub-agents**, each with exclusive
bounded context ownership. Convergence gate: **QWO-PX1-001** (via PX1-EWO-012).

EWO-001…005 are **implemented**. Remaining PX-1 work splits into six EWOs + one
integration EWO.

---

## Supervisor responsibilities

| Does | Does not |
|------|----------|
| Maintains Capability Graph | Write application code |
| Approves / records Proposals | Change ADRs or architecture |
| Assigns sub-agent ownership | Modify another EWO's files |
| Sets merge order + wave barriers | Skip CI after merge |
| Integrates PRs / worktree merges | Auto-accept QWO PARTIAL |
| Runs QWO-PX1-001 | Redesign Context Engine |

State machine: `.asep/governance/engineering-supervisor.md`

---

## Parallel graph

```text
                         Supervisor
                              │
        ┌──────────┬─────────┼─────────┬──────────┐
        │          │         │         │          │
   Wave A (parallel — disjoint ownership)
        │          │         │         │          │
     EWO-006    EWO-008   EWO-009      │          │
   Project     Library    Context      │          │
   Context      UX         Viz UI      │          │
        │          │         │         │          │
        └──────────┴────┬────┴─────────┘          │
                        │ merge barrier Wave A      │
        ┌───────────────┼───────────────┐           │
        │               │               │           │
   Wave B (parallel — after Wave A deps)
        │               │               │           │
     EWO-007        EWO-010        EWO-011         │
   Writing UI     Navigation      Review UX         │
        │               │               │           │
        └───────────────┴───────┬───────┘           │
                                │ merge barrier Wave B
                           EWO-012
                      Qualification &
                      Integration
                                │
                         QWO-PX1-001
                                │
                           PX-1 PASS
```

---

## Merge order (strict)

```text
006 → 009 → 007 → 008 → 010 → 011 → 012 → QWO-PX1-001
```

| Order | EWO | Rationale |
|-------|-----|-----------|
| 1 | **006** | ProjectContext foundation — all routes consume |
| 2 | **009** | Relocate ContextBar → `components/context/` |
| 3 | **007** | Writing layout imports ContextBar from 009 |
| 4 | **008** | Library UX — independent of Writing |
| 5 | **010** | Navigation + project switcher consumes 006 |
| 6 | **011** | Review mode — independent surface |
| 7 | **012** | E2E + integration evidence → QWO |

**Wave A execute in parallel:** 006, 008, 009 (disjoint paths).  
**Wave B execute in parallel:** 007, 010, 011 (after Wave A merged per deps above).

---

## Sub-agent registry

### Sub-agent A — PX1-EWO-006 Project Context

**Ownership (exclusive write):**

```text
backend/app/schemas/context.py          # ProjectContext fields only
backend/app/api/projects.py             # session/workspace query wiring
backend/app/services/context/           # project resolution stub only
frontend/lib/projectContext.ts          # NEW — shared helper
frontend/lib/contextClient.ts           # ProjectContext types + client
frontend/lib/contextLoad.ts             # uses projectContext helper
```

**Must NOT touch:** `frontend/components/**`, `frontend/app/**` pages, ContextBar.

**Deliverables:** Proposal → Implementation → Evidence → Tests → Report

---

### Sub-agent B — PX1-EWO-007 Writing Workspace

**Ownership (exclusive write):**

```text
frontend/app/writing/**
frontend/components/writing/**          # NEW
```

**Must NOT touch:** backend, ContextBar implementation (import only from `@/components/context`).

**Depends on:** EWO-009 merged (ContextBar path).

**Scope:** Three-panel layout shell, outline placeholder, editor placeholder, AI panel slot, responsive. PX-2 full editor deferred — this is **layout shell** for PX-1.

---

### Sub-agent C — PX1-EWO-008 Library Experience

**Ownership (exclusive write):**

```text
frontend/app/sources/**
frontend/app/knowledge/**
frontend/components/library/**          # NEW
frontend/lib/libraryStub.ts             # NEW — stub data
```

**Must NOT touch:** Context Engine, backend, Writing, Navigation core.

**Scope:** Sources list/cards, filters stub, knowledge explorer cards, navigation between sources ↔ knowledge. Consumes existing EntityCard + design tokens.

---

### Sub-agent D — PX1-EWO-009 Context Visualization

**Ownership (exclusive write):**

```text
frontend/components/context/**          # NEW — migrate ContextBar here
frontend/components/ContextBar.tsx      # DELETE after migrate
frontend/components/ContextBar.test.tsx # MOVE to context/
```

**Must NOT touch:** backend, Writing layout, API schemas.

**Scope:** ContextBar, constraint chips, decision badges, active-corpus indicators. **View only** — no assembly logic.

**Note:** Updates import paths in Writing pages (`app/writing/**`) — coordinate with Supervisor at merge; Sub-agent D owns those import line changes only.

---

### Sub-agent E — PX1-EWO-010 Navigation Experience

**Ownership (exclusive write):**

```text
frontend/components/navigation/**       # NEW
frontend/lib/nav.ts                     # breadcrumbs, switcher helpers
frontend/components/AppShell.tsx        # integration hooks ONLY (minimal diff)
```

**Must NOT touch:** backend, module page content, Context Engine.

**Depends on:** EWO-006 merged (project switcher).

**Scope:** Breadcrumbs, project switcher stub, workspace nav enhancements. AppShell changes limited to importing navigation subcomponents.

---

### Sub-agent F — PX1-EWO-011 Review Experience

**Ownership (exclusive write):**

```text
frontend/app/review/**                  # NEW route
frontend/components/review/**           # NEW
```

**Must NOT touch:** backend, Writing editor, Context Engine.

**Scope:** Review mode shell, revision workflow placeholder, compare/acceptance UI stubs per Spec §5.6 / ADR-0039 action model preview.

---

### Sub-agent G — PX1-EWO-012 Qualification & Integration

**Ownership (exclusive write):**

```text
tests/e2e/**                            # NEW or extend
frontend/playwright.config.ts           # if new
.asep/reports/PX1-EWO-012-*.md
.asep/certificates/PX1-EWO-012-*.yaml
```

**Must NOT touch:** product feature code (tests + reports only).

**Scope:** E2E smoke (Home, Writing, Sources, Context API), visual regression stubs, integration evidence for QWO-PX1-001. Runs `make ci` + OR baseline checklist.

---

## Sub-agent rules (all)

1. **NO** architecture changes  
2. **NO** Capability Graph edits (Supervisor only)  
3. **NO** ADR changes  
4. **NO** API schema changes outside owned paths  
5. **NO** cross-EWO file edits  
6. **YES** Proposal → Implementation → Evidence → Tests → Report  
7. **YES** `make ci` green before handoff  
8. **YES** declare layer: Business (Product Plane) on PR  

---

## Dispatch prompts

Copy-paste to spawn a sub-agent. Replace `{EWO}` with the work order id.

```text
You are Sub-agent for {EWO} in the PX1 Parallel Engineering Program.

Read FIRST:
- .asep/reports/PX1-PARALLEL-PROGRAM.md (your ownership section)
- .asep/proposals/{EWO}-*.md
- .asep/capabilities/thesisos-product-v2.yaml (your node only)

Rules:
- Exclusive ownership — do NOT edit files outside your bounded context
- Do NOT change architecture, ADRs, or Capability Graph
- Produce: Proposal (if missing) → Implementation → Tests → Report (.asep/reports/)
- make ci must pass before completion
- Match existing design tokens and component patterns

When done, output:
- Files changed (list)
- Tests run (evidence)
- Report path
- Merge readiness: yes/no + blockers
```

---

## Current state (Supervisor OBSERVE)

| EWO | Status | Ready |
|-----|--------|-------|
| 001–005 | implemented | — |
| **006** | **merged** | Wave A |
| **008** | **merged** | Wave A |
| **009** | **merged** | Wave A |
| **007** | **merged** | Wave B @ `543d870` |
| **010** | **merged** | Wave B @ `c99f7db` |
| **011** | **merged** | Wave B @ `89c0824` |
| **012** | **ready** | **Wave C** — dispatch Sub-agent G |
| QWO-PX1-001 | blocked | blocked until 012 |

**Wave A handoff:** `.asep/reports/PX1-WAVE-A-handoff.md` (2026-07-03)  
**Wave B handoff:** `.asep/reports/PX1-WAVE-B-handoff.md` — **barrier PASS** @ `89c0824`, `make ci` PASS (2026-07-03)

---

## WO-TRACE

```text
PX1-EWO-005 (Context Graph) → PX1 Parallel Program → Wave A → Wave B → EWO-012 → QWO-PX1-001
```
