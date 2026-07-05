# MB2 — Engineering Runtime Specification of Record (SoR)

- **Document class:** **Specification of Record (SoR)** — normative technical contract
- **Status:** Frozen (Architect design freeze — 2026-07-05)
- **Milestone:** Platform Track **MB2** — Engineering Runtime
- **Plane:** Build Control Plane + Engineering Runtime (sidecar only)
- **Supersedes (normative authority):** `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` for Runtime contract semantics. That document remains a **historical reference implementation roadmap** (Era I cycle head/tail — Observe → Replan). **This SoR is authoritative** for conformance.
- **Authority chain:**

  ```text
  Vision (Era II)           docs/platform/era-model.md
        ↓
  ADR                       decisions/ADR-0042-engineering-runtime.md (+ cited ADRs)
        ↓
  Specification of Record   this document
        ↓
  Reference Implementation  builder_engine/ (today); future sidecars per ADR-0023
        ↓
  Qualification Package     MB2-Q* gates, .asep/reports/MB2-*.md, test evidence
  ```

- **Companions (non-normative structure):** `docs/platform/runtime-model-v2.md` (L3 dynamics map), `.asep/programs/px-exec.yaml` (delivery program)

---

## Document hierarchy and terminology

| Term | Role | Mutability |
|------|------|------------|
| **Vision** | Directional platform maturity (Era I → IV) | Rare — era boundaries |
| **ADR** | Irreversible architectural decisions | New ADR only |
| **Specification of Record (SoR)** | Normative Runtime contract — implementation must satisfy | MB2 freeze amendments via Architect + traceability update |
| **Reference Implementation** | Code that implements the SoR | Continuous — must stay conformant |
| **Qualification Package** | Evidence that Reference Implementation satisfies SoR | Per gate run — immutable reports/certificates |

**Normative rule:** Where this SoR, an ADR, and `runtime-model-v2.md` disagree on **contract requirements**, this SoR wins. Where they disagree on **architectural intent**, ADR wins. Where they disagree on **10-phase cycle semantics**, `runtime-model.md` (v1) wins.

---

## Conformance statement

> **This specification does not prescribe any particular implementation.**
> Any implementation is **conformant** if and only if it satisfies:
> - all **Runtime invariants** (§3),
> - all **contracts** (§4–§9),
> - all **Supervisor interaction rules** (§10),
> - all **failure and recovery semantics** (§11–§12),
> - and passes all **Qualification gates** (§13) with documented evidence in a Qualification Package.

The Reference Implementation in `builder_engine/` is the **first** implementation target — not the definition of the Runtime.

---

## 1. Scope

### 1.1 In scope

The Engineering Runtime (**Runtime**) is the deterministic execution engine of ASEP's
Build Control Plane. This SoR defines:

1. **Data model** — Program Graph input, Execution Graph derivation, job queue, checkpoints, projections
2. **State model** — Job FSM, composition with Supervisor FSM (Governance)
3. **Event model** — typed append-only catalog and emission rules
4. **Rule model** — declarative Event → Action reactions
5. **Plugin contracts** — swappable engines (Scheduler, Merge, Integration, Qualification, …)
6. **Projection model** — read-only observability derived from authoritative state
7. **Supervisor interaction** — delegation, escalation, WAIT halting
8. **Failure and recovery** — fail-closed behavior, retry policy
9. **Qualification** — verifiable gates and traceability

### 1.2 Consumers

| Consumer | Relationship |
|----------|--------------|
| `builder_engine/` | Reference Implementation (Phase 1+) |
| `.asep/programs/px-exec.yaml` | Delivery program — maps SoR sections to PX-EXEC phases |
| Engineering Supervisor | Governance — reads Qualification Package; delegates execution |
| Product programs (PX-3+) | Declare Program Graph contracts compatible with SoR |
| CLI / Dashboard | Projection consumers only |

