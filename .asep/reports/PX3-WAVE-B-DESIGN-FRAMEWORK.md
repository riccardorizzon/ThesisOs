# PX-3 Wave B — Design Framework (RATIFIED · DISPATCH AUTHORIZED)

> **Status:** **DISPATCH AUTHORIZED** — `.asep/reports/PX3-AUTHORIZATION-WAVE-B-20260705.md`  
> **Architect decision:** `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-FRAMEWORK.md`  
> **Backlog review:** `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-BACKLOG-REVIEW.md`  
> **Date:** 2026-07-05

---

## Principle

Wave B is **not** the next product feature wave.

Wave B is the next **SoR conformance** wave. Product work is a *means* to verify that
product behavior aligns with the SoR contract — PX-3 does **not** exercise the Runtime.

```text
Wrong:  Wave B → Explain Page
Wrong:  Wave B → Projection Exercise   (implies Runtime exercise)
Right:  Wave B → Projection Conformance (§9)
        Secondary → Supervisor Conformance (§10)
        Optional → §11 only if natural — not forced
```

---

## Wave B objectives (Architect approved)

| Tier | SoR target | PX-3 exercisability |
|------|------------|---------------------|
| **Primary** | §9 Projection Conformance | Yes |
| **Secondary** | §10 Supervisor Interaction Observation | Observable |
| **Optional** | §11 Failure semantics | Observable — do not force artificial FAIL paths |

**Not in Wave B primary scope:** §4.2 Execution Graph, §11 forced failure, §12 Recovery.

---

## Selection algorithm

1. Read live coverage matrix — primary targets: **Yes**; secondary: **Observable**.
2. Name the wave by **SoR conformance objective**, not product module.
3. Draft EWOs with `covers:` (max **3 elements** per EWO).
4. Simulate `Coverage += union(EWO.covers)` — reject wave if marginal SoR gain unclear.
5. Backlog review → explicit `AUTHORIZE` for Wave B implementation.

---

## Wave selection rule

> **Which new part of the SoR becomes verifiable because of this wave?**

Not: *Which features does it add?*

---

## Deferred themes (not Wave B)

| Theme | Reason |
|-------|--------|
| Execution Graph Conformance (§4.2) | Observable — defer to later wave |
| Rule model (§7) | No (Runtime) |
| Plugin Registry (§8) | No (Runtime) |
| Recovery Conformance (§12) | No (Qualification) |
| Forced Failure Exercise (§11) | Optional only; artificial paths forbidden |

**Explain Page** is an acceptable product vehicle **only if** EWO primary objective remains
§9 Projection Conformance with `covers` capped at three elements.

---

## Authorization gate

| Check | Status |
|-------|--------|
| Framework ratified by Architect | ✅ 2026-07-05 |
| Yes/Observable taxonomy | ✅ |
| Backlog review PASS | ✅ 2026-07-05 |
| Program Graph registered | ✅ EWO 005–007 |
| Wave B dispatch authorized | ✅ `.asep/reports/PX3-AUTHORIZATION-WAVE-B-20260705.md` |
| First executable EWO | **PX3-EWO-005** |

---

## Wave B exit criteria

Wave B PASS requires: all EWOs PASS; Conformance Integration B PASS; no N-class in log;
coverage +≥1 Yes or Observable row vs Wave A baseline.

---

## WO-TRACE

```text
Wave A Conformance Review PASS
  → Coverage taxonomy draft
  → Architect Decision RATIFIED
  → PX3-WAVE-B-BACKLOG.md (draft)
  → Backlog review → AUTHORIZE PX-3 Wave B dispatch (future)
```
