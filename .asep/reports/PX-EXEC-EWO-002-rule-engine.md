# PX-EXEC-EWO-002 — Rule Engine

Program: px-exec  
WorkOrder: PX-EXEC-EWO-002  
Capability: `px-exec-2-rule-engine`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-002-20260706.md`  
Proposal: `.asep/proposals/PX-EXEC-EWO-002-rule-engine.md`  
SoR: §7.1–§7.4 @ 2026-07-05  
Verdict: **PASS**  
Timestamp: 2026-07-06T03:30:00+02:00  

---

## Summary

Implemented the Runtime Rule Engine in `builder_engine/rules.py`: §7.2 YAML pack
loader (with line parser for nested rule entries), `ActionDescriptor` / `NoMatch`,
deterministic guard evaluation against event payload + checkpoint snapshot,
INV-R-07 governance guard rejection, and Event Bus subscriber integration via
`as_subscriber()` / `register()`.

Golden PX-2 parallel rules fixture (§7.3) and negative governance fixture included.

**Does not satisfy MB2-Q2** — Rule Engine reference implementation only; MB2-Q-004…006
qualification gates not run.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/rules.py` | New — RuleEngine, ActionDescriptor, pack loader, subscriber hook |
| `builder_engine/tests/test_rules.py` | New — 14 acceptance tests |
| `builder_engine/fixtures/px2_parallel_rules.yaml` | New — §7.3 golden path (4 rules) |
| `builder_engine/fixtures/rule_pack_invalid_governance.yaml` | New — INV-R-07 negative fixture |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| Rule pack loads §7.2 schema; invalid schema raises clear error | ✓ |
| Rules sorted by `priority`; first match wins | ✓ |
| Same event + same checkpoint ⇒ same result (INV-R-13) | ✓ |
| Governance guard keys rejected (INV-R-07) | ✓ |
| Golden PX-2 fixture: four §7.3 rules parse and match | ✓ |
| Rule Engine as Event Bus subscriber; no state mutation | ✓ |
| RuleEngine separate from PolicyEngine (no `policy.py` import) | ✓ |
| EWO report traceability §7.1–§7.4, REQ-09 | ✓ |
| No MB2-Q2 claim | ✓ |

---

## Verification

```text
pytest tests/test_rules.py -q  → 14 passed
```

Full suite (`make unit-builder-engine`): **107 passed, 1 failed** — failure is
`tests/test_job_queue.py::test_materialize_from_execution_graph` from parallel
EWO-004 work (ready-queue ordering); `job_queue.py` is outside EWO-002 exclusive
write scope and was not modified.

Era I + EWO-002 tests: **100 passed** when excluding untracked EWO-004 job-queue tests.

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-01 | §6, §7 event-driven | Subscriber on publish; action descriptors |
| REQ-09 | §7, INV-R-13 | `test_deterministic_match`; priority ordering |
| REQ-13 | §7.3 escalation rule | `qwo-escalate-supervisor` → notification descriptor |
| REQ-19 | §7.3 qualification rule | `post-integration-qwo` → qualification descriptor |
| INV-R-07 | §7.4 | Forbidden prefix guard; `test_governance_keys_rejected` |
| INV-R-08 | §7.1 | Descriptors only; evaluate does not mutate queue/state |
| INV-R-13 | §7.1 | Replay determinism test |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/rules.py` | yes |
| `builder_engine/tests/test_rules.py` | yes |
| `builder_engine/fixtures/*rules*.yaml` | yes |
| `builder_engine/events.py` | no (read-only API) |
| `builder_engine/policy.py` | no |
| `builder_engine/job_queue.py` | no |
| `backend/app/**` | no |
| SoR | no |

---

## Qualification boundary

This EWO delivers Phase 1 Rule Engine reference implementation and unit tests.
It **does not satisfy MB2-Q2** and does not issue MB2-Q-004…006 evidence.

---

## Unblocks

- **PX-EXEC-EWO-005** Scheduler (reactive dispatch rules consume action descriptors)

---

## WO-TRACE

```text
PX-EXEC-EWO-001 PASS → AUTHORIZE EWO-002 → implement → verify → PASS
  → next: EWO-005 scheduler wiring
```
