# ASEP — Engineering Runtime Model v2

- **Status:** Frozen (design — 2026-07-05)
- **Scope:** Structural model for Era II Engineering Runtime — **specification only**.
  No implementation authorized until MB2 freeze (see `.asep/programs/px-exec.yaml`).
- **Authority:** ADR-0042. **Normative contract:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` (MB2 SoR). This document is the structural companion map.
- **Companion:** `docs/platform/era-model.md`, `docs/platform/global-state-machine.md`,
  `.asep/programs/px-exec.yaml`

---

## 1. Purpose

v1 defines **what the processor does** (Observe → … → Replan).

v2 defines **how the platform is structured** so that processor scales:

```text
Program Graph        (declarative intent — Governance)
        ↓ derive
Execution Graph      (operational DAG — Runtime)
        ↓ schedule
Job Queue            (EWO instances — Runtime)
        ↓ events
Rule Engine          (reactive actions — Runtime)
        ↓ invoke
Plugins              (Merge, Integration, QWO, …)
        ↓ emit
Projection           (observability — read-only)
```

This document will outlive individual ADRs: it is the **map** MB2 implements.

---

## 2. Platform layers

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        ASEP Platform                                     │
├──────────────────────────────┬──────────────────────────────────────────┤
│     Governance Layer         │           Runtime Layer                   │
│                              │                                           │
│  Program / Capability        │  Event Bus                                │
│  ADR / Constitution           │  Rule Engine                             │
│  Engineering Supervisor      │  Dependency Engine                       │
│  QC Certificates             │  Job Queue + Scheduler                   │
│  QWO contracts               │  Plugin Registry                         │
│  Auto-approval / termination │  State Writer                            │
│                              │  Projection Builder                      │
│  Decides: MAY we proceed?    │  Decides: WHAT runs next?                │
│  States: WAIT, APPROVED, STOP│  States: READY, RUNNING, MERGED, …     │
└──────────────────────────────┴──────────────────────────────────────────┘
                              │
                              ▼
                    Execution Workers (AgentProvider)
                    Cursor Task · human · future providers
```

### 2.1 Delegation contract

| Operator action | Governance | Runtime |
|-----------------|------------|---------|
| `APPROVED` | Authorizes delegated scope for current program phase | May dispatch until next governance gate |
| `STOP` | Halts all autonomous progression | Drains in-flight per policy; no new dispatch |
| `WAIT` (Supervisor) | Session halted pending human | Queue paused; state preserved |
| QWO verdict FAIL | Supervisor → WAIT | QualificationPlugin reports; no retry without rule |

Runtime **never** interprets Constitution or ADR text. It evaluates **Runtime rules**
and **L1 invariants** only. Governance policies are evaluated by Supervisor **before**
delegation and at escalation boundaries.

---

## 3. Program Graph

**Source of truth:** `.asep/programs/*.yaml`, `.asep/proposals/*.md`, capability graphs.

The Program Graph is **declarative** — it describes what the program intends:

```yaml
# Conceptual — px2-parallel is the validated reference pattern
waves:
  wave_b:
    workorders: [PX2-EWO-003, PX2-EWO-004, PX2-EWO-006]
    depends_on: integration_a
    merge_order: [PX2-EWO-003, PX2-EWO-004, PX2-EWO-006]
    execute_in_parallel: true
integrations:
  integration_b:
    depends_on_wave: wave_b
    actions: [merge, wire, make ci, report]
    unblocks: wave_c
qualification:
  QWO-PX2-001:
    unblocks_when: [wave_c, integration_c]
```

### 3.1 Node types

| Node | Governance owner | Runtime treatment |
|------|------------------|-----------------|
| EWO | Proposal + QC | Job template |
| Wave | Program yaml | Parallel job group |
| Integration | Program yaml | Sequential plugin chain |
| QWO | Qualification contract | Job with stricter gates |
| Milestone gate | Program + ADR | Escalation to Supervisor |

### 3.2 Invariants

- **PG-1:** Every Execution Graph node MUST trace to a Program Graph declaration.
- **PG-2:** Program Graph changes require Governance authorization — Runtime cannot mutate.
- **PG-3:** `merge_order` is part of Program Graph; Dependency Engine validates, not invents.

---

## 4. Execution Graph

**Derived** at runtime from Program Graph + current state + event history.

```text
PX2-EWO-001 ──┐
PX2-EWO-002 ──┼──► integration_a ──► PX2-EWO-003 ──┐
PX2-EWO-005 ──┘                                      ├──► integration_b ──► …
                              PX2-EWO-004 ───────────┤
                              PX2-EWO-006 ───────────┘
```

