# Engineering WorkOrder Proposal — PX-EXEC-EWO-001

> **Status:** ✅ **IMPLEMENTED** — `.asep/reports/PX-EXEC-EWO-001-event-model.md` PASS @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P1 — Runtime Foundation |
| **Wave** | Wave A (first executable) |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-1-event-model` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-001 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on authorization) → `done` (on PASS report) |

---

## Objective

Extend the Era I append-only event bus (`builder_engine/events.py`) to satisfy **SoR §6
Event model**: closed v2 catalog, normative payload schema including `program_id`, durable
append-only log, and subscriber delivery hook for at-least-once dispatch — **without**
implementing Rule Engine logic (EWO-002) or emitting business workflow events from plugins
(Phase 2).

This EWO is the **foundation** for all Phase 1 capabilities and enables future MB2-Q2
evidence (REQ-01, REQ-08, REQ-18); it does **not** constitute MB2-Q2 or MB2-Q pass.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-001 deliverable |
|-------|-------------|---------------------|
| **§6.1** Bus requirements | Append-only log; closed catalog; at-least-once delivery; immutability | Extend `BuildEventBus`; catalog enforcement; `subscribe()` / dispatch hook (no Rule Engine) |
| **§6.2** Era I baseline | Retain existing catalog entries | No removals from `ALLOWED_EVENT_TYPES` |
| **§6.3** MB2 extensions | 14 new event types | Add to catalog constant; document payload stubs |
| **§6.4** Event payload | `type`, `timestamp`, `cycle_id?`, `program_id`, `payload` | Extend `BuildEvent` schema; migration-safe defaults for Era I callers |

### MB2 §6.3 catalog (normative — implement in this EWO)

| Event | Emitted when (SoR) | EWO-001 scope |
|-------|-------------------|---------------|
| `ExecutionGraphDerived` | Dependency Engine completes | Catalog + payload type stub |
| `JobReady` | Job enters READY | Catalog + payload type stub |
| `JobClaimed` | Scheduler claims job | Catalog + payload type stub |
| `EwoCompleted` | EWO worker reports success | Catalog + payload type stub |
| `MergeCompleted` | Merge plugin succeeds | Catalog only (plugin Phase 2) |
| `MergeFailed` | Merge plugin fails | Catalog only |
| `IntegrationStarted` | Integration plugin begins | Catalog only |
| `IntegrationPassed` | Integration gate PASS | Catalog only |
| `IntegrationFailed` | Integration gate FAIL | Catalog only |
| `QwoSpawned` | Qualification plugin starts QWO | Catalog only |
| `QwoPassed` | QWO PASS | Catalog only |
| `QwoFailed` | QWO FAIL | Catalog only |
| `RuntimeEscalated` | Unrecoverable error / invariant violation | Catalog + payload type stub |
| `ProjectionUpdated` | Projection rebuilt | Catalog + payload type stub |

EWO-001 adds **catalog membership and serialization** for all §6.3 types. **Emitters**
for Phase 2 plugin events are out of scope; tests use `event_now()` / direct publish.

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-01 | Runtime is event-driven | MB2-Q2 | MB2-Q-004 |
| REQ-08 | No silent state mutation | MB2-Q2 | MB2-Q-004 |
| REQ-18 | Idempotent event handlers | MB2-Q2 | MB2-Q-004 |

### Invariants

| Invariant | EWO-001 enforcement |
|-----------|---------------------|
| **INV-R-08** | Bus API documents: state writers must publish before checkpoint commit; add helper or contract test hook |
| **INV-R-09** | Subscriber dispatch documents idempotency contract; duplicate delivery test fixture |

### Phase 1 binding

Per SoR §14.3, Phase 1 Runtime Foundation includes §6. This EWO is the **first**
implementation step under that phase after program authorization.

---

## Ownership (exclusive)

```text
builder_engine/events.py
builder_engine/tests/test_events.py
builder_engine/tests/test_mb2_event_catalog.py   # new — MB2 §6.3 catalog tests
```

**Shared read-only (callers updated only if required for `program_id`):**

```text
builder_engine/cycle.py          # publish sites — minimal additive program_id
builder_engine/runtime.py        # publish sites — minimal additive program_id
```

Changes outside ownership require explicit Architect approval in EWO report.

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/rules.py          # EWO-002
builder_engine/scheduler.py      # EWO-005 (beyond event publish sites)
builder_engine/merge.py          # Phase 2
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
.asep/governance/**              # no policy changes
product conformance reports      # PX-3 scope
```

**Behavioral exclusions:**

- Rule pack evaluation (§7)
- Program Graph → Execution Graph derivation (§4.2) — EWO-003
- Job FSM / queue (§5) — EWO-004
- Plugin registry (§8) — Phase 2
- Projection builder (§9) — EWO-006
- MB2-Q qualification report issuance
- PX-4 / product milestone work

---

## Scope

### In scope

1. **Extend `ALLOWED_EVENT_TYPES`** with all SoR §6.3 events; retain §6.2 Era I set
2. **Extend `BuildEvent`** with required `program_id: str` per §6.4 (default `"*"` or
   `"builder"` for legacy Era I publish sites to preserve test compatibility)
