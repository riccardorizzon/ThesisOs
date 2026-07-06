# Engineering WorkOrder Proposal — PX-EXEC-EWO-008

> **Status:** PROPOSED — blocked until PX-EXEC-EWO-007 **IMPLEMENTED**  
> **Prerequisites:** PX-EXEC-EWO-007 **PENDING**; Phase 2 dispatch authorized @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P2 — Execution Plugins |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-8-integration-plugin` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-008 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on develop authorization) → `done` (on PASS report) |

---

## Objective

Implement the **Integration Plugin** per SoR §8.2: `start(integration_id)`,
`run_checks()`, `report()` — registered via Plugin Registry, spawned on `MergeCompleted`
when Rule Engine guard `ci_status: passed` matches (§7.3 `post-merge-integration`),
emitting `IntegrationStarted`, `IntegrationPassed`, `IntegrationFailed` — **without**
Qualification plugin execution, **without** Product Plane mutations, and **without**
claiming §13.3 golden path PASS.

This EWO replaces manual integration review orchestration steps from
`orchestrate-builders` for the Reference Implementation golden path.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-008 deliverable |
|-------|-------------|---------------------|
| **§8.2** integration interface | `start`, `run_checks`, `report` | `IntegrationPlugin` in `integration.py` |
| **§7.3** `post-merge-integration` | MergeCompleted + CI → integration | Rule hook + plugin execute |
| **§6.3** Events | IntegrationStarted/Passed/Failed | Bus publish |
| **§10.2** CI guard | No integration start on CI fail | `run_checks()` gate |

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-10 | Plugin registry | MB2-Q4 | MB2-Q-010 |
| REQ-16 | PX-2 golden path | §13.3 | MB2-Q-018 (integration stage) |

### Invariants

| Invariant | EWO-008 enforcement |
|-----------|---------------------|
| **INV-R-07** | Integration checks are Runtime scope — no Governance policy in plugin |
| **INV-R-08** | Lifecycle via typed events |
| **INV-R-14** | Registry resolve only — core does not import integration impl directly |

---

## Ownership (exclusive)

```text
builder_engine/integration.py                     # new — IntegrationPlugin + types
builder_engine/tests/test_integration_plugin.py   # new — unit tests
builder_engine/tests/fixtures/integration_checks.yaml  # new — CI guard fixtures
```

**Shared read-only:**

```text
builder_engine/plugin_registry.py
builder_engine/rules.py
builder_engine/events.py
builder_engine/merge.py              # MergeCompleted subscriber context only
```

---

## Forbidden paths

```text
backend/app/**
frontend/**
builder_engine/qualification.py     # EWO-009
builder_engine/merge.py               # EWO-007 — read-only unless integration touch approved
docs/superpowers/specs/mb2-engineering-runtime-spec.md
.asep/governance/**
```

**Behavioral exclusions:**

- QWO spawn (EWO-009)
- Product code changes
- §13.3 PASS claim
- MB2 promotion

---

## Scope

### In scope

1. **`IntegrationPlugin` class** — §8.2 interface methods
2. **CI check adapter** — pluggable `run_checks()` (stub: read checkpoint `ci_status` field for Phase 2)
3. **Rule Engine hook** — `post-merge-integration` action → integration plugin
4. **Event emission** — IntegrationStarted / Passed / Failed
5. **Unlock semantics** — IntegrationPassed enables downstream wave per px2-parallel model
6. **Tests** — see Acceptance tests
7. **EWO report** — `.asep/reports/PX-EXEC-EWO-008-integration-plugin.md`

### Out of scope

- Qualification plugin (EWO-009)
- Live `make ci` subprocess in default Phase 2 stub (document extension point)
- Full §13.3 automated replay

---

## Acceptance criteria (EWO exit)

- [ ] IntegrationPlugin satisfies §8.2; registers via PluginRegistry
- [ ] Spawned only when MergeCompleted + CI guard passes in rule test
- [ ] CI fail → no IntegrationStarted (§10.2)
- [ ] IntegrationPassed / Failed events emitted
- [ ] `make unit-builder-engine` green
- [ ] EWO report: **does not satisfy §13.3**

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_integration_plugin_registers` | Factory registers integration interface | §8.2 |
| `test_integration_start_on_merge_completed` | MergeCompleted + ci passed → start | §7.3 |
| `test_integration_blocked_on_ci_fail` | ci failed → no IntegrationStarted | §10.2 |
| `test_integration_passed_event` | run_checks pass → IntegrationPassed | §6.3 |
| `test_integration_failed_event` | run_checks fail → IntegrationFailed | §8.4 |
| `test_rule_action_triggers_integration` | post-merge-integration descriptor | §7.3 |

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-007 Merge Plugin | **PENDING** |
| Phase 2 dispatch authorization | **PASS** @ 2026-07-06 |
| Architect authorization for EWO-008 develop | **BLOCKED** (requires EWO-007 PASS) |

**Unblocks:** PX-EXEC-EWO-009 Qualification Plugin

---

## WO-TRACE

```text
EWO-007 PASS → AUTHORIZE PX-EXEC-EWO-008 → implement → verify → report PASS
  → unblocks EWO-009
```