### 1.3 Era I partial implementation

Era I delivered a **vertical slice**: Schedule → Validate → Update State (`builder_engine/runtime.py`, ADR-0025 packet FSM). MB2 **extends** this slice to full event-driven Runtime — it does not discard ADR-0025 semantics.

---

## 2. Non-goals

| ID | Non-goal | Rationale |
|----|----------|-----------|
| NG-1 | Product Plane LangGraph topology | Product Track — M5+ |
| NG-2 | Mutating `backend/app/` or end-user runtime | ADR-0023 sidecar boundary |
| NG-3 | Evaluating Governance policies inside Runtime | ADR-0042 Governance/Runtime split |
| NG-4 | Auto-editing ADRs, Constitution, or frozen specs | Architect gate |
| NG-5 | Dashboard or CLI scheduling logic | Projection-only (§9) |
| NG-6 | Prescribing Cursor Task as sole agent vendor | AgentProvider abstraction (Phase 4) |
| NG-7 | Replacing git or filesystem as source of truth for code | ADR-0019, ADR-0023 |
| NG-8 | Removing human `APPROVED` at promotion/freeze | Governance invariant |

---

## 3. Runtime invariants

Violations are **conformance failures** — implementation MUST fail closed.

### 3.1 Graph invariants

| ID | Invariant |
|----|-----------|
| **INV-R-01** | Every executable node belongs to exactly one Program Graph declaration. |
| **INV-R-02** | Execution Graph is fully derived from Program Graph + runtime state + event history — never manually edited. |
| **INV-R-03** | `merge_order` constrains merge sequencing; Dependency Engine MUST NOT invent dependencies absent from Program Graph. |

### 3.2 Layer separation invariants

| ID | Invariant |
|----|-----------|
| **INV-R-04** | Supervisor MUST NOT mutate Runtime authoritative state (queue, locks, execution transitions). |
| **INV-R-05** | Runtime MUST NOT mutate Governance state (Program Graph, capability lifecycle, ADR, QC verdicts). |
| **INV-R-06** | Runtime MUST NOT import `backend.app` or mutate Product Plane on behalf of end users (ADR-0023). |
| **INV-R-07** | Governance policies MUST NOT be evaluated inside Runtime plugins — only Runtime rules + L1 invariants. |

### 3.3 Event and state invariants

| ID | Invariant |
|----|-----------|
| **INV-R-08** | Every Runtime state transition MUST emit a typed event before or atomically with checkpoint commit — no silent mutation. |
| **INV-R-09** | Event handlers MUST be idempotent under at-least-once delivery. |
| **INV-R-10** | Authoritative state is event log + atomic checkpoint — not projection, not CLI output. |

### 3.4 Observability invariants

| ID | Invariant |
|----|-----------|
| **INV-R-11** | Projection never owns state — it is rebuildable and read-only. |
| **INV-R-12** | Observability surfaces (CLI, dashboard, reports) MUST NOT compute scheduling decisions independently of Runtime. |

### 3.5 Rule and plugin invariants

| ID | Invariant |
|----|-----------|
| **INV-R-13** | Rules are deterministic: same event + same checkpoint ⇒ same action descriptor (or explicit no-match). |
| **INV-R-14** | Plugins MUST register via Plugin Registry — core MUST NOT import plugin implementations directly. |
| **INV-R-15** | Plugin API version mismatch MUST fail closed at registration time. |

### 3.6 Supervisor invariants

| ID | Invariant |
|----|-----------|
| **INV-R-16** | Supervisor `WAIT` MUST halt autonomous Runtime progression until operator or policy clears. |
| **INV-R-17** | Runtime escalation (`RuntimeEscalated`) MUST transition Supervisor to `WAIT` or `STOP` — never auto-override. |

### 3.7 Mapping to ADR-0042

