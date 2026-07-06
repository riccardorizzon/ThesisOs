# PX-EXEC-EWO-008 — Integration Plugin

Program: px-exec  
WorkOrder: PX-EXEC-EWO-008  
Capability: `px-exec-8-integration-plugin`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-008-20260706.md`  
SoR: §8.2 integration, §7.3 post-merge-integration, §6.3 events, §10.2 CI guard, INV-R-07/08/14  
Verdict: **PASS**  
Timestamp: 2026-07-06T04:35:00+02:00  

---

## Summary

Implemented `builder_engine/integration.py` with MB2 Integration Plugin per SoR §8.2:
`IntegrationPlugin` (`start`, `run_checks`, `report`, `on_action`), registry bootstrap
(`register_integration_plugin`), and rule-action executor (`execute_integration_action`).

Integration runs after `MergeCompleted` when the Rule Engine guard `ci_status: passed`
matches (`post-merge-integration`). CI failure blocks `IntegrationStarted` (§10.2).
Phase 2 stub reads check outcomes from fixture YAML — extension point documented for
live `make ci` subprocess in a future EWO.

**Does not satisfy §13.3 golden path PASS** — Qualification plugin (EWO-009) remains
separate. **Does not claim MB2 promotion.**

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/integration.py` | New — IntegrationPlugin + registry/rule hooks |
| `builder_engine/tests/test_integration_plugin.py` | New — 8 acceptance tests |
| `builder_engine/tests/fixtures/integration_checks.yaml` | New — CI guard fixtures |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| IntegrationPlugin satisfies §8.2 interface; registers via PluginRegistry | ✓ |
| Spawned only when MergeCompleted + CI guard passes in rule test | ✓ |
| CI fail → no IntegrationStarted (§10.2) | ✓ |
| IntegrationPassed / Failed events emitted | ✓ |
| `make unit-builder-engine` | ✓ **175 passed** |
| No §13.3 PASS or MB2 promotion claim | ✓ |

---

## Traceability

| Req | SoR / INV | Evidence |
|-----|-----------|----------|
| REQ-10 | §8.2 Plugin registry | `test_integration_plugin_registers` |
| REQ-16 (partial) | §13.3 integration stage prep | `test_rule_action_triggers_integration` |
| §8.2 | integration interface | `start`, `run_checks`, `report` |
| §8.4 | Plugin failure events | `test_integration_failed_event` |
| §6.3 | IntegrationStarted/Passed/Failed | `test_integration_passed_event`, `test_integration_start_on_merge_completed` |
| §7.3 | post-merge-integration rule hook | `test_rule_action_triggers_integration` |
| §10.2 | CI guard | `test_integration_blocked_on_ci_fail`, `test_fixture_ci_fail_blocks_via_integration_id` |
| INV-R-07 | No governance in plugin | plugin reads checkpoint/fixture only |
| INV-R-08 | Lifecycle via typed events | event bus publish in start/run_checks |
| INV-R-14 | Registry resolve only | `execute_integration_action` via registry |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/integration.py` | yes (new) |
| `builder_engine/tests/test_integration_plugin.py` | yes |
| `builder_engine/tests/fixtures/integration_checks.yaml` | yes |
| `builder_engine/merge.py` | no (read-only context) |
| `builder_engine/qualification.py` | no (EWO-009) |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Verification

```text
make unit-builder-engine → 175 passed in 0.73s
```

---

## Downstream

| EWO | Status after PASS |
|-----|-------------------|
| PX-EXEC-EWO-009 Qualification Plugin | **ready** — pending `AUTHORIZE PX-EXEC-EWO-009` |
| §13.3 golden path replay | blocked until EWO-009 + separate authorization |

---

```text
Milestone Status: PASS
Repository Status: main @ a037bae (+ EWO-008 changes uncommitted)
Remaining Scope: PX-EXEC-EWO-009 Qualification Plugin
Known Risks: Phase 2 stub uses fixture check outcomes; live CI subprocess deferred
Recommended Next Action: ASEP: AUTHORIZE PX-EXEC-EWO-009
```
