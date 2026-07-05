# PX1-EWO-002 — Design System Tokens and Core Components

**WorkOrder:** PX1-EWO-002  
**Type:** EWO (Infrastructure)  
**Milestone:** PX-1 Foundation  
**Date:** 2026-07-03  
**Verdict:** **IMPLEMENTED**

---

## Objective

Establish design system v1 with semantic tokens and core component stubs for Home
and module surfaces.

---

## Deliverables

| Artifact | Path |
|----------|------|
| Token documentation | `docs/product/design-system-v1.md` |
| CSS tokens | `frontend/styles/tokens.css` |
| Tailwind mapping | `frontend/tailwind.config.ts` |
| Global styles | `frontend/app/globals.css` |
| ProgressRing | `frontend/components/ProgressRing.tsx` |
| EntityCard | `frontend/components/EntityCard.tsx` |
| AppShell (tokenized) | `frontend/components/AppShell.tsx` |
| Utility | `frontend/lib/cn.ts` |
| Tests | `ProgressRing.test.tsx`, `EntityCard.test.tsx` |

---

## Acceptance Criteria

| Criterion | Result |
|-----------|--------|
| Design tokens documented (color, type, spacing) | **PASS** |
| AppShell uses semantic tokens | **PASS** |
| ProgressRing stub | **PASS** |
| EntityCard stub | **PASS** |
| `npm test` + `npm run build` | **PASS** (53 tests) |

---

## Design decisions

- **Palette:** Stone neutrals + ink-blue accent — research workspace, not chat-app
- **Typography:** System UI stack v1 (no font CDN)
- **ProgressRing:** Accepts deterministic `value` 0–100 per ADR-0040 INV-PS-1
- **EntityCard:** Italian type labels (Capitolo, Fonte, …) for operator locale

---

## Next Ready

| ID | Title | Status |
|----|-------|--------|
| **PX1-EWO-003** | Home page | **ready** |
| PX1-EWO-004 | Product routing | ready |
| PX1-EWO-005 | Context Engine v0 | ready |
| PX1-EWO-006 | Project scope | ready |

---

## WO-TRACE

```text
PX1-EWO-001 → PX1-EWO-002 → PX1-EWO-003 (Home + ProgressRing)
```
