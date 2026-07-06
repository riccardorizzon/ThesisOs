# PX-EXEC-EWO-009 — Qualification Plugin

Program: px-exec  
WorkOrder: PX-EXEC-EWO-009  
Capability: `px-exec-9-qualification-plugin`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-009-20260706.md`  
SoR: §8.2 qualification, §7.3 post-integration-qwo, §6.3 events, §10.3 Supervisor escalation, INV-R-07/08/16  
Verdict: **PASS**  
Timestamp: 2026-07-06T04:42:00+02:00  

---

## Summary

Implemented `builder_engine/qualification.py` with MB2 Qualification Plugin per SoR §8.2:
`QualificationPlugin` (`spawn`, `collect_evidence`, `report`, `on_action`), registry bootstrap
(`register_qualification_plugin`), and rule-action executor (`execute_qualification_action`).

Qualification runs after `IntegrationPassed` when the Rule Engine guard `coverage_gate: passed`
matches (`post-integration-qwo`). Coverage failure blocks `QwoSpawned` (§7.3). Spawn or evidence
failure emits `QwoFailed` plus `RuntimeEscalated` with `supervisor_action: WAIT` (INV-R-16).
Phase 2 stub reads spawn outcomes from fixture YAML — extension point documented for live QWO
evidence collection in a future act.

**Does not satisfy §13.3 golden path PASS** — replay bundle requires separate authorization.
**Does not claim MB2 promotion.** Phase 2 plugin trio is now complete.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/qualification.py` | New — QualificationPlugin + registry/rule hooks |
| `builder_engine/tests/test_qualification_plugin.py` | New — 8 acceptance tests |
| `builder_engine/tests/fixtures/qwo_spawn_context.yaml` | New — coverage gate fixtures |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| QualificationPlugin satisfies §8.2 interface; registers via PluginRegistry | ✓ |
| IntegrationPassed + coverage gate → QwoSpawned in rule test | ✓ |
| Coverage fail → no QwoSpawned (§7.3) | ✓ |
| Failure path emits QwoFailed + RuntimeEscalated (WAIT) | ✓ |
| No Governance auto-approval in plugin | ✓ |
| `make unit-builder-engine` | ✓ **183 passed** |
| No §13.3 PASS or MB2 promotion claim | ✓ |

---

## Traceability

| Req | SoR / INV | Evidence |
|-----|-----------|----------|
| REQ-19 | §8.2 qualification plugin spawns QWO | `test_qwo_spawn_on_integration_passed`, `test_rule_action_triggers_qualification` |
| REQ-10 | §8.2 Plugin registry | `test_qualification_plugin_registers` |
| §8.2 | qualification interface | `spawn`, `collect_evidence`, `report` |
| §7.3 | post-integration-qwo rule hook | `test_rule_action_triggers_qualification` |
| §6.3 | QwoSpawned, QwoFailed | spawn + failure tests |
| §10.3 | Supervisor WAIT on failure | `test_qwo_failed_escalates` + projection WAIT |
| INV-R-07 | No governance in plugin | plugin reads checkpoint/fixture only |
| INV-R-08 | Lifecycle via typed events | event bus publish in spawn/collect_evidence |
| INV-R-16 | WAIT escalation on qualification failure | `RuntimeEscalated` + projection |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/qualification.py` | yes (new) |
| `builder_engine/tests/test_qualification_plugin.py` | yes |
| `builder_engine/tests/fixtures/qwo_spawn_context.yaml` | yes |
| `builder_engine/integration.py` | no (read-only context) |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR / governance | no |

---

## Verification

```text
make unit-builder-engine → 183 passed in 0.80s
```

---

## Phase 2 completion

| EWO | Status |
|-----|--------|
| PX-EXEC-EWO-007 Merge Plugin | PASS |
| PX-EXEC-EWO-008 Integration Plugin | PASS |
| PX-EXEC-EWO-009 Qualification Plugin | **PASS** |

---

```text
Milestone Status: PASS
Repository Status: main @ 4d876ec (+ EWO-009 changes uncommitted)
Remaining Scope: §13.3 golden path replay (separate authorization)
Known Risks: Phase 2 stub uses fixture spawn/evidence outcomes; live QWO subprocess deferred
Recommended Next Action: WAIT — AUTHORIZE §13.3 golden path audit when ready
```
