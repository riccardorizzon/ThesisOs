# PX2 Wave C — Dispatch Record

> **Supervisor:** Engineering Supervisor  
> **Date:** 2026-07-04  
> **Prerequisite:** Integration B **PASS**

---

## Dispatch mode

**Single sub-agent** — Wave C is sequential per `px2-parallel.yaml`.

```text
Integration B PASS
      ↓
Dispatch Wave C
      └── Sub-agent G → PX2-EWO-007
      ↓
Integration C review
      ↓
WAIT (Wave D not auto-dispatched)
```

---

## WorkOrder dispatched

| EWO | Sub-agent | Capability | Status |
|-----|-----------|------------|--------|
| PX2-EWO-007 | G | PX-2.2 Review workspace | implemented |

---

## Integration C (supervisor, post-EWO)

- Wire `Revisione` tab in RightRail to pending proposals / review queue
- Verify entry points: Home, Writing ⌘⇧R, outline
- `make ci` + `.asep/reports/PX2-INTEGRATION-C.md`

---

## WO-TRACE

```text
Integration B → PX2-WAVE-C-DISPATCH → PX2-EWO-007 → Integration C → WAIT
```
