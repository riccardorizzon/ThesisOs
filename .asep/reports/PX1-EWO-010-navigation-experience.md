# PX1-EWO-010 — Navigation Experience

**WorkOrder:** PX1-EWO-010  
**Sub-agent:** E  
**Type:** EWO (Infrastructure)  
**Milestone:** PX-1 Foundation  
**Date:** 2026-07-03  
**Depends on:** PX1-EWO-006 (ProjectContext)  
**Verdict:** **IMPLEMENTED** (frontend scope)

---

## Objective

Navigation experience enhancements — route-aware breadcrumbs, project switcher stub,
workspace nav helper. Minimal AppShell integration without sidebar IA changes.

---

## Deliverables

| Artifact | Path |
|----------|------|
| Breadcrumbs component | `frontend/components/navigation/Breadcrumbs.tsx` |
| ProjectSwitcher stub | `frontend/components/navigation/ProjectSwitcher.tsx` |
| WorkspaceNav stub | `frontend/components/navigation/WorkspaceNav.tsx` |
| Barrel export | `frontend/components/navigation/index.ts` |
| Breadcrumb helpers | `frontend/lib/nav.ts` (`buildBreadcrumbs`, `formatBreadcrumbLabel`, `shouldShowBreadcrumbs`) |
| AppShell integration | `frontend/components/AppShell.tsx` (+11 line integration diff vs EWO-001 base) |
| Unit tests | `frontend/lib/nav.test.ts`, `frontend/components/navigation/*.test.tsx`, `frontend/components/AppShell.test.tsx` |
| Proposal | `.asep/proposals/PX1-EWO-010-navigation-experience.md` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Breadcrumbs on module routes (Writing, Sources, Knowledge) | **PASS** |
| Breadcrumbs on nested dynamic routes (`/writing/[id]`, `/sources/[id]`, `/knowledge/[id]`, `/research/[id]`) | **PASS** |
| Project switcher shows current `project_id` stub (`thesis-agent`) | **PASS** |
| AppShell integration diff ≤ 30 lines | **PASS** (11 lines vs EWO-001 AppShell base) |
| Sidebar IA unchanged (ADR-0036 `PRIMARY_NAV`) | **PASS** |
| Frontend tests pass | **PASS** (90/90) |
| `make ci` full gate | **FAIL** — backend unit (pre-existing; see Regression) |

---

## Implementation Notes

### `buildBreadcrumbs(pathname)`

- Returns `[]` on `/` (Home has no breadcrumb bar).
- Module roots (`/writing`, `/sources`, `/knowledge`, `/research`, `/settings`) → single segment with module label from `PRIMARY_NAV`.
- Nested paths → parent module link + humanized dynamic segments (`ch-1` → `ch 1`).
- `PRIMARY_NAV` frozen per ADR-0036 — no sidebar IA edits.

### AppShell integration (11 lines)

1. Import `Breadcrumbs`, `ProjectSwitcher` from `@/components/navigation`.
2. `ProjectSwitcher` in sidebar header below ThesisOS title.
3. `Breadcrumbs` in a bar above main content (`border-b` strip); page content unchanged in `p-6` wrapper.

### ProjectSwitcher

- Reads `defaultProjectContext()` from EWO-006 (`project_id: thesis-agent`).
- Disabled button stub; multi-project selection deferred to PX-2+.

### WorkspaceNav

- Optional stub exported for future workspace sub-nav; renders workspace id when provided, otherwise `null`. Not wired into AppShell in PX-1 (no workspace scope in shell yet).

---

## Layer Declaration

**Business** — Product Plane (`frontend/components/navigation/**`, `frontend/lib/nav.ts`, `AppShell` integration).

---

## Regression / CI Evidence

| Gate | Result |
|------|--------|
| `make lint` | **PASS** |
| `make typecheck` | **PASS** |
| `make unit-frontend` | **PASS** (90 tests, 23 files) |
| `make unit-builder-engine` | **PASS** (65 tests) |
| `make drift` | **PASS** |
| `make scope` | **PASS** (informational) |
| `make isolation` | **PASS** |
| `make unit` (backend) | **FAIL** (20 failed — pre-existing on branch; `test_context_api.py` `PromptContextFilters.include_binding_decisions` AttributeError; DB deadlock/FK flakes in integration tests) |

**Note:** Worktree branch `builder/px1-ewo-010` lacks committed EWO-001/002 foundation files (`cn.ts`, `EntityCard`, `ModuleStub`). Copied from main workspace working tree to unblock frontend typecheck for parallel agents' dependent components. Supervisor should merge EWO-001→005 foundation before final integration.

---

## ADR Compliance

- **ADR-0036 INV-IA-1:** `PRIMARY_NAV` unchanged; breadcrumbs derive labels from frozen IA map.
- **ADR-0040 INV-PS-5:** ProjectSwitcher consumes `defaultProjectContext()` / EWO-006 helper only (no backend schema changes).

---

## Merge Readiness

**Conditional yes** — EWO-010 frontend deliverables complete and tested.

| Blocker | Owner |
|---------|-------|
| Backend `make unit` failures (`test_context_api.py`, integration DB flakes) | Pre-existing on `builder/px1-ewo-010` branch — not introduced by EWO-010 |
| `layout.tsx` still uses legacy inline nav (not AppShell) | Out of EWO-010 scope — integrate at supervisor merge with EWO-001/004 |
| Foundation files (`cn.ts`, design tokens) uncommitted on branch | EWO-001/002 merge prerequisite |

---

## WO-TRACE

```text
PX1-EWO-006 → PX1-EWO-010 → PX1-EWO-012 (integration) → QWO-PX1-001
```
