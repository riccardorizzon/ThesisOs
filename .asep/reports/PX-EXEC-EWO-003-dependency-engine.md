# PX-EXEC-EWO-003 — Dependency Engine

Program: px-exec  
WorkOrder: PX-EXEC-EWO-003  
Capability: `px-exec-3-dependency-engine`  
Authorization: `.asep/reports/PX-EXEC-AUTHORIZATION-EWO-003-20260706.md`  
Proposal: `.asep/proposals/PX-EXEC-EWO-003-dependency-engine.md`  
SoR: §4.1–§4.2, §5 @ 2026-07-05  
Verdict: **PASS**  
Timestamp: 2026-07-06T03:30:00+02:00  

---

## Summary

Implemented Program Graph loader and Dependency Engine per SoR §4.2: derive-only
Execution Graph from Governance program YAML, ready set with `merge_order` tie-break
(INV-R-03), cycle/reference validation, and `ExecutionGraphDerived` event emission via
Event Bus.

**Does not satisfy MB2-Q1** — qualification act and MB2-Q-001…003 remain separate.

---

## Deliverables

| Artifact | Change |
|----------|--------|
| `builder_engine/program_graph.py` | New — `ProgramGraph`, `ProgramGraphLoader`, validation |
| `builder_engine/dependency.py` | New — `DependencyEngine`, `ExecutionGraph`, `ExecutionNode` |
| `builder_engine/tests/test_dependency_engine.py` | New — 12 acceptance tests |
| `builder_engine/tests/fixtures/px_exec_program_minimal.yaml` | New |
| `builder_engine/tests/fixtures/px2_parallel_program_excerpt.yaml` | New |
| `builder_engine/tests/fixtures/px_exec_program_circular.yaml` | New |

---

## Acceptance criteria

| Criterion | Result |
|-----------|--------|
| Program Graph loads px-exec-style YAML | ✓ |
| Execution Graph derive-only (INV-R-02) | ✓ |
| Every node traces to Program Graph (INV-R-01) | ✓ |
| merge_order tie-break only (INV-R-03) | ✓ |
| Orphan / unknown dependency rejected | ✓ |
| Circular depends_on rejected | ✓ |
| `ExecutionGraphDerived` with stable hash | ✓ |
| Ready set empty when upstream incomplete | ✓ |
| PX-2 merge_order [003, 004, 006] excerpt | ✓ |
| Era I `compute_ready()` parity (wave 1) | ✓ |
| `make unit-builder-engine` | ✓ **87 passed** |
| No MB2-Q1 claim | ✓ |

---

## Traceability

| Req | SoR | Evidence |
|-----|-----|----------|
| REQ-02 | §4.2 derived graph | `DependencyEngine.derive()` |
| REQ-03 | §4.1 / INV-R-01 | `program_graph_ref` on every node |
| REQ-04 | INV-R-03 | merge_order tests |
| REQ-14 | §5 hook | `ExecutionNode.state` / ready preconditions |

---

## Scope guard

| Path | Touched |
|------|---------|
| `builder_engine/program_graph.py` | yes |
| `builder_engine/dependency.py` | yes |
| `builder_engine/tests/*` | yes |
| `builder_engine/rules.py` | no |
| `builder_engine/scheduler.py` | no (read-only in tests) |
| `backend/app/**` | no |
| `frontend/**` | no |
| `.asep/programs/px-exec.yaml` | no (read-only loader) |
| SoR | no |

---

## Unblocks

- **PX-EXEC-EWO-004** Job Queue (ready set + ExecutionNode ids)
- Integration A may proceed when EWO-002 also PASS

---

## WO-TRACE

```text
AUTHORIZE PX-EXEC-EWO-003 → implement → verify PASS
  → next: EWO-002 or Integration A (when both PASS)
  → EWO-004 unblocked
```