| ADR-0042 | SoR |
|----------|-----|
| INV-RT-1 | INV-R-06 |
| INV-RT-2 | INV-R-07 |
| INV-RT-3 | INV-R-08 |
| INV-RT-4 | INV-R-11, INV-R-12 |
| INV-RT-5 | INV-R-01, INV-R-02, INV-R-03 |
| INV-RT-6 | INV-R-16, INV-R-17 |

---

## 4. Data model

### 4.1 Program Graph (input — Governance-owned)

**Source:** `.asep/programs/*.yaml`, `.asep/proposals/*`, `.asep/capabilities/*.yaml`

| Entity | Fields (minimum) | Owner |
|--------|------------------|-------|
| `Program` | `id`, `waves`, `integrations`, `qualification` | Governance |
| `Wave` | `workorders[]`, `merge_order[]`, `depends_on`, `execute_in_parallel` | Governance |
| `Integration` | `depends_on_wave`, `actions[]`, `unblocks` | Governance |
| `EwoTemplate` | `id`, `depends_on[]`, `acceptance[]` | Governance |
| `QwoContract` | `id`, `unblocks_when[]`, gates | Governance |

Runtime **reads** Program Graph; changes require Governance authorization.

### 4.2 Execution Graph (derived — Runtime-owned)

| Entity | Derivation |
|--------|------------|
| `ExecutionNode` | Materialized EWO / integration / QWO job from Program Graph |
| `ReadySet` | Nodes whose preconditions are `DONE` for current stage |
| `CriticalPath` | Ordered ready set respecting `merge_order` and dependencies |

**Derivation trigger:** `ExecutionGraphDerived` event with content hash.

### 4.3 Job (runtime instance)

| Field | Type | Notes |
|-------|------|-------|
| `job_id` | string | Stable identifier |
| `program_id` | string | Parent program |
| `ewo_id` | string | Trace to proposal |
| `state` | JobState enum | §5 |
| `wave_id` | string? | Optional grouping |
| `locks` | map path → job_id | File locks |
| `provider_handle` | opaque? | AgentProvider reference |
| `checkpoint_ref` | string | Last committed event offset |

### 4.4 Checkpoint

Atomic persistence of:

- job queue segments (pending, in_flight, terminal)
- wave/integration aggregate markers
- lock table
- program execution scope (delegation token from Supervisor)

**Storage:** successor to `plans/builder/STATE.yaml` — backward compatible migration required (Reference Implementation detail).

### 4.5 Projection document

Derived document conforming to schema §9. **Not authoritative.**

---

## 5. State model

### 5.1 Job FSM (normative)

```text
CREATED → READY → CLAIMED → RUNNING → VALIDATING → MERGED → DONE
                ↘ FAILED → DEBUGGING ⇄ READY (recovery rule only)
                ↘ CANCELLED (terminal)
```

Qualification jobs extend:

```text
… → MERGED → QUALIFYING → QUALIFIED | FAILED
```

| State | Entry condition | Exit events |
|-------|-----------------|-------------|
| READY | Dependencies satisfied; in queue | `JobClaimed` |
| RUNNING | AgentProvider active | `WorkerReported` |
| VALIDATING | Checks executing | `ValidationPassed` / `ValidationFailed` |
| MERGED | Merge policy satisfied | `MergeCompleted` |
| QUALIFIED | QWO PASS | `QwoPassed` |

**Conformance:** Transitions MUST be subset of ADR-0025 + L2 GSM Task transitions. Illegal transitions MUST raise `TransitionError` and emit `RuntimeEscalated`.

### 5.2 Supervisor FSM (Governance — interaction only)

Runtime observes Supervisor state; does not implement Supervisor logic.

| Supervisor state | Runtime behavior |
|------------------|------------------|
| `EXECUTE` (delegated) | May schedule per delegation scope |
| `WAIT` | Queue paused — no new CLAIM |
| `STOP` | Drain or hold per policy — no new dispatch |

### 5.3 Aggregate roll-up states (projection)

