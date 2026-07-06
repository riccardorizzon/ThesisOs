# Product–Runtime Integration Contract

> **Version:** 1.0  
> **Status:** Ratified (PX4-EWO-001)  
> **Date:** 2026-07-06  
> **Runtime baseline:** `mb2-complete` @ `3957c94`  
> **SoR revision:** 2026-07-05 (`docs/superpowers/specs/mb2-engineering-runtime-spec.md`)  
> **Binding ADR:** ADR-0042 (Governance / Runtime split)

This document is the **normative integration contract** between the ThesisOS **Product
Plane** (`backend/app/`, `frontend/`) and the MB2 **Engineering Runtime**
(`builder_engine/`). All subsequent PX-4+ EWOs that consume runtime services MUST comply
with this contract.

---

## 1. Layer model

```text
ASEP Platform
├── Governance Layer     Program Graph, Supervisor, QC, policies
├── Runtime Layer        Event Bus, Rule Engine, Scheduler, Plugins, Projection
└── Product Plane        backend/app/, frontend/ — user-facing ThesisOS
```

| Layer | Owns | Must not |
|-------|------|----------|
| **Governance** | Program Graph, authorization, freeze/qualify decisions | Dispatch agents, merge worktrees, mutate runtime checkpoint |
| **Runtime** | Event log, job queue, plugins, projection rebuild | Override Constitution/ADR/QC; mark milestones qualified |
| **Product** | UX, business APIs, conformance read adapters | Scheduling, plugin execution, checkpoint writes, Supervisor mutation |

**Hard boundary (ADR-0042 §1):** Product observes Runtime through **read-only
projection** and **approved event subscriptions**. Product never becomes a Runtime
plugin or scheduling authority.

---

## 2. Runtime API surface (product-facing)

Product code may integrate through these surfaces only:

| Surface | Location | Access | Purpose |
|---------|----------|--------|---------|
| **Projection query** | `GET /projects/{id}/conformance/projection` (product adapter) or `.builder-engine/projection.json` (CLI/offline) | Read-only | Wave/job/supervisor/gate status for UI |
| **Program Graph query** | `GET /projects/{id}/conformance/program-graph` | Read-only | EWO nodes, deps, wave membership (PX-3 pattern) |
| **Event subscription** | Product event bus adapter (future) or polling on `ProjectionUpdated` | Subscribe only | React to runtime state changes |
| **State observation** | `StateObserved` publish (see §3) | Publish (read-only snapshot) | Feed product context into engineering cycle |

Product MUST NOT call `builder-engine` CLI dispatch, merge, or plugin APIs directly from
`frontend/` or user-triggered `backend/app/` routes.

---

## 3. Event boundary

### 3.1 Payload minimum (SoR §6.4)

All cross-boundary events MUST include:

```yaml
type: string
timestamp: ISO8601
cycle_id: string?
program_id: string
payload: object
```

### 3.2 Product may consume (subscribe)

| Event | Product reaction | UI mapping |
|-------|------------------|------------|
| `ProjectionUpdated` | Refresh projection consumers | Re-fetch projection; update badges |
| `RuntimeEscalated` | Show error/block state | Supervisor `WAIT` or `STOP` indicator |
| `WaveAdvanced` | Update wave progress | Wave status chip |
| `QwoPassed` | Show qualification success | Gate/checkmark in trace UI |
| `QwoFailed` | Show qualification failure | Block indicator; link to report |

### 3.3 Product may produce (publish)

| Event | When | Constraints |
|-------|------|-------------|
| `StateObserved` | Product emits read-only snapshot (context, surface state) | No scheduling side effects |
| `CycleStarted` | Operator explicitly starts an engineering cycle from product UI | Requires Governance authorization scope |
| `CycleHalted` | Operator halts cycle from product UI | Must not bypass Supervisor `WAIT` |

### 3.4 Product must not produce (runtime-only)

```text
JobClaimed, WorkerDispatched, MergeCompleted, MergeFailed,
IntegrationStarted, IntegrationPassed, IntegrationFailed,
QwoSpawned, EwoCompleted, ExecutionGraphDerived,
JobReady, PolicyAllowed, PolicyBlocked, Replanned, …
```

Full catalog: SoR §6.2–§6.3. New event types require SoR amendment — not product-side
invention.

---

## 4. Projection boundary (SoR §9, INV-R-11)

### 4.1 Read sources

Product UI and `backend/app/` adapters read projection from:

1. **Preferred:** product conformance API (`GET …/conformance/projection`) — rebuilds
   from Program Graph + parallel program YAML (deterministic, MB2-Q5 aligned).
2. **Alternative:** `.builder-engine/projection.json` — offline/CLI parity only; not
   parsed directly in browser.

### 4.2 Consumer rules

