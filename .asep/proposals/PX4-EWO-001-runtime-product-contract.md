# Engineering WorkOrder Proposal — PX4-EWO-001

> **Status:** **AUTHORIZED** — `.asep/reports/PX4-AUTHORIZATION-20260706.md`
> **Date:** 2026-07-06
>
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Milestone:** PX-4 — Knowledge  
> **Phase:** Phase 0 — Product-Runtime Integration Contract  
> **SoR:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` revision 2026-07-05  
> **Runtime baseline:** `mb2-complete` @ `3957c94`

```yaml
platform_contract:
  classification_schema: platform-contract-v1
  classification_mode: prospective
  classification_pass: px4-20260706-v1
  classified_on: 2026-07-06
  category: A
  hypothesis_id: n/a
  success_metric: "Signed product-runtime contract accepted by Architect and runtime team"
  exit_id: n/a
  program_mode: product
```

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX4-EWO-001 |
| **Type** | EWO — Product / Contract |
| **EWO category** | Alignment |
| **Layer** | Business + Runtime boundary |
| **Lifecycle transition** | `proposed` → `authorized` → `done` (contract accepted) |

---

## Objective

Define, document, and ratify the **integration contract** between the ThesisOS Product Plane (`backend/app/`, `frontend/`) and the MB2 Engineering Runtime (`builder_engine/`).

This EWO does **not** implement product features. It produces the normative document that all subsequent PX-4 EWOs must follow when consuming runtime services.

---

## SoR mapping

| SoR section | Requirement | PX4-EWO-001 deliverable |
|-------------|-------------|------------------------|
| §6 Event model | Product may publish/subscribe to runtime events | Event taxonomy for product-runtime boundary |
| §9 Projection model | Projection is read-only | Product UI reads projection only; no scheduling logic |
| §10 Supervisor | Product observes Supervisor state | Supervisor state propagation contract |
| §13 Promotion | Product programs use runtime for execution | Integration contract enables future §13.3 evidence |
| ADR-0042 | Two-layer split | Clear boundary: Governance/Runtime/Product layers |

---

## Scope

### In scope

1. **Runtime API surface for product**
   - Event subscription interface (read-only)
   - Projection query interface
   - Supervisor state observation interface
   - Program lifecycle query interface

2. **Product-to-runtime contracts**
   - Which product actions may trigger runtime events
   - Which runtime events the product may react to
   - Payload schemas for cross-boundary events

3. **Ownership matrix**
   - Who owns `backend/app/` runtime client
   - Who owns frontend projection consumers
   - Who owns runtime-side product-facing adapters

4. **Security & isolation**
   - Product cannot mutate runtime checkpoint
   - Product cannot bypass Supervisor WAIT
   - Product cannot invoke plugin execution directly

5. **Error handling contract**
   - RuntimeEscalated → product-visible error state
   - Projection stale/mismatch → graceful degradation

6. **Deliverables**
   - `docs/product/runtime-integration-contract.md` (normative)
   - `.asep/reports/PX4-EWO-001-runtime-product-contract.md` (PASS report)
   - Interface stubs (optional, contract-only)

### Out of scope

- Implementation of product features in PX-4
- Changes to MB2 runtime internals
- Phase 2 plugin development
- SoR/Constitution modifications
- MB2 re-qualification

---

## Product-runtime contract (draft — to be ratified)

### Event boundary

Product plane may **consume** (subscribe):
- `ProjectionUpdated`
- `RuntimeEscalated`
- `WaveAdvanced`
- `QwoPassed` / `QwoFailed`

Product plane may **produce** (publish):
- `StateObserved` (read-only snapshot from product)
- `CycleStarted` / `CycleHalted` (user-triggered cycles)

Product plane may **not** produce:
- `JobClaimed`, `WorkerDispatched`, `MergeCompleted`, etc. (runtime-only)

### Projection boundary

Product UI reads from:
- `.builder-engine/projection.json` or runtime projection API
- No direct event log parsing in UI
- No scheduling decisions in UI

### Supervisor boundary

Product observes Supervisor state via projection:
- `WAIT` → UI shows pause/block
- `APPROVED` → UI allows progression
- `STOP` → UI shows error/block

Product cannot mutate Supervisor state.

---

## Dependencies

| Depends on | Status |
|------------|--------|
| MB2 promoted (`mb2-complete`) | ✅ PASS @ 3957c94 |
| PX-3 Sources in progress | ✅ active |
| SoR frozen @ 2026-07-05 | ✅ frozen |
| Product Constitution frozen | ✅ frozen |
| Runtime Constitution frozen | ✅ frozen |

---

## Acceptance criteria

- [x] Runtime integration contract document drafted
- [x] Event taxonomy approved by Architect
- [x] Projection read-only boundary approved
- [x] Supervisor observation contract approved
- [x] Ownership matrix signed off
- [x] No MB2 runtime internals modified
- [x] No SoR/Constitution modifications
- [x] EWO report filed with verdict PASS
- [x] Contract accepted by product and runtime teams

---

## Forbidden paths

```text
builder_engine/events.py          # runtime-owned
builder_engine/scheduler.py       # runtime-owned
builder_engine/rules.py           # runtime-owned
builder_engine/job_queue.py       # runtime-owned
builder_engine/dependency.py      # runtime-owned
builder_engine/plugin_registry.py # runtime-owned
docs/superpowers/specs/mb2-engineering-runtime-spec.md  # SoR — no edits
docs/runtime-constitution.md      # Constitution — no edits
```

---

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-P4-001 | Contract too restrictive → product cannot evolve | Medium | High | Versioned contract; amendments via Architect |
| R-P4-002 | Product team bypasses runtime → silent state drift | Medium | High | Clear ownership + code review gates |
| R-P4-003 | Runtime changes break product contract | Low | High | Contract pinned to MB2 tag; runtime changes require new contract version |
| R-P4-004 | Projection read-only boundary violated | Low | High | Static checks + ADR-0042 review |

---

## WO-TRACE

```text
MB2 promoted @ mb2-complete
  → PX-3 Sources active
  → PX4-EWO-001 runtime-product contract (this proposal)
  → Architect authorization
  → Contract ratified
  → PX-4 feature EWOs authorized with runtime contract as binding spec
```
