# PX-EXEC-EWO-007 — Merge Plugin

Program: px-exec  
WorkOrder: PX-EXEC-EWO-007  
Capability: `px-exec-7-merge-plugin`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-007-20260706.md`  
SoR: §8.2 merge, §6.3 events, §7.3 post-ewo-merge, INV-R-03  
Verdict: **PASS**  
Timestamp: 2026-07-06T04:30:00+02:00  

---

## Summary

Extended `builder_engine/merge.py` with MB2 Merge Plugin per SoR §8.2:
`MergeContext`, `MergePlugin` (`eligible`, `execute`, `report`, `on_action`),
registry bootstrap (`register_merge_plugin`), and rule-action executor
(`execute_merge_action`). Era I `merge_eligibility()` stub retained unchanged.

Merge execution emits `MergeCompleted` / `MergeFailed` events and writes an
external-integrator manifest — **no in-process git mutations** (Era I D8).

**Does not satisfy §13.3 golden path PASS** — Integration and Qualification
plugins (EWO-008, 009) remain separate. **Does not claim MB2 promotion.**

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/merge.py` | Extended — `MergePlugin` + registry/rule hooks |
| `builder_engine/tests/test_merge_plugin.py` | New — 10 acceptance tests |
| `builder_engine/tests/fixtures/merge_order_graph.yaml` | New — INV-R-03 fixture |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| MergePlugin satisfies §8.2 interface; registers via PluginRegistry | ✓ |
| `eligible()` enforces merge_order (INV-R-03) with fixture graph | ✓ |
| `execute()` emits `MergeCompleted` or `MergeFailed`; no silent failure | ✓ |
| No in-process git mutations; external integrator manifest documented | ✓ |
| Rule Engine `post-ewo-merge` action triggers merge plugin in unit test | ✓ |
| Era I tests unchanged (`merge_eligibility`) | ✓ |
| `make unit-builder-engine` | ✓ **167 passed** |
| No §13.3 PASS or MB2 promotion claim | ✓ |

---

## Traceability

| Req | SoR / INV | Evidence |
|-----|-----------|----------|
| REQ-04 | INV-R-03 merge_order | `test_merge_order_enforced`, `test_merge_order_satisfied_after_prior_complete` |
| REQ-10 | §8.2 Plugin registry | `test_merge_plugin_registers` |
| REQ-16 (partial) | §13.3 merge stage prep | `test_rule_action_triggers_merge` — merge events only |
| §8.2 | merge interface | `eligible`, `execute`, `report` |
| §8.4 | Plugin failure events | `test_merge_execute_emits_failed` |
| §6.3 | MergeCompleted / MergeFailed | `test_merge_execute_emits_completed` |
| §7.3 | post-ewo-merge rule hook | `test_rule_action_triggers_merge` |
| Era I D8 | No git mutation | `test_no_git_mutation`, manifest `integrator: external` |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/merge.py` | yes (extend) |
| `builder_engine/tests/test_merge_plugin.py` | yes |
| `builder_engine/tests/fixtures/merge_order_graph.yaml` | yes |
| `builder_engine/plugin_registry.py` | no (read-only) |
| `builder_engine/rules.py` | no (read-only) |
| `builder_engine/dependency.py` | no (read-only `_merge_rank`) |
| `builder_engine/integration.py` | no (EWO-008) |
| `builder_engine/qualification.py` | no (EWO-009) |
| `backend/app/**` | no |
| `frontend/**` | no |
| SoR | no |

---

## Verification

```text
make unit-builder-engine → 167 passed in 1.08s
```

---

## Downstream

| EWO | Status after PASS |
|-----|-------------------|
| PX-EXEC-EWO-008 Integration Plugin | **ready** — pending `AUTHORIZE PX-EXEC-EWO-008` |
| PX-EXEC-EWO-009 Qualification Plugin | blocked until EWO-008 |

---

```text
Milestone Status: PASS
Repository Status: main @ 26a5d1a, changes uncommitted
Remaining Scope: PX-EXEC-EWO-008 Integration Plugin
Known Risks: Rule→plugin wiring is unit-tested; full golden-path replay deferred to EWO-009 + §13.3 act
Recommended Next Action: ASEP: AUTHORIZE PX-EXEC-EWO-008
```
