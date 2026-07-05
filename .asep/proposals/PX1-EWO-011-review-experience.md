# Engineering WorkOrder Proposal — PX1-EWO-011

> **Status:** APPROVED (2026-07-03) — Wave B (parallel with 007, 010)

Program: `.asep/programs/thesisos-product-v2.yaml`  
Capability: `px1-ewo-011-review-experience`

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX1-EWO-011 |
| **Sub-agent** | F |
| **Type** | EWO (Alignment) |
| **Milestone** | PX-1 (Review shell) |
| **Depends on** | PX1-EWO-004 (routing) |
| **ADR refs** | ADR-0039, OR-6 |

---

## Objective

Review experience shell — revision workflow placeholder, compare/acceptance UI
stubs. Distinct from `/ai` power mode (ADR-0036).

---

## Ownership (exclusive)

```text
frontend/app/review/**
frontend/components/review/**
frontend/lib/routes.ts              # add /review route entry only
```

**Forbidden:** backend, Writing editor, Context Engine.

---

## Scope

### In scope

- `/review` route (revision mode entry)
- Review panel shell: document selector, diff placeholder, accept/reject stubs
- Link from Home quick action "Revisione" → `/review` (import path update in HomeView — coordinate: **one line** in `HomeView.tsx` quick action href, Supervisor approves)

### Out of scope

- Actual diff engine (PX-2+)
- AI revision execution

---

## Acceptance Criteria

- [ ] `/review` renders review mode shell
- [ ] Workflow steps visible (select → compare → accept stub)
- [ ] No backend changes
- [ ] Tests + build pass

---

## WO-TRACE

```text
PX1-EWO-004 → PX1-EWO-011 (Wave B parallel)
```
