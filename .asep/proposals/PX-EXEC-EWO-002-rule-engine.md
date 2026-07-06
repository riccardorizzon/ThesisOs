# Engineering WorkOrder Proposal — PX-EXEC-EWO-002

> **Status:** PROPOSED — pending Architect authorization for dispatch  
> **Prerequisite:** PX-EXEC-EWO-001 **IMPLEMENTED** @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P1 — Runtime Foundation |
| **Wave** | Wave A (parallel with EWO-003 after EWO-001) |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-2-rule-engine` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-002 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on authorization) → `done` (on PASS report) |

---

## Objective

Implement the **Runtime Rule Engine** per SoR §7: load declarative rule packs from YAML,
evaluate guards deterministically on incoming events, emit action descriptors (or explicit
no-match), and integrate with the Event Bus subscriber hook from EWO-001 — **without**
evaluating Governance policies (Supervisor scope), **without** executing Phase 2 plugins
(merge, integration, qualification), and **without** claiming MB2-Q2 or any MB2-Q pass.

This EWO enables future MB2-Q2 evidence (REQ-09, MB2-Q-004…006); it does **not** constitute
qualification.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-002 deliverable |
|-------|-------------|---------------------|
| **§7.1** Processing model | Event → load packs → evaluate guards → action descriptor | `RuleEngine.evaluate(event, checkpoint)` |
| **§7.2** Rule pack format | `schema_version`, `program_id`, `rules[]` with `priority`, `on`, `when`, `action` | YAML loader + schema validation |
| **§7.3** Reference rules | Golden PX-2 parallel rules as fixture pack | `builder_engine/fixtures/px2_parallel_rules.yaml` (test-only) |
| **§7.4** Governance exclusion | No QC, termination, ADR, Constitution in rule packs | Negative test + INV-R-07 guard |

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-01 | Runtime is event-driven | MB2-Q2 | MB2-Q-004 |
| REQ-09 | Rules deterministic | MB2-Q2 | MB2-Q-004 |
| REQ-13 | Escalation to Supervisor | MB2-Q3 | MB2-Q-008 (action descriptor only) |
| REQ-19 | Qualification plugin spawn rule | MB2-Q2 | MB2-Q-006 |

### Invariants

| Invariant | EWO-002 enforcement |
|-----------|---------------------|
| **INV-R-07** | Rule packs MUST NOT contain governance keys; engine rejects or ignores forbidden guard keys |
| **INV-R-13** | Same event + same checkpoint ⇒ same action descriptor (or no-match); unit tests with replay |
| **INV-R-08** | Rule evaluation does not mutate authoritative state; actions are descriptors only until plugin executes (Phase 2) |

### Phase 1 binding

Per SoR §14.3, Phase 1 includes §7 Rule model. Plugin execution from action descriptors
is stubbed via `ActionDescriptor` dataclass and optional no-op resolver for Phase 1 tests.

---

## Ownership (exclusive)

```text
builder_engine/rules.py                              # new — RuleEngine, ActionDescriptor, pack loader
builder_engine/tests/test_rules.py                   # new — unit + determinism tests
builder_engine/fixtures/px2_parallel_rules.yaml      # new — §7.3 golden path fixture (test data)
builder_engine/fixtures/rule_pack_invalid_governance.yaml  # new — INV-R-07 negative fixture
```

**Shared read-only (no structural changes without Architect approval):**

```text
builder_engine/events.py           # subscribe RuleEngine; read-only API use
builder_engine/yaml_loader.py      # reuse loader; no rule-specific hacks in loader
```

**Integration touch (minimal, documented in EWO report if required):**

```text
builder_engine/cycle.py            # optional: wire RuleEngine subscriber in postflight — additive only
```

Changes outside ownership require explicit Architect approval in EWO report.

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/dependency.py       # EWO-003 (or graph derivation module)
builder_engine/job_queue.py          # EWO-004
builder_engine/scheduler.py          # EWO-005 (beyond read-only reference)
builder_engine/projection.py         # EWO-006
builder_engine/merge.py              # Phase 2 plugin
docs/superpowers/specs/mb2-engineering-runtime-spec.md   # SoR — no edits
.asep/governance/**                  # no policy changes
plans/builder/policies.yaml          # Governance — Rule Engine must not consume as rule pack
```

**Behavioral exclusions:**

- Governance policy evaluation (`PolicyEngine` remains separate — Era I D2)
- Plugin Registry implementation (MB2-Q4 / Phase 2)
- Actual merge / integration / QWO execution
- Job FSM transitions (EWO-004)
- Program Graph → Execution Graph derivation (EWO-003)
- MB2-Q qualification report issuance
- PX-4 / product milestone work

---

## Scope

### In scope

1. **`ActionDescriptor` dataclass** — `plugin`, `params`, `rule_id`, `matched_event_id`
2. **`RulePack` loader** — parse §7.2 schema; validate required fields; reject unknown `schema_version`
3. **`RuleEngine` class:**
   - Load packs by `program_id` with `"*"` default fallback
   - Sort rules by `priority` (lower = earlier)
   - Match `on` event type; evaluate `when` guards (equality / boolean keys only in Phase 1)
   - Return first matching action descriptor or explicit `NoMatch`
   - Deterministic: no wall-clock or random guards in Phase 1
