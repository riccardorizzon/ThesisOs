# Execution Graph Observation — PX3-EWO-008

> **Type:** Conformance observation artifact (not Runtime Dependency Engine)  
> **SoR:** §4.2 Execution Graph · INV-R-01 · INV-R-12 boundary  
> **Date:** 2026-07-05

---

## Observation scope

PX-3 **observes** Program→Execution structure from the Program Graph. It does **not**
derive ReadySet, CriticalPath, or emit `ExecutionGraphDerived`.

| SoR entity | Product observation | Runtime exercised? |
|------------|---------------------|-------------------|
| `ExecutionNode` | Each workorder in `px3-parallel.yaml` rendered as read-only node | **No** |
| `ReadySet` | **Not computed** — absent from API schema and UI | **No** |
| `CriticalPath` | **Not computed** — absent from API schema and UI | **No** |
| Wave DAG | `depends_on_wave` + `merge_order` edges parsed from yaml | **No** |

---

## INV-R-01 audit table

Every displayed node maps 1:1 to a Program Graph workorder declaration:

| Node ID | Wave | Type | Program Graph source |
|---------|------|------|----------------------|
| PX3-EWO-001 | wave_a_foundation | ewo | `waves.wave_a_foundation.workorders` |
| PX3-EWO-002 | wave_a_core | ewo | `waves.wave_a_core.workorders` |
| PX3-EWO-003 | wave_a_core | ewo | `waves.wave_a_core.workorders` |
| PX3-EWO-004 | wave_a_integration | integration | `waves.wave_a_integration.workorders` |
| PX3-EWO-005 | wave_b_projection | ewo | `waves.wave_b_projection.workorders` |
| PX3-EWO-006 | wave_b_supervisor | ewo | `waves.wave_b_supervisor.workorders` |
| PX3-EWO-007 | wave_b_conformance_integration | integration | `waves.wave_b_conformance_integration.workorders` |
| PX3-EWO-008 | wave_c_execution_graph | ewo | `waves.wave_c_execution_graph.workorders` |
| PX3-EWO-009 | wave_c_job_fsm | ewo | `waves.wave_c_job_fsm.workorders` |
| PX3-EWO-010 | wave_c_conformance_integration | integration | `waves.wave_c_conformance_integration.workorders` |

**Count:** 10 nodes · 10 yaml workorders · **1:1 match**

---

## INV-R-12 boundary

**Invariant:** Observability surfaces MUST NOT compute scheduling decisions independently of Runtime.

**Evidence:**

1. `build_program_graph_observation()` parses `.asep/programs/px3-parallel.yaml` only.
2. API response schema excludes `ready_set`, `critical_path`, `ready_jobs`, `dispatch`.
3. `ProgramTracePanel` displays structure; banner states INV-R-12 boundary explicitly.
4. Tests: `test_program_graph_does_not_compute_ready_set` asserts forbidden keys absent.

Code: `backend/app/services/conformance/program_graph.py`  
UI: `frontend/components/conformance/ProgramTracePanel.tsx`

---

## What this does NOT prove

- `ExecutionGraphDerived` event emission
- Dependency Engine derivation (MB2-Q-001…003)
- ReadySet / CriticalPath correctness
- Runtime scheduling

Class: **Observable** (class B).