`waiting | ready | running | pass | fail | locked` — derived from job states; see §9.

---

## 6. Event model

### 6.1 Bus requirements

| Requirement | Normative |
|-------------|-----------|
| Storage | Append-only log (e.g. `.builder-engine/events.jsonl`) |
| Catalog | Closed set — new types require SoR amendment + ADR if architectural |
| Delivery | At-least-once to Rule Engine and registered plugins |
| Immutability | Events never updated or deleted |

### 6.2 Catalog — Era I baseline (retained)

Retained from `builder_engine/events.py` and L2 §7:

`SnapshotCreated`, `StateObserved`, `PolicyAllowed`, `PolicyBlocked`, `PlanGenerated`, `PlanEmpty`, `TaskScheduled`, `LockAcquired`, `ValidationPassed`, `ValidationFailed`, `StateUpdated`, `WaveAdvanced`, `MergeAccepted`, `MergeRejected`, `Replanned`, `RecoveryTaskCreated`, `WorkerDispatched`, `WorkerReported`, `CycleStarted`, `CycleHalted`, `EventsPublished`

### 6.3 Catalog — MB2 extensions (normative)

| Event | Emitted when |
|-------|--------------|
| `ExecutionGraphDerived` | Dependency Engine completes derivation |
| `JobReady` | Job enters READY |
| `JobClaimed` | Scheduler claims job |
| `EwoCompleted` | EWO worker reports success |
| `MergeCompleted` | Merge plugin succeeds |
| `MergeFailed` | Merge plugin fails |
| `IntegrationStarted` | Integration plugin begins |
| `IntegrationPassed` | Integration gate PASS |
| `IntegrationFailed` | Integration gate FAIL |
| `QwoSpawned` | Qualification plugin starts QWO |
| `QwoPassed` | QWO PASS with certificate hook |
| `QwoFailed` | QWO FAIL |
| `RuntimeEscalated` | Unrecoverable error or invariant violation |
| `ProjectionUpdated` | Projection rebuilt |

### 6.4 Event payload (minimum)

Every event MUST include:

```yaml
type: string          # catalog name
timestamp: ISO8601
cycle_id: string?     # engineering cycle correlation
program_id: string
payload: object       # event-specific
```

---

## 7. Rule model

### 7.1 Processing model

```text
Event received
  → Rule Engine loads rule pack(s) for program_id
  → Evaluate guards (deterministic)
  → Emit action descriptor OR no-match (logged)
  → Plugin Registry resolves plugin
  → Plugin executes (may emit new events)
```

**Not a pipeline:** rule order is by priority field; no implicit stage ordering.

### 7.2 Rule pack format (normative schema)

```yaml
schema_version: 1
program_id: px2-parallel   # or "*" for defaults
rules:
  - id: string
    priority: integer      # lower = earlier
    on: EventType          # catalog name
    when:                  # guard — all must pass
      key: value
    action:
      plugin: string       # registry id
      params: object
```

### 7.3 Reference rules (golden path — PX-2 parallel)

| Rule ID | On | When | Action |
|---------|-----|------|--------|
| `post-ewo-merge` | `EwoCompleted` | `all_dependencies_satisfied: true` | `merge` |
| `post-merge-integration` | `MergeCompleted` | `ci_status: passed` | `integration` |
| `post-integration-qwo` | `IntegrationPassed` | `coverage_gate: passed` | `qualification` |
| `qwo-escalate-supervisor` | `QwoPassed` | — | `notification` → Supervisor |

Conformance test **MB2-Q-002** replays these rules against fixture events.

### 7.4 Governance policy exclusion

Rules MUST NOT encode: QC certificate requirements, termination limits, ADR freeze checks, Constitution compliance. Those are Supervisor scope (INV-R-07).

---

## 8. Plugin contracts

### 8.1 Registry

