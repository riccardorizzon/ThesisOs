# Architect Authorization — PX3-EWO-008

Program: PX-3  
Work Order: **PX3-EWO-008**  
Status: **AUTHORIZED**  
Scope: **EWO-only** — Wave C sequential dispatch; EWO-009 and EWO-010 NOT authorized  
Timestamp: 2026-07-05

---

## Primary objective

Execution Graph Observation (§4.2) — Observable

## Secondary objective

Read-only Program Trace API + UI (wave DAG, merge_order, depends_on).

## Conformance targets

- §4.2 Execution Graph
- INV-R-01
- Class B — Observable (not Qualified)

## Constraints

- MB2 SoR normative; Runtime read-only; Governance frozen
- Product code only; scope bounded by approved `covers:`
- **Do not** compute ReadySet or scheduling decisions (INV-R-12 boundary)
- No `builder_engine/` changes
- No Dependency Engine, `ExecutionGraphDerived`, MB2-Q-001…003

## Explicitly NOT in scope

- Rule Model (§7), Plugin Contracts (§8), Recovery (§12)
- Job FSM primary evidence (EWO-009)
- Integration C (EWO-010)

## Upon completion

**STOP** — Architect review before authorizing PX3-EWO-009.