### 4.1 Derivation algorithm (spec)

1. Load Program Graph for active `program_id`.
2. Filter nodes whose `depends_on` / `depends_on_wave` preconditions are `DONE`.
3. Materialize **ready set** for current wave or integration stage.
4. Apply `merge_order` as topological tie-breaker, not dependency invention.
5. Emit `ExecutionGraphDerived` event with snapshot hash.

Dependency Engine owns steps 2–4. Output is immutable for one scheduling cycle.

### 4.2 Relationship to v1 cycle

| v1 phase | v2 primary owner |
|----------|------------------|
| Observe | Projection Builder + State Reader |
| Evaluate Policies | Supervisor (Governance); Runtime evaluates rules only |
| Plan | Dependency Engine → Execution Graph |
| Schedule | Scheduler + Job Queue |
| Execute | AgentProvider |
| Validate | CheckRunner + plugins |
| Merge | MergePlugin |
| Publish Events | Event Bus |
| Update State | State Writer |
| Replan | Rule Engine + Dependency Engine on failure events |

---

## 5. Execution State

Two composed machines — **never merged into one**.

### 5.1 Supervisor FSM (Governance)

Documented in `.asep/governance/engineering-supervisor.md`.

Key terminal-wait state:

```text
WAIT — Human Review; session halted; Runtime queue paused
```

`WAIT` is the proof that Governance is not a script: autonomous progression stops.

### 5.2 Job FSM (Runtime)

Extends ADR-0025 / L2 Task FSM:

```text
CREATED → READY → CLAIMED → RUNNING → VALIDATING → MERGED → DONE
                ↘ FAILED → DEBUGGING → (recovery rule) → READY
                ↘ CANCELLED
```

Qualification jobs add:

```text
… → MERGED → QUALIFYING → QUALIFIED | FAILED
```

| State | Meaning | Typical event |
|-------|---------|---------------|
| READY | Dependencies satisfied; in queue | `JobReady` |
| RUNNING | AgentProvider active | `WorkerDispatched` |
| VALIDATING | Checks running | `ValidationStarted` |
| MERGED | Code integrated per merge policy | `MergeCompleted` |
| QUALIFIED | QWO PASS | `QwoPassed` |

### 5.3 Wave / Integration aggregate state

Projections expose roll-ups — not separate authoritative FSMs:

```yaml
wave_b:
  status: running   # derived: any job RUNNING or VALIDATING
  jobs:
    PX2-EWO-003: running
    PX2-EWO-004: ready
    PX2-EWO-006: ready
integration_b:
  status: locked    # derived: wave_b not complete
qwo:
  QWO-PX2-001:
    status: locked
    unblocks_when: [wave_c, integration_c]
```

Status enum: `waiting | ready | running | pass | fail | locked`.

---

## 6. Event Model

### 6.1 Principles

1. **Typed catalog** — no ad-hoc event names (extends `builder_engine/events.py`).
2. **Append-only log** — authoritative audit trail.
3. **Reactions, not calls** — plugins subscribe via Rule Engine.
4. **At-least-once delivery** — handlers must be idempotent.

### 6.2 Catalog extensions (v2 — design)

| Event | Payload (conceptual) | Typical subscribers |
|-------|----------------------|---------------------|
| `ExecutionGraphDerived` | program_id, ready_set, hash | Scheduler |
| `JobReady` | job_id, ewo_id | Scheduler |
| `WorkerDispatched` | job_id, provider, handle | Metrics |
| `WorkerReported` | job_id, outcome | Validate rules |
| `EwoCompleted` | job_id, report_path | Merge rules |
| `MergeCompleted` | job_id, branch, sha | Integration rules |
| `MergeFailed` | job_id, reason | Replan rules |
| `IntegrationStarted` | integration_id | — |
| `IntegrationPassed` | integration_id, report | QWO rules |
| `IntegrationFailed` | integration_id, reason | Supervisor escalate |
| `QwoSpawned` | qwo_id | QC workflow |
| `QwoPassed` | qwo_id, certificate | Supervisor |
| `QwoFailed` | qwo_id, reason | Supervisor → WAIT |
| `RuntimeEscalated` | reason, context | Supervisor |
| `ProjectionUpdated` | path, version | Dashboard |

v1 catalog events (`TaskScheduled`, `WaveAdvanced`, …) remain valid — v2 extends.