```text
PluginRegistry.register(plugin_id, api_version, interface, factory)
PluginRegistry.resolve(action_descriptor) → Plugin
```

Core depends on **interfaces** only (INV-R-14).

### 8.2 Required plugin interfaces (Phase 1–2)

| Plugin ID | Interface methods (minimum) | Phase |
|-----------|----------------------------|-------|
| `scheduler` | `claim(job)`, `release(job)`, `build_manifest(jobs[])` | P1 |
| `merge` | `eligible(job)`, `execute(context)`, `report()` | P2 |
| `integration` | `start(integration_id)`, `run_checks()`, `report()` | P2 |
| `qualification` | `spawn(qwo_id)`, `collect_evidence()`, `report()` | P2 |
| `notification` | `notify(target, message, severity)` | P3 |
| `metrics` | `record(event, metrics)` | P3 |

### 8.3 AgentProvider (Phase 4 — specified)

```text
dispatch(job, manifest) → handle
status(handle) → AgentStatus
cancel(handle) → void
```

Reference adapter: `CursorTaskProvider`. Conformance requires **one** non-Cursor stub passing contract tests (MB2-Q-006 scope extension).

### 8.4 Plugin failure

Plugin failure MUST emit failure event (`MergeFailed`, etc.) or `RuntimeEscalated` — MUST NOT silently swallow.

---

## 9. Projection model

### 9.1 Schema version 1 (normative)

```yaml
schema_version: 1
program_id: string
derived_at: ISO8601
cycle_id: string?
supervisor:
  state: string
  reason: string?
waves:
  <wave_id>:
    status: waiting|ready|running|pass|fail|locked
    jobs: { <ewo_id>: { status: string } }
integrations:
  <integration_id>:
    status: waiting|ready|running|pass|fail|locked
jobs:
  <job_id>: { status: string, ewo_id: string }
queue:
  pending: integer
  in_flight: integer
  failed: integer
qwo:
  <qwo_id>:
    status: waiting|ready|running|pass|fail|locked
    certificate: string?
gates:
  ci: pass|fail|unknown
  coverage: pass|fail|unknown
```

### 9.2 Rebuild requirement

Given event log + latest checkpoint, Projection Builder MUST reproduce identical projection (deterministic rebuild). Test: **MB2-Q-005**.

### 9.3 Consumer rules

| Consumer | Allowed | Forbidden |
|----------|---------|-----------|
| CLI `builder-engine status` | Read projection | Compute ready-set |
| Dashboard | Render projection | Dispatch buttons |
| `.asep/reports/*` | Snapshot projection at gate time | Mutate queue |

---

## 10. Supervisor interaction

### 10.1 Delegation

| Operator signal | Governance effect | Runtime effect |
|-----------------|-------------------|----------------|
| `APPROVED` | Authorizes delegation token for program scope | May dispatch until next governance gate |
| `STOP` | Halts Supervisor loop | No new claims; in-flight per drain policy |
| Clear `WAIT` | Resumes Supervisor | Resumes queue if delegation still valid |

Delegation token fields (minimum): `program_id`, `scope` (phase/wave), `expires_at` or `until_gate`.

### 10.2 Escalation

Runtime MUST emit `RuntimeEscalated` when:

- Invariant violation detected
- Plugin unrecoverable failure
- Checkpoint write failure
- Projection/checkpoint mismatch

Supervisor MUST transition to `WAIT` or `STOP` — not auto-continue.

### 10.3 QWO boundary

| Outcome | Runtime | Supervisor |
|---------|---------|------------|
| `QwoPassed` | Emit event; update projection | OBSERVE → freeze decision |
| `QwoFailed` | Emit event; hold queue | WAIT — human required |

Runtime MUST NOT mark milestone `qualified` — Governance capability graph update only.

---

## 11. Failure semantics

