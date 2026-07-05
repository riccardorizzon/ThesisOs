# PX2 Wave B — Dispatch Record

> **Supervisor:** Engineering Supervisor  
> **Date:** 2026-07-04  
> **Prerequisite:** Integration A **PASS**

---

## Dispatch mode

**Parallel** — three sub-agents, exclusive ownership.

```text
Integration A PASS
      ↓
Dispatch Wave B (simultaneous)
      ├── Sub-agent D → PX2-EWO-003
      ├── Sub-agent E → PX2-EWO-004
      └── Sub-agent F → PX2-EWO-006
      ↓
Merge (merge_order: 003 → 004 → 006)
      ↓
Integration B review
      ↓
WAIT (Wave C not auto-dispatched)
```

---

## WorkOrders dispatched

| EWO | Sub-agent | Capability | Status |
|-----|-----------|------------|--------|
| PX2-EWO-003 | D | PX-2.2 AI panel + proposals | in_progress |
| PX2-EWO-004 | E | PX-2.3 Source interaction | in_progress |
| PX2-EWO-006 | F | PX-2.5 Session continuity | in_progress |

---

## Parallel conflict avoidance

| Risk | Mitigation |
|------|------------|
| EWO-006 vs EWO-003 on `proposalQueue.ts` | EWO-003 owns queue; EWO-006 reads via exported `getPendingProposalCount()` only |
| EWO-004 cite vs EWO-002 MarkdownEditor | EWO-004 owns `citationInsert.ts` + dispatches `thesisos:insert-citation` event; Integration B wires editor listener |
| EWO-003 vs EWO-004 on RightRail Fonte tab | EWO-003 owns RightRail shell + tabs; EWO-004 provides `SourcePeekReader` component; Integration B imports into Fonte slot |
| EWO-003 vs EWO-006 on WritingWorkspace | EWO-003 replaces AI panel with RightRail; do not modify WritingWorkspace layout beyond RightRail slot |

---

## Post-wave supervisor duties

1. Merge 003 → 004 → 006  
2. Integration B wiring  
3. `make ci`  
4. `.asep/reports/PX2-INTEGRATION-B.md`  
5. Capability graph update  
6. **WAIT** — no Wave C until explicit authorization  

---

## WO-TRACE

```text
Integration A → PX2-WAVE-B-DISPATCH → [D,E,F executing] → Integration B → WAIT
```