### 6.3 Event → Rule → Action

```text
         ┌─────────────┐
 Event ──►│ Rule Engine │── match? ──► Action descriptor
         └─────────────┘                      │
                │                             ▼
                │                    ┌─────────────────┐
                └─ no match ────────►│ log + continue  │
                                     └─────────────────┘
                                              │
                                              ▼
                                     Plugin Registry.resolve(action)
                                              │
                                              ▼
                                     Plugin.execute(context)
```

Rule format (declarative YAML — illustrative):

```yaml
rules:
  - id: post-ewo-merge
    on: EwoCompleted
    when:
      all_dependencies_satisfied: true
      program_phase: execution
    action:
      plugin: merge
      params: { respect_merge_order: true }

  - id: post-merge-integration
    on: MergeCompleted
    when:
      ci_status: passed
    action:
      plugin: integration
      params: { template: integration_review }

  - id: post-integration-qwo
    on: IntegrationPassed
    when:
      coverage_gate: passed
    action:
      plugin: qualification
      params: { qwo_id: "{{ program.qwo.id }}" }
```

---

## 7. Plugin Architecture

### 7.1 Registry

```text
PluginRegistry
  register(id, interface, version, handler)
  resolve(action_descriptor) → Plugin instance
```

Core knows **interfaces** only:

| Plugin ID | Interface responsibility |
|-----------|-------------------------|
| `scheduler` | Claim jobs, acquire locks, build dispatch manifest |
| `merge` | Git/worktree merge per Program Graph order |
| `integration` | Cross-package wiring checks + CI orchestration |
| `qualification` | Spawn QWO, collect evidence, issue certificate hook |
| `notification` | Operator alerts (WAIT, FAIL) |
| `metrics` | Queue depth, latency, error rate |

### 7.2 Versioning

Plugins declare `plugin_api_version`. Runtime core rejects incompatible versions at
register time — fail closed.

### 7.3 Non-goals

Plugins MUST NOT:

- Write to `backend/app/` or `frontend/` except via delegated worker jobs
- Evaluate Governance policies
- Bypass Supervisor `WAIT`

---

## 8. Job Queue

```text
Queue
  ├── pending[]     READY jobs ordered by Execution Graph
  ├── in_flight[]   CLAIMED | RUNNING | VALIDATING
  ├── completed[]   MERGED | DONE | QUALIFIED (retention policy)
  └── failed[]      FAILED | DEBUGGING
```

### 8.1 Properties

- **Durability:** queue state recoverable from event log + checkpoint
- **Fairness:** single-program default; Phase 4 adds program-scoped queues
- **Retry:** `FAILED → READY` only via explicit recovery rule or operator action
- **Idempotency:** duplicate `WorkerReported` does not double-merge

### 8.2 Scheduler

Pulls from `pending` when:

1. AgentProvider capacity available
2. File locks acquirable
3. No Supervisor `WAIT` on program
4. Wave parallel limit not exceeded

---

## 9. Projection

**Authoritative state:** event log + atomic checkpoints (`STATE.yaml` successor).

**Projection:** derived document for humans and UI.

### 9.1 Schema v1 (illustrative)

```yaml
schema_version: 1
program_id: px2-parallel
derived_at: "2026-07-05T18:00:00Z"
cycle_id: cyc-20260705-001
supervisor:
  state: WAIT
  reason: px2_complete_pending_operator
waves:
  wave_a: { status: pass, completed_at: "2026-07-04T12:00:00Z" }
  wave_b: { status: pass }
  wave_c: { status: pass }
  wave_d: { status: waiting }
integrations:
  integration_a: { status: pass }
  integration_b: { status: pass }
  integration_c: { status: pass }
jobs:
  PX2-EWO-007: { status: done }
queue:
  pending: 0
  in_flight: 0
  failed: 0
qwo:
  QWO-PX2-001:
    status: pass
    certificate: .asep/certificates/QWO-PX2-001-R1-20260705.yaml
gates:
  ci: pass
  coverage: pass
```

### 9.2 Projection rules

- **PR-1:** Rebuilt from events + checkpoint — never edited by hand in production
- **PR-2:** CLI, dashboard, reports are **consumers** only
- **PR-3:** Mismatch between projection and checkpoint → `RuntimeEscalated`

### 9.3 Dashboard UX (Phase 3)

View only. Example:

```text
PX-2    Wave A  PASS    Wave B  PASS    Wave C  PASS    QWO  PASS
PX-3    Wave A  WAITING                              QWO  LOCKED
```

