# PX2 Wave D — Dispatch Record

> **Supervisor:** Engineering Supervisor  
> **Date:** 2026-07-04  
> **Prerequisite:** Integration C **PASS**  
> **Authorization:** Explicit operator dispatch — `ASEP: Dispatch Wave D`

---

## Dispatch mode

**Single sub-agent** — Wave D is sequential per `px2-parallel.yaml`.

```text
Integration C PASS
      ↓
Dispatch Wave D
      └── Sub-agent H → PX2-EWO-008
      ↓
Integration D review (supervisor)
      ↓
WAIT (QWO-PX2-001 not auto-dispatched)
```

---

## WorkOrder dispatched

| EWO | Sub-agent | Capability | Status |
|-----|-----------|------------|--------|
| PX2-EWO-008 | H | Cross-cutting chrome + integration | implemented |

---

## Constraints (preserved)

- ADR-0036…0040 — IA, knowledge model, context engine, AI interaction, product state
- OR-1…OR-5 — runtime operational requirements
- PX-1 Foundation — AppShell navigation, six modules unchanged
- PX-2 Waves A–C — no regression to ContextBar, Writing, Sources, Review, Session

---

## Integration D (supervisor, post-EWO)

- Verify CommandPalette wired in AppShell; nav badges (Writing status, Review pending)
- Verify global shortcuts do not conflict with workspace-local handlers
- CoachMark onboarding flow on Home / Writing / ContextBar
- `make ci` + `.asep/reports/PX2-INTEGRATION-D.md`
- Capability graph update; **WAIT** for QWO authorization

---

## WO-TRACE

```text
Integration C → PX2-WAVE-D-DISPATCH → PX2-EWO-008 → Integration D → WAIT (QWO)
```