| Failure class | Detection | Required behavior |
|---------------|-----------|-------------------|
| Validation fail | `ValidationFailed` | Job → FAILED; rule may create recovery task |
| Merge conflict | `MergeFailed` | Wave blocked; `RuntimeEscalated` or replan rule |
| CI fail | Integration guard | No integration start; job remains MERGED or FAILED per rule |
| Invariant violation | Pre-commit check | Abort transition; `RuntimeEscalated` |
| Provider timeout | `WorkerReported` timeout | Job → FAILED; metrics + notification |
| Duplicate event | Idempotency key | No double transition |

**Fail-closed default:** if guard cannot be evaluated (missing CI status, stale snapshot), action MUST NOT proceed.

---

## 12. Recovery semantics

| Recovery | Trigger | Normative path |
|----------|---------|----------------|
| Job retry | Operator or rule `recovery.retry_job` | FAILED → DEBUGGING → READY with audit event |
| Wave replay | Integration fail after partial merge | Supervisor APPROVED + recovery rule |
| Checkpoint restore | Process crash | Replay event log from last checkpoint |
| Projection rebuild | Corruption detected | Rebuild from log — never repair projection in place |

Recovery MUST emit `RecoveryTaskCreated` or `Replanned` (Era I catalog retained).

**MB2-Q-006** validates FAILED → READY recovery with full audit trail.

---

## 13. Qualification criteria

### 13.1 Qualification Package structure

A Qualification Package for gate **MB2-Qn** MUST include:

| Artifact | Path pattern |
|----------|--------------|
| Gate report | `.asep/reports/MB2-Q{n}-*.md` |
| Test evidence | `builder_engine/tests/test_mb2_*.py` results |
| Projection snapshot | attached YAML at gate time |
| Traceability rows | §14 rows for this gate — all PASS |
| Certificate (optional) | `.asep/certificates/MB2-Q{n}-*.yaml` |

### 13.2 Qualification gates (normative)

| Gate | Title | Scope | Pass criteria (summary) |
|------|-------|-------|-------------------------|
| **MB2-Q1** | Runtime Graph | §4.2, §5, Dependency Engine | Program Graph → Execution Graph derivation; illegal node rejected; **MB2-Q-001…003** |
| **MB2-Q2** | Rule Engine | §7 | Deterministic rule evaluation; golden PX-2 rules; **MB2-Q-004…006** |
| **MB2-Q3** | Scheduler | §5, §8.2 scheduler | Claim/release; lock acquisition; respects WAIT; **MB2-Q-007…009** |
| **MB2-Q4** | Plugin Registry | §8 | Register/resolve; version mismatch fails closed; **MB2-Q-010…012** |
| **MB2-Q5** | Projection | §9 | Rebuild deterministic; CLI read-only; **MB2-Q-013…015** |
| **MB2-Q6** | Recovery | §12 | FAILED → READY audit; checkpoint replay; **MB2-Q-016…018** |

**MB2 promotion** (platform milestone complete): all MB2-Q1…Q6 PASS + PX-2 parallel golden path replay (§13.3).

### 13.3 Golden path acceptance

Reference program: `.asep/programs/px2-parallel.yaml`

Automated or audited replay MUST produce equivalent evidence to manual execution:

```text
wave_a → integration_a → wave_b → integration_b → wave_c → integration_c
  → wave_d → QWO-PX2-001 → qualified
```

Qualification test **MB2-Q-018** (gate MB2-Q6 / promotion bundle).

### 13.4 Individual qualification tests (registry)

