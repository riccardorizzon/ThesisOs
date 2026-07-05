# Engineering WorkOrder Proposal — PX2-EWO-001

> **Status:** ⏳ **PROPOSED** — dispatch blocked until `EXECUTION-AUTHORIZATION-PX2-AMENDMENT` ratified.
>
> Program: `.asep/programs/thesisos-product-v2.yaml`  
> Capability: `px2-ewo-001-contextbar-inspector`  
> Spec: `docs/product/specs/px2-research-workspace-experience.md` §4.2, §6.1  
> UI: `design-system/thesisos/px2-research-workspace-ui-spec.md` §4.2, §5.4

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX2-EWO-001 |
| **Sub-agent** | A |
| **Type** | **EWO** — Grounding |
| **EWO category** | **Grounding** |
| **Capability** | `px2-ewo-001-contextbar-inspector` |
| **User capability** | **PX-2.1** Context Awareness |
| **Milestone** | PX-2 Research Workspace Experience |
| **Layer** | Business (Product Plane — `frontend/` + context API extension) |
| **Wave** | px2-parallel/wave_a |
| **Lifecycle transition** | `approved` → `implemented` (on success) |

---

## Objective

Activate **live ContextBar** with selection-scoped counts from Context Packet assembly
and deliver **Context Inspector** (Contesto tab) with human-readable scope, constraints,
definitions, and sources — no OR jargon or raw JSON.

---

## Ownership (exclusive)

```text
frontend/components/context/ContextBar.tsx
frontend/components/context/ContextInspector.tsx
frontend/components/context/ContextSummary.tsx (extend)
frontend/lib/contextClient.ts (extend query params)
frontend/lib/contextLoad.ts
backend/app/api/projects.py (context endpoint query params only)
backend/app/services/context/service.py
backend/app/services/context/present.py
backend/app/schemas/context.py (non-breaking extensions)
```

**Forbidden:** `components/writing/**`, `components/sources/**`, `components/decisions/**`,
graph nodes, memory services.

---

## Scope

### In scope

1. **ContextBar live counts** — `[ Cap. 3 · §3.2 ]  12 fonti · 4 decisioni · 18 voci · 34 citazioni`
2. **Skeleton → content crossfade** (150ms); editor never blocked while loading
3. **Click targets** — scope chip scrolls outline; counts open Contesto tab
4. **ContextInspector accordion** — scope, corpus constraints, definitions, relevant sources, writing rules (collapsed)
5. **Context API extension** — `entity_id`, `selection_anchor` query params for scoped packet
6. **Layout tokens** — `--contextbar-height`, compact row per UI spec §1.1
7. **Amber warning hook** — CSS/state slot for binding decision (populated by PX2-EWO-005)

### Out of scope

- DecisionCard content (PX2-EWO-005)
- Right rail tab wiring (PX2-EWO-003)
- AI action context injection (PX2-EWO-003)
- New top-level routes

---

## Constraints

- Product Constitution v1.0 + ADR-0038 Context Engine precedence
- IR-3: binding decisions always in packet for AI (packet must include them)
- IR-5: Italian operator copy; English nav unchanged
- PX-1 ContextBar contract preserved — extend, do not replace IA
- Runtime Constitution C1–C8 — context service only; no graph redesign

---

## Acceptance Criteria

- [ ] ContextBar displays live counts matching Context Packet for active chapter + selection (AC-1)
- [ ] ContextBar skeleton → populated crossfade; typing in editor not blocked (spec §18)
- [ ] Scope chip click scrolls outline to section anchor
- [ ] Counts click switches right rail to Contesto tab (hook/event for EWO-003)
- [ ] ContextInspector renders human-readable sections — no raw JSON
- [ ] Context API accepts entity/selection scope; backward compatible with PX-1 clients
- [ ] `npm test`, `npm run build`, backend context tests pass
- [ ] `make ci` green

---

## Tests

- Extend `ContextBar.test.tsx` — live counts, skeleton, click handlers
- New `ContextInspector.test.tsx` — accordion sections, empty state
- Backend: selection-scoped context assembly unit test

---

## Regression

- `make ci`
- PX-1 ContextBar on non-workspace routes unchanged
- OR-1…OR-7 baseline preserved

---

## WO-TRACE

```text
PX-1 COMPLETE → EXECUTION-AUTHORIZATION-PX2-AMENDMENT → PX2-EWO-001 → PX2-EWO-003, PX2-EWO-005
```