3. **Serialization** — JSONL line format includes `program_id`; round-trip in `from_line` /
   `to_line`
4. **`BuildEventBus` enhancements:**
   - Append-only publish (existing behavior preserved)
   - `subscribe(handler)` registry for at-least-once delivery to registered handlers
   - `replay(from_offset)` or tail-based replay helper for idempotency tests
   - Handler exceptions logged; bus continues (no silent drop of publish)
5. **Catalog enforcement** — reject unknown types at construct and publish time (existing +
   extended catalog)
6. **Tests** — Era I regression + MB2 catalog coverage (see Acceptance tests)
7. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-001-event-model.md`

### Out of scope

- Rule Engine implementation and golden PX-2 rules (EWO-002 / MB2-Q-006)
- Actual emission of `ExecutionGraphDerived`, `JobReady`, etc. from runtime modules
  (downstream EWOs — catalog ready only)
- Checkpoint / projection integration
- CLI changes beyond existing `builder-engine events --tail`
- Qualification Package for MB2-Q2

---

## Acceptance criteria (EWO exit)

- [ ] All SoR §6.2 Era I event names remain in `ALLOWED_EVENT_TYPES`
- [ ] All SoR §6.3 MB2 extension event names added to `ALLOWED_EVENT_TYPES`
- [ ] `BuildEvent` includes `program_id`; serialized in JSONL; validated on read
- [ ] Unknown event type rejected at construction and publish (closed catalog)
- [ ] Append-only: no update/delete API on bus or log file
- [ ] `subscribe()` delivers each published event to registered handlers (at-least-once
      within process; redelivery test documented for INV-R-09)
- [ ] Era I tests in `test_events.py` and `test_mb2_integration.py` pass unchanged or
      with additive `program_id` defaults only
- [ ] New `test_mb2_event_catalog.py` passes (see below)
- [ ] `make unit-builder-engine` green
- [ ] EWO report filed with traceability to §6.1–§6.4 and REQ-01/08/18
- [ ] **No MB2-Q2 PASS claim** in EWO report

---

## Acceptance tests (implement with EWO — design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_era_catalog_retained` | Every §6.2 baseline name ∈ `ALLOWED_EVENT_TYPES` | §6.2 |
| `test_mb2_catalog_complete` | Every §6.3 name ∈ `ALLOWED_EVENT_TYPES`; count = 14 extensions | §6.3 |
| `test_program_id_required_round_trip` | Publish + tail restores `program_id` | §6.4 |
| `test_unknown_type_rejected` | ValueError on unknown type (existing, extended) | §6.1 catalog |
| `test_append_only_tail_order` | Multiple publishes preserve order | §6.1 storage |
| `test_subscriber_receives_publish` | Handler invoked on `publish()` | §6.1 delivery |
| `test_subscriber_idempotent_redelivery` | Same event delivered twice; handler safe per contract doc | INV-R-09 |
| `test_corrupt_line_skipped` | Tail skips bad JSON (existing behavior) | durability |
| `test_legacy_cycle_events_still_publish` | `CycleStarted`, `TaskScheduled` etc. still work with default `program_id` | Era I compat |

Future gate tests ( **not** part of EWO-001 exit):

- `MB2-Q-004` — same event + state ⇒ same action (requires Rule Engine — EWO-002)

---

## Dependencies

| Depends on | Status |
|------------|--------|
| MB2 SoR frozen @ 2026-07-05 | **PASS** — certificate on file |
| PX-3 COMPLETE + conformance assessment | **PASS** — ratified |
| Program `AUTHORIZE px-exec` | **PASS** — `.asep/reports/PX-EXEC-AUTHORIZATION-20260705.md` |
| Wave A backlog registered | **PENDING** — Architect review of backlog doc |
| This proposal approved | **PENDING** |

**Unblocks:** PX-EXEC-EWO-002, PX-EXEC-EWO-003, PX-EXEC-EWO-006 (partial)

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation merged | `builder_engine/events.py` + tests on branch |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | No forbidden paths touched; no SoR diff |
| Traceability | EWO report maps deliverables → §6.1–§6.4, REQ-01/08/18 |
| Downstream ready | Catalog types available for EWO-002/003/006 |
| Qualification boundary | Report states: **does not satisfy MB2-Q2** |

---

## Constraints

- ADR-0042 §2 — event-driven execution; no Governance logic in bus
- ADR-0023 — sidecar isolation; events in `.builder-engine/events.jsonl` only
- `sor-compatibility-policy` — implementation clarifications OK; no normative SoR edits
- Smallest correct diff; match `builder_engine/` style
- Do not dispatch until Architect authorizes after backlog registration

---

## WO-TRACE

```text
AUTHORIZE px-exec → STOP (no EWO)
  → PX-EXEC-WAVE-A-BACKLOG + this proposal
  → Architect review
  → register workorder_backlog
  → AUTHORIZE PX-EXEC-EWO-001
  → implement → verify → PX-EXEC-EWO-001 report PASS
  → PX-EXEC-EWO-002 ∥ PX-EXEC-EWO-003
```