| Test ID | Gate | Requirement | Section |
|---------|------|-------------|---------|
| MB2-Q-001 | Q1 | Execution Graph derived only from Program Graph | §4.2, INV-R-02 |
| MB2-Q-002 | Q1 | No orphan executable nodes | INV-R-01 |
| MB2-Q-003 | Q1 | merge_order respected | INV-R-03 |
| MB2-Q-004 | Q2 | Same event + state ⇒ same action | INV-R-13 |
| MB2-Q-005 | Q2 | Governance policy not in rule pack | INV-R-07 |
| MB2-Q-006 | Q2 | PX-2 golden rules replay | §7.3 |
| MB2-Q-007 | Q3 | Single-flight lock per owned path | §8.2 scheduler |
| MB2-Q-008 | Q3 | WAIT halts new claims | INV-R-16 |
| MB2-Q-009 | Q3 | Dispatch manifest emitted | §6.3 |
| MB2-Q-010 | Q4 | Plugin registers by interface | INV-R-14 |
| MB2-Q-011 | Q4 | Version mismatch rejected | INV-R-15 |
| MB2-Q-012 | Q4 | Core has no direct plugin imports | INV-R-14 |
| MB2-Q-013 | Q5 | Projection rebuild = original | INV-R-11 |
| MB2-Q-014 | Q5 | CLI does not compute ready-set | INV-R-12 |
| MB2-Q-015 | Q5 | Schema v1 valid | §9.1 |
| MB2-Q-016 | Q6 | FAILED → READY emits audit | §12 |
| MB2-Q-017 | Q6 | Checkpoint + replay restores queue | §12 |
| MB2-Q-018 | Q6 | PX-2 golden path replay | §13.3 |

Test implementations are Reference Implementation artifacts — test IDs are **normative** in this SoR.

---

## 14. Traceability

### 14.1 Hierarchy (normative)

```text
Vision → ADR → SoR (this document) → Capability → Qualification Test
```

### 14.2 Master traceability matrix

| Req ID | Requirement | SoR § | ADR | Capability | Gate | Test |
|--------|-------------|-------|-----|------------|------|------|
| REQ-01 | Runtime is event-driven | §6, §7 | ADR-0042 §2 | px-exec-1-event-model | MB2-Q2 | MB2-Q-004 |
| REQ-02 | Execution Graph is derived | §4.2 | ADR-0042 §3 | px-exec-3-dependency-engine | MB2-Q1 | MB2-Q-001 |
| REQ-03 | Every node traces to Program Graph | §4.1, §3 INV-R-01 | ADR-0042 §3 | px-exec-3-dependency-engine | MB2-Q1 | MB2-Q-002 |
| REQ-04 | merge_order enforced | §3 INV-R-03 | ADR-0042 §3 | px-exec-7-merge-plugin | MB2-Q1 | MB2-Q-003 |
| REQ-05 | Supervisor cannot mutate runtime state | §10, INV-R-04 | ADR-0042 §1 | governance | MB2-Q3 | MB2-Q-008 |
| REQ-06 | Runtime cannot mutate governance state | §3 INV-R-05 | ADR-0042 §1 | governance | MB2-Q2 | MB2-Q-005 |
| REQ-07 | Sidecar isolation | §2 NG-2, INV-R-06 | ADR-0023 | px-exec-* | all | isolation lint |
| REQ-08 | No silent state mutation | §6, INV-R-08 | ADR-0042 §2 | px-exec-1-event-model | MB2-Q2 | MB2-Q-004 |
| REQ-09 | Rules deterministic | §7, INV-R-13 | ADR-0042 §2 | px-exec-2-rule-engine | MB2-Q2 | MB2-Q-004 |
| REQ-10 | Plugin registry required | §8, INV-R-14 | ADR-0042 §5 | px-exec-7…9 | MB2-Q4 | MB2-Q-010…012 |
| REQ-11 | Projection read-only | §9, INV-R-11 | ADR-0042 §6 | px-exec-6-state-projection | MB2-Q5 | MB2-Q-013…015 |
| REQ-12 | WAIT halts autonomous progression | §10, INV-R-16 | ADR-0042 §1 | px-exec-5-scheduler | MB2-Q3 | MB2-Q-008 |
| REQ-13 | Escalation to Supervisor | §10.2, INV-R-17 | ADR-0042 §1 | px-exec-2-rule-engine | MB2-Q3 | MB2-Q-008 |
| REQ-14 | Job FSM conforms ADR-0025 | §5 | ADR-0025 | px-exec-4-job-queue | MB2-Q1 | MB2-Q-001 |
| REQ-15 | Recovery auditable | §12 | ADR-0042 | px-exec-15-recovery-policies | MB2-Q6 | MB2-Q-016…017 |
| REQ-16 | PX-2 golden path replay | §13.3 | ADR-0042 §8 | px-exec P2 | MB2-Q6 | MB2-Q-018 |
| REQ-17 | AgentProvider abstraction | §8.3 | ADR-0042 §7 | px-exec-13-agent-provider | Phase 4 | TBD |
| REQ-18 | Idempotent event handlers | §6, INV-R-09 | ADR-0006 | px-exec-1-event-model | MB2-Q2 | MB2-Q-004 |
| REQ-19 | Qualification plugin spawns QWO | §7.3, §8.2 | ADR-0042 §2 | px-exec-9-qualification-plugin | MB2-Q2 | MB2-Q-006 |
| REQ-20 | Dashboard is view only | §9.3, NG-5 | ADR-0042 §6 | px-exec-10-dashboard-projection | MB2-Q5 | MB2-Q-014 |

