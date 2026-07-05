# Supervisor Interaction Observation — PX3-EWO-006

> **Type:** Conformance observation artifact (not Runtime Supervisor)  
> **SoR:** §10 Supervisor interaction · INV-R-16  
> **Date:** 2026-07-05

---

## Observation scope

PX-3 **observes** Supervisor interaction semantics. It does **not** implement or
exercise the Engineering Runtime Supervisor.

| SoR signal | Product observation | Runtime exercised? |
|------------|---------------------|-------------------|
| `WAIT` | Region B fetch halted when `supervisor.state === WAIT` and wave job not delegated | **No** |
| Delegation clear | Region B fetch proceeds when `PX3-EWO-006` job status is `ready`/`running`/`pass` in projection | **No** |
| `STOP` | Not simulated in this EWO | **No** |

---

## INV-R-16 mapping

**Invariant:** Supervisor `WAIT` MUST halt autonomous Runtime progression until cleared.

**Observation evidence:**

1. Explain Page loads region **A** (header) first via `GET …/concepts/{slug}/header`.
2. Before region **B**, client reads read-only projection (`GET …/conformance/projection`).
3. If `supervisor.state === WAIT` and wave job `PX3-EWO-006` is not delegated,
   **definition fetch is not issued** — UI shows `explain-region-b-wait`.
4. When delegation observable in projection (job `running`), definition fetch proceeds.

Code: `frontend/components/knowledge/explain/supervisorObservation.ts`  
UI: `ExplainRegionWait`, `explain-supervisor-observation` banner.

---

## §10 delegation table (observed subset)

| Operator signal | Product analogue in PX-3 |
|-----------------|-------------------------|
| `WAIT` | Halt region B progression; banner + wait skeleton |
| Clear WAIT (delegation) | Projection shows EWO-006 job `running` → definition loads |

---

## What this does NOT prove

- Runtime queue pause/resume
- Engineering Supervisor FSM implementation
- MB2-Q-008 qualification

Class: **Observable** (class B).
