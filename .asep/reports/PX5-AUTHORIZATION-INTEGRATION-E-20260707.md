# Architect Authorization — PX-5 Integration E (Wave E)

Program: thesisos-product-v2  
Milestone: PX-5 — Research  
Role: engineering  
Status: **AUTHORIZED**  
Authorized EWO: **PX5-EWO-008** — Satellite node layer  
Pre-flight: **PASS**  
Operator command: `AUTHORIZE Integration E`  
Timestamp: 2026-07-07

---

## Pre-flight summary

| Check | Result |
|-------|--------|
| PX5-INTEGRATION-D | ✓ PASS — `.asep/reports/PX5-INTEGRATION-D.md` |
| PX5-EWO-004…007 | ✓ implemented |
| Wave D complete | ✓ |
| Wave E backlog | ✓ `.asep/reports/PX5-WAVE-E-BACKLOG.md` |
| `make ci` | ✓ green @ `b6c04da9` |
| Repository | ✓ clean @ main |
| First executable EWO | ✓ PX5-EWO-008 |

---

## Authorized scope (Wave E)

| EWO | Title | Dispatch |
|-----|-------|----------|
| **PX5-EWO-008** | Satellite node layer | **Execute now** |
| **PX5-EWO-009** | Basket + Writing handoff | Authorized — after 008 PASS |
| **PX5-EWO-010** | Saved views persistence | Authorized — parallel after 008 PASS |
| PX5-EWO-011 | Minimap + cluster + hard-limit | Not authorized — blocked on 009 + 010 |
| PX5-INTEGRATION-E | Wave E merge review | Supervisor — after 011 |

---

## Scope boundary

Product code only in `frontend/` and `backend/app/`. Does **not** authorize:

- MB2 Runtime / SoR / Constitution modifications
- px-exec Runtime Engineering
- PX-6 Polish
- QWO-PX5-001 (post Integration E)

---

## WO-TRACE

```text
PX5-INTEGRATION-D PASS
  → AUTHORIZE Integration E → PX5-EWO-008 (execute now)
  → PX5-EWO-009 ∥ PX5-EWO-010 → PX5-EWO-011 → PX5-INTEGRATION-E
```

---

## Recommended next action

Execute **PX5-EWO-008** — satellite node layer + canvas graph API extension.