4. **Guard vocabulary (Phase 1 minimum):**
   - Flat key-value equality against event payload + checkpoint snapshot fields
   - Documented extension point for `all_dependencies_satisfied`, `ci_status`, etc. (stub values in tests)
5. **Event Bus integration** — register as subscriber; evaluate on publish; log no-match at DEBUG
6. **Forbidden governance keys detector** — reject packs containing `qc_`, `termination_`, `adr_`, `constitution_` guard keys
7. **Golden PX-2 rules fixture** — four rules from §7.3 table (evaluate only; no plugin execution)
8. **Tests** — see Acceptance tests
9. **EWO completion report** — `.asep/reports/PX-EXEC-EWO-002-rule-engine.md`

### Out of scope

- Plugin Registry (`PluginRegistry.register/resolve`) — EWO-004+ / MB2-Q4
- Scheduler `claim()` driven by rule actions — EWO-005
- Checkpoint persistence of rule evaluation history
- MB2-Q2 Qualification Package
- Wiring Rule Engine into live px-exec program execution loop (Phase 2 golden path replay)

---

## Acceptance criteria (EWO exit)

- [ ] Rule pack loads §7.2 schema; invalid schema raises clear error
- [ ] Rules sorted by `priority`; first match wins
- [ ] Same event + same checkpoint ⇒ same `ActionDescriptor` or same `NoMatch` (INV-R-13)
- [ ] Governance guard keys rejected or flagged per INV-R-07
- [ ] Golden PX-2 fixture: four §7.3 rules parse and match fixture events in unit tests
- [ ] Rule Engine registered as Event Bus subscriber; evaluation on publish does not mutate queue/state
- [ ] `PolicyEngine` and `RuleEngine` remain separate modules — no import of governance policies into rules
- [ ] Era I tests unchanged (`make unit-builder-engine` green)
- [ ] EWO report filed with traceability to §7.1–§7.4, REQ-09
- [ ] **No MB2-Q2 PASS claim** in EWO report

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_rule_pack_loads_schema_v1` | Valid pack parses | §7.2 |
| `test_rule_priority_ordering` | Lower priority evaluated first | §7.1 |
| `test_deterministic_match` | Replay same event twice → same action | INV-R-13, MB2-Q-004 prep |
| `test_no_match_logged` | Unknown guard → NoMatch, no exception | §7.1 |
| `test_governance_keys_rejected` | Pack with `qc_required` guard rejected | INV-R-07, MB2-Q-005 prep |
| `test_px2_golden_post_ewo_merge` | `EwoCompleted` + deps satisfied → merge action | §7.3 |
| `test_px2_golden_post_merge_integration` | `MergeCompleted` + ci passed → integration action | §7.3 |
| `test_px2_golden_post_integration_qwo` | `IntegrationPassed` + coverage → qualification action | §7.3 |
| `test_subscriber_on_publish` | Bus publish triggers evaluation | §6.1 delivery |
| `test_policy_engine_not_used` | RuleEngine has no import from `policy.py` | INV-R-07 |

Future gate tests (**not** part of EWO-002 exit):

- `MB2-Q-004` — full checkpoint + event replay suite
- `MB2-Q-006` — end-to-end golden path with plugins (Phase 2)

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-001 Event Model & Bus | **PASS** @ 2026-07-06 |
| MB2 SoR frozen @ 2026-07-05 | **PASS** |
| Program `AUTHORIZE px-exec` | **PASS** |
| Wave A engineering package | **PENDING** — this proposal + package review |
| Architect authorization for EWO-002 dispatch | **PENDING** |

**Unblocks:** PX-EXEC-EWO-005 (Scheduler requires Rule Engine for reactive dispatch rules)

**Parallel with:** PX-EXEC-EWO-003 (disjoint ownership — no file conflicts)

---

## Exit criteria (WorkOrder complete)

| Criterion | Evidence |
|-----------|----------|
| Implementation on branch | `builder_engine/rules.py` + tests + fixtures |
| Verification green | `make unit-builder-engine` log in EWO report |
| Scope honored | No forbidden paths; no SoR diff |
| Traceability | EWO report maps deliverables → §7.1–§7.4, REQ-09 |
| Downstream ready | Action descriptors available for EWO-005 scheduler wiring |
| Qualification boundary | Report states: **does not satisfy MB2-Q2** |

---

## Constraints

- ADR-0042 §2 — event-driven; Governance policies outside Runtime
- INV-R-07 — hard boundary vs `PolicyEngine` / Supervisor
- `sor-compatibility-policy` — clarifications OK; no normative SoR edits
- Smallest correct diff; match `builder_engine/` style
- Do not dispatch until Architect authorizes Wave A slice or explicit EWO-002 authorization

---

## WO-TRACE

```text
PX-EXEC-EWO-001 PASS
  → Wave A engineering package review
  → AUTHORIZE PX-EXEC-EWO-002 (parallel with EWO-003)
  → implement → verify → PX-EXEC-EWO-002 report PASS
  → unblocks EWO-005
```