### 14.3 PX-EXEC phase mapping

| PX-EXEC Phase | SoR sections | Gates |
|---------------|--------------|-------|
| P1 Runtime Foundation | §4–§7, §9, §10 (partial) | MB2-Q1, Q2, Q3, Q5 (partial) |
| P2 Execution Plugins | §8.2 merge/integration/qualification | MB2-Q4, Q2 rules |
| P3 Observability | §9.3, §8.2 notification/metrics | MB2-Q5 |
| P4 Provider Abstraction | §8.3, §4 queue multi-program | MB2-Q6 + REQ-17 |

### 14.4 Vision anchor

| Vision | SoR expression |
|--------|----------------|
| Era II — Adaptive Workflow Intelligence (`era-model.md`) | Event-driven Runtime + observable projections |
| ADR-0026 §5 lifecycle | Qualification Package gates before promotion |
| PX-2 validated patterns | Golden path §13.3 |

---

## 15. Freeze record

- [x] Document class: Specification of Record declared
- [x] Conformance statement (implementation-independent)
- [x] Runtime invariants §3 (17 invariants)
- [x] Data, state, event, rule, plugin, projection models
- [x] Supervisor interaction, failure, recovery semantics
- [x] Qualification gates MB2-Q1…Q6 + test registry MB2-Q-001…018
- [x] Traceability matrix REQ-01…20
- [x] Supersedes normative authority of 2026-06-25 MB2 design spec
- [x] **Specification Freeze** — Architect sign-off `.asep/certificates/MB2-SOR-20260705.yaml` (2026-07-05)

**Reference Implementation authorized:** after MB2-Q gate passage — **not** at Specification Freeze.

**Amendment policy:** `.asep/governance/sor-compatibility-policy.md`

---

## 16. References

| Artifact | Role |
|----------|------|
| `docs/platform/era-model.md` | Vision — Era II |
| `decisions/ADR-0042-engineering-runtime.md` | ADR |
| `docs/platform/runtime-model-v2.md` | Structural companion |
| `docs/platform/runtime-model.md` | 10-phase cycle semantics (v1) |
| `docs/platform/global-state-machine.md` | L2 transitions |
| `docs/platform/engineering-traceability-matrix.md` | Platform ETM (extended by §14) |
| `.asep/programs/px-exec.yaml` | Delivery program |
| `.asep/capabilities/px-exec.yaml` | Capability graph |
| `.asep/programs/px2-parallel.yaml` | Golden path reference |
| `builder_engine/` | Reference Implementation (partial) |
| `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` | Historical — Era I cycle completion roadmap |
