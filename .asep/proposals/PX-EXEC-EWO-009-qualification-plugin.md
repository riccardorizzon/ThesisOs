# Engineering WorkOrder Proposal — PX-EXEC-EWO-009

> **Status:** PROPOSED — blocked until PX-EXEC-EWO-008 **IMPLEMENTED**  
> **Prerequisites:** PX-EXEC-EWO-008 **PENDING**; Phase 2 dispatch authorized @ 2026-07-06

| Field | Value |
|-------|-------|
| **Program** | `.asep/programs/px-exec.yaml` |
| **Phase** | PX-EXEC-P2 — Execution Plugins |
| **SoR revision** | 2026-07-05 (read-only) |
| **Capability** | `px-exec-9-qualification-plugin` |

---

## Identity

| Field | Value |
|-------|-------|
| **WorkOrder id** | PX-EXEC-EWO-009 |
| **Type** | **EWO** — Platform / Reference Implementation |
| **EWO category** | **Infrastructure** |
| **Milestone** | MB2 — Engineering Runtime |
| **Layer** | Runtime (Build Control Plane) |
| **Lifecycle transition** | `specified` → `implementing` (on develop authorization) → `done` (on PASS report) |

---

## Objective

Implement the **Qualification Plugin** per SoR §8.2: `spawn(qwo_id)`,
`collect_evidence()`, `report()` — registered via Plugin Registry, triggered on
`IntegrationPassed` when coverage gate passes (§7.3 `post-integration-qwo`), emitting
`QwoSpawned`, `QwoPassed`, `QwoFailed`, escalating to Supervisor WAIT on failure —
**without** Product Plane mutations, **without** auto-accepting QWO disposition, and
**without** claiming MB2 promotion (§13.3 bundle is separate authorization).

This EWO completes Phase 2 plugin trio and enables live QWO spawn evidence for REQ-19
beyond rule-only MB2-Q-006.

---

## SoR mapping

### Primary sections

| SoR § | Requirement | EWO-009 deliverable |
|-------|-------------|---------------------|
| **§8.2** qualification interface | `spawn`, `collect_evidence`, `report` | `QualificationPlugin` in `qualification.py` |
| **§7.3** `post-integration-qwo` | IntegrationPassed + coverage → qualification | Rule hook + plugin |
| **§6.3** Events | QwoSpawned, QwoPassed, QwoFailed | Bus publish |
| **§10.3** Supervisor escalation | Plugin failure → WAIT | RuntimeEscalated or QwoFailed path |

### Traceability

| Req ID | Requirement | Gate | Test ID (future — not claimed now) |
|--------|-------------|------|-------------------------------------|
| REQ-19 | Qualification plugin spawns QWO | MB2-Q2 | MB2-Q-006 (live extension) |
| REQ-16 | PX-2 golden path | §13.3 | MB2-Q-018 |
| REQ-10 | Plugin registry | MB2-Q4 | MB2-Q-010 |

### Invariants

| Invariant | EWO-009 enforcement |
|-----------|---------------------|
| **INV-R-07** | No Governance auto-approval in plugin |
| **INV-R-08** | QWO lifecycle via typed events |
| **INV-R-16** | WAIT escalation on qualification failure |

---

## Ownership (exclusive)

```text
builder_engine/qualification.py                   # new — QualificationPlugin + types
builder_engine/tests/test_qualification_plugin.py # new — unit tests
builder_engine/tests/fixtures/qwo_spawn_context.yaml  # new — coverage gate fixtures
```

**Shared read-only:**

```text
builder_engine/plugin_registry.py
builder_engine/rules.py
builder_engine/events.py
builder_engine/integration.py     # IntegrationPassed context only
builder_engine/projection.py      # optional qwo section update on events
```

---

## Forbidden paths

```text
backend/app/**
frontend/**
docs/superpowers/specs/mb2-engineering-runtime-spec.md
.asep/governance/**               # no auto-approval policy changes
```

**Behavioral exclusions:**

- Auto-accept QWO PARTIAL/FAIL (Supervisor gate preserved)
- Product qualification execution (QWO runs remain governed separately)
- MB2 promotion / `mb2-complete` tag
- §13.3 PASS without replay bundle authorization

---

## Scope

### In scope

1. **`QualificationPlugin` class** — §8.2 interface methods
2. **QWO spawn descriptor** — emit `QwoSpawned` with qwo_id, program_id, evidence paths stub
3. **Evidence collection stub** — `collect_evidence()` returns structured artifact refs (no Ground Truth edits)
4. **Rule Engine hook** — `post-integration-qwo` action → qualification plugin
5. **Failure escalation** — QwoFailed → Supervisor WAIT signal (event or projection marker)
6. **Tests** — see Acceptance tests
7. **EWO report** — `.asep/reports/PX-EXEC-EWO-009-qualification-plugin.md`

### Out of scope

- Phase 3 dashboard / metrics plugins
- Full PX-2 parallel end-to-end replay (separate §13.3 authorization)
- MB2 promotion

---

## Acceptance criteria (EWO exit)

- [ ] QualificationPlugin satisfies §8.2; registers via PluginRegistry
- [ ] IntegrationPassed + coverage gate → QwoSpawned in rule test
- [ ] Failure path emits QwoFailed + escalation marker
- [ ] No Governance auto-approval
- [ ] `make unit-builder-engine` green
- [ ] EWO report: Phase 2 plugins complete; **§13.3 replay not claimed**

---

## Acceptance tests (design specification)

| Test ID | Description | SoR / INV |
|---------|-------------|-----------|
| `test_qualification_plugin_registers` | Factory registers qualification interface | §8.2 |
| `test_qwo_spawn_on_integration_passed` | IntegrationPassed + coverage → QwoSpawned | §7.3, REQ-19 |
| `test_qwo_blocked_on_coverage_fail` | coverage fail → no QwoSpawned | §7.3 |
| `test_qwo_failed_escalates` | spawn/check fail → WAIT signal | INV-R-16 |
| `test_rule_action_triggers_qualification` | post-integration-qwo descriptor | §7.3 |
| `test_collect_evidence_structure` | report() returns evidence refs | §8.2 |

---

## Dependencies

| Depends on | Status |
|------------|--------|
| PX-EXEC-EWO-008 Integration Plugin | **PENDING** |
| Phase 2 dispatch authorization | **PASS** @ 2026-07-06 |
| Architect authorization for EWO-009 develop | **BLOCKED** (requires EWO-008 PASS) |

**Unblocks:** Phase 2 integration review; §13.3 golden path audit authorization

---

## WO-TRACE

```text
EWO-008 PASS → AUTHORIZE PX-EXEC-EWO-009 → implement → verify → report PASS
  → Phase 2 EWO trio complete
  → WAIT: AUTHORIZE §13.3 golden path audit
```