No buttons that schedule — operator uses `APPROVED` / ASEP skill; Runtime reacts.

---

## 10. Agent Provider (Phase 4)

```python
# Conceptual protocol — specified, not implemented
class AgentProvider(Protocol):
    provider_id: str

    def dispatch(self, job: Job, manifest: DispatchManifest) -> AgentHandle: ...
    def status(self, handle: AgentHandle) -> AgentStatus: ...
    def cancel(self, handle: AgentHandle) -> None: ...
```

| Adapter | Era | Status |
|---------|-----|--------|
| `CursorTaskProvider` | II | Reference implementation target |
| `HumanProvider` | II | Manual steps (integration, approval) |
| Others | III+ | Out of scope until protocol stable |

Runtime schedules **jobs**; providers execute **workers**.

---

## 11. Governance Policy vs Runtime Rule

| | Governance Policy | Runtime Rule |
|--|-------------------|--------------|
| **Examples** | QC required before QWO; termination limits; ADR freeze | Merge after EwoCompleted; CI gate before integration |
| **Evaluator** | Engineering Supervisor | Rule Engine |
| **On failure** | WAIT / STOP | Retry, replan, or RuntimeEscalated |
| **Source** | `.asep/governance/`, `docs/auto-approval-policy.md` | Rule packs per program |
| **Changes** | Architect / operator | Program yaml + MB2 spec |

Mixing these causes either an over-powered Runtime or an over-operational Supervisor.

---

## 12. MB2 phase mapping

| PX-EXEC Phase | v2 sections | Implementation home |
|---------------|-------------|---------------------|
| P1 Runtime Foundation | §4–§6, §8–§9 | `builder_engine/` extend |
| P2 Execution Plugins | §7 | `builder_engine/plugins/` |
| P3 Observability | §9 | projection builder + UI spec |
| P4 Provider Abstraction | §10, §8.2 | `AgentProvider` + multi-queue |

MB2 spec MUST trace each deliverable to section IDs above.

---

## 13. Validated reference path

PX-2 parallel program (`.asep/programs/px2-parallel.yaml`) is the **golden manual
execution** Runtime must replay:

```text
wave_a → integration_a → wave_b → integration_b → wave_c → integration_c
  → wave_d → QWO-PX2-001 → milestone qualified → frozen
```

MB2 acceptance: automated run produces equivalent evidence bundle + projection.

---

## 14. Non-goals (v2)

| Forbidden | Rationale |
|-----------|-----------|
| Product LangGraph changes | Product Plane |
| Removing APPROVED at freeze/promotion | Governance |
| Runtime reading Constitution prose | Separation of concerns |
| Dashboard scheduling logic | Projection-only |
| Implementation before MB2 freeze | ADR-0042 |

---

## 15. Relationship to v1

| Document | Role |
|----------|------|
| `mb2-engineering-runtime-spec.md` | **Specification of Record** — normative contract |
| `runtime-model.md` (v1) | Canonical **10-phase cycle** semantics — still valid |
| `runtime-model-v2.md` (this) | **Structure** — graphs, events, plugins, projection |
| ADR-0042 | Irreversible architectural decisions |
| `px-exec.yaml` | Delivery program |

When v1 and v2 appear to conflict on **phase names**, v1 wins on semantics.
When they conflict on **structure**, v2 wins for Era II+.

---

## 16. Freeze record

- [x] Governance / Runtime layer split defined
- [x] Program Graph vs Execution Graph defined
- [x] Job FSM + Supervisor FSM composition defined
- [x] Event → Rule → Action model defined
- [x] Plugin registry interfaces defined
- [x] Projection schema v1 defined
- [x] Agent Provider specified (not implemented)
- [x] MB2 phase mapping defined
- [x] PX-2 golden path identified

**Implementation authorized:** MB2 SoR §15 — Reference Implementation after Architect sign-off on SoR freeze record.

---

## 17. References

- **`docs/superpowers/specs/mb2-engineering-runtime-spec.md`** — MB2 Specification of Record (normative)
- ADR-0042 Engineering Runtime
- ADR-0026, ADR-0023, ADR-0025, ADR-0028
- `docs/platform/runtime-model.md` (v1)
- `docs/platform/era-model.md`
- `docs/platform/global-state-machine.md`
- `.asep/programs/px-exec.yaml`
- `.asep/programs/px2-parallel.yaml`
- `.asep/governance/engineering-supervisor.md`
- `builder_engine/events.py`, `builder_engine/state_machine.py`