| Allowed | Forbidden |
|---------|-----------|
| Render `supervisor.state`, `waves`, `jobs`, `gates` | Compute ready-set or critical path |
| Display job/wave/integration/QWO status | Dispatch, merge, or claim jobs |
| Snapshot projection for reports | Mutate queue or checkpoint |
| Poll or subscribe on `ProjectionUpdated` | Parse raw `.builder-engine/events.jsonl` in UI |

### 4.3 Staleness and mismatch

| Condition | Required product behavior |
|-----------|---------------------------|
| Projection `derived_at` older than threshold (configurable, default 60s) | Show stale indicator; re-fetch; degrade to last-known-good |
| Projection rebuild fails (5xx) | Graceful empty state + retry; no fabricated status |
| Checkpoint/projection mismatch (RuntimeEscalated) | Block progression UI; surface escalation reason |

---

## 5. Supervisor boundary (SoR §10, INV-R-16/17)

Product observes Supervisor state **only** via `projection.supervisor`:

| `supervisor.state` | Product UI behavior |
|--------------------|---------------------|
| `WAIT` | Pause/block autonomous progression; show reason |
| `STOP` | Hard block; show error and escalation link |
| `APPROVED` (delegation active) | Allow operator-initiated progression within scope |
| `IDLE` / `OBSERVE` | Informational; no block |

**Product cannot:**

- Mutate Supervisor state or delegation tokens
- Clear `WAIT` without Governance operator action
- Auto-approve QWO or freeze milestones
- Bypass `RuntimeEscalated` → `WAIT`/`STOP` transitions

---

## 6. Ownership matrix

| Artifact / concern | Owner | Location |
|--------------------|-------|----------|
| Runtime core (bus, rules, scheduler, plugins) | Platform / PX-EXEC | `builder_engine/` |
| Product runtime client (HTTP adapters) | Product milestone EWO | `backend/app/services/conformance/` |
| Frontend projection consumers | Product milestone EWO | `frontend/` components (read-only) |
| Normative contract (this document) | Product Phase 0 | `docs/product/runtime-integration-contract.md` |
| SoR + Runtime Constitution | Governance (frozen) | `docs/superpowers/specs/…`, `docs/runtime-constitution.md` |
| Program Graph | Governance | `.asep/programs/*.yaml` |
| Event log + checkpoint | Runtime | `.builder-engine/events.jsonl`, checkpoint files |

**Code review gate:** Any PR touching `backend/app/` runtime adapters MUST declare layer
(Business | Runtime | Infrastructure per ADR-0030 §4) and cite this contract version.

---

## 7. Security and isolation

| Rule | Enforcement |
|------|-------------|
| Product cannot mutate runtime checkpoint | No writes to `.builder-engine/` from `backend/app/` |
| Product cannot bypass Supervisor `WAIT` | UI blocks progression; no dispatch routes |
| Product cannot invoke plugin execution | No imports of `builder_engine.scheduler`, `merge`, etc. from `backend/app/` |
| Runtime cannot import product | `builder_engine/` MUST NOT `import backend.app` (existing isolation gate) |
| Architecture boundary | ADR-0042 two-layer split; Constitution C1–C8 |

---

## 8. Error handling contract

| Runtime signal | Product-visible state | Recovery |
|----------------|----------------------|----------|
| `RuntimeEscalated` | Error banner + Supervisor block | Operator resolves via Governance; product re-fetches projection |
| `QwoFailed` | Qualification failure in trace UI | Link to QWO report; hold wave display |
| Projection stale | Yellow stale badge | Auto re-fetch on `ProjectionUpdated` or interval |
| API unreachable | Empty/degraded shell | Retry with backoff; never show synthetic PASS |

---

## 9. Versioning and amendments

| Field | Value |
|-------|-------|
| Contract version | `1.0` |
| Pinned runtime tag | `mb2-complete` @ `3957c94` |
| Pinned SoR revision | `2026-07-05` |

Amendments require Architect authorization and a new contract version bump. Runtime tag or
SoR revision changes without contract update are **forbidden** for product integration work.

---

## 10. Compliance checklist (PX-4+ EWOs)

Before merging any PX-4+ EWO that touches runtime integration:

- [ ] Events used are in §3.2 or §3.3 allow-lists
- [ ] No §3.4 forbidden events emitted from product
- [ ] Projection consumed read-only per §4
- [ ] Supervisor observed via projection only per §5
- [ ] No forbidden paths modified (`builder_engine/` core modules)
- [ ] Layer declared on PR per ADR-0030
- [ ] `make ci` green; PX-2/PX-3 regression preserved

---

## WO-TRACE

```text
MB2 promoted @ mb2-complete
  → PX4-EWO-001 authorization
  → runtime-integration-contract.md v1.0 (this document)
  → PX-4 feature EWOs (future — separate authorization)
```

---

## Sign-off

```text
Contract:     runtime-integration-contract v1.0
EWO:          PX4-EWO-001
Milestone:    PX-4 Phase 0
Report:       .asep/reports/PX4-EWO-001-runtime-product-contract.md
Architect:    ratified via ASEP execution 2026-07-06
```
