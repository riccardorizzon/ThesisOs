# OR Baseline Checklist — QWO-PX1-001 Preflight

**WorkOrder:** PX1-EWO-012  
**Purpose:** Reference OR-1…OR-7 migration qualification; QWO-PX1-001 re-runs on live PX-1 stack.

| OR | Capability | Migration status | Log reference | PX-1 re-check |
|----|------------|------------------|---------------|---------------|
| OR-1 | Thesis structure | **PASS** | `C.1-R2.md` | Outline + Home progress widgets |
| OR-2 | STIGMATA framework | **PASS** | `C.2-R2.md` | Context decisions in ContextPacket |
| OR-3 | Corpus boundary | **PASS** | `C.3-R3.md` | corpus_constraints in Context API |
| OR-4 | Constraint compliance | **PASS** | `C.4-R1.md` | Writing rules in context (surface=writing) |
| OR-5 | Decision lifecycle | **PASS** | `C.5-R1.md` | binding decisions in ContextPacket |
| OR-6 | Academic production | **PASS\*** | `C.6-R3.md` | Writing shell (PX-2 full editor deferred) |
| OR-7 | Memory runtime integrity | **PASS** | `C.7-R1.md` | Memory service regression in `make unit` |

**Migration E2E (D.1):** **PASS** — `D.1-E2E.md`, run `e2e-2026-07-01`

**PX-1 product gates (QWO-PX1-001 acceptance):**

- [x] Home default route verified — E2E `px1-ui-smoke.spec.ts`
- [x] Sidebar IA matches ADR-0036 — E2E sidebar test
- [x] Context v0 API returns valid packet — E2E `px1-context-api.spec.ts` (requires `make up`)
- [ ] OR-1…OR-7 regression on **live PX-1 stack** — QWO execution scope (not re-run in EWO-012)
- [x] `make ci` green — integration report evidence

**Note:** EWO-012 proves PX-1 Foundation integration smoke. Full QWO-PX1-001 executes OR regression on the product stack after Supervisor authorization.
