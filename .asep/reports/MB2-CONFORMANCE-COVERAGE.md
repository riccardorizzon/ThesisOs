# MB2 Conformance Coverage

> **Metric:** Specification coverage — not code coverage, not test count.  
> **SoR:** `docs/superpowers/specs/mb2-engineering-runtime-spec.md` (2026-07-05)  
> **Program:** PX-3 Knowledge Experience (first Runtime Conformance Program)  
> **Updated:** 2026-07-05 — Architect ratification; Yes/Observable column; Conformance framing

---

## Live coverage model

Each conformance EWO declares `covers:` (see `.asep/templates/conformance-ewo-template.md`).

**Cap:** at most **three elements** per EWO `covers:` block (one per list typical).

After each wave:

```text
Coverage := union(all implemented EWO.covers)
```

Manual matrix rows update from that union — not from post-hoc narrative.

---

## PX-3 exercisability (Architect ratified 2026-07-05)

| PX-3 exercisability | Meaning | Wave B+ primary target? |
|---------------------|---------|-------------------------|
| **Yes** | Fully demonstrable in PX-3 | **Yes** |
| **Observable** | PX-3 observes effects; cannot prove Runtime contract | Secondary only |
| **No (Runtime)** | Requires Reference Implementation | **No** — defer to px-exec |
| **No (Qualification)** | Requires MB2-Q gates | **No** — defer to MB2-Q |

**Not "Parziale".** Observable is explicit: product may reflect SoR semantics without
proving Runtime implementation.

### Class A/B/C (wave gating — retained)

| Class | Maps to | Wave B+ in PX-3? |
|-------|---------|-----------------|
| **A** | Yes | Yes — primary objectives |
| **B** | Observable | Yes — secondary; simulation/observation contract |
| **C** | No (Runtime) or No (Qualification) | **No** |

Architect decision: `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-FRAMEWORK.md`

---

## Wave selection rule

Each wave answers:

> **Which new part of the SoR becomes verifiable because of this wave?**

PX-3 validates SoR **sufficiency for product development** — not Runtime implementation.

---

## Summary

| Metric | Value |
|--------|-------|
| EWOs complete | 7 (Wave A: 4 · Wave B: 3) |
| Integrations | 2 (A + B) |
| Conformance Log entries | **0** |
| N-class | **0** |
| Rows with evidence (✅ or ⏳) | **7 / 15** |
| Yes/Observable rows still open | **2** (Execution Graph, Failure — optional) |
| Wave B status | **COMPLETE** |
| Wave C status | **DISPATCH AUTHORIZED — EWO-008 first** |
| Architect Review Wave B | `.asep/reports/PX3-ARCHITECT-REVIEW-WAVE-B-20260705.md` |
| Runtime Engineering | **NOT AUTHORIZED** |
| PX-4 | **NOT AUTHORIZED** |
| Next artifact (post Wave C) | `MB2-CONFORMANCE-ASSESSMENT.md` |

---

## Coverage matrix

Legend: **Status** — ✅ evidenced · ⏳ partial evidence · ❌ not evidenced  
**PX-3?** — Yes · Observable · No (Runtime) · No (Qualification)

| SoR area | § | Status | PX-3 exercisability | Class | Wave A / union evidence |
|----------|---|--------|---------------------|-------|-------------------------|
| **Program Graph** | 4.1 | ✅ | Yes | A | EWO-001…004 backlog, `px3-parallel.yaml`, merge_order |
| **Execution Graph** | 4.2 | ❌ | Observable | B | ReadySet not derived; effects visible in program yaml only |
| **Job / Checkpoint** | 4.3–4.4 | ❌ | No (Runtime) | C | Awaits Reference Implementation |
| **Projection document** | 4.5, §9 | ✅ | Yes | A | PX3-PROJECTION-SNAPSHOT; API + Explain consumer |
| **Job FSM** | 5 | ❌ | Observable | B | Program `status:` — not JobState enum proof |
| **Event model** | 6 | ❌ | No (Runtime) | C | Event catalog / emission — px-exec |
| **Rule model** | 7 | ❌ | No (Runtime) | C | Event→Action engine — Reference Implementation |
| **Plugin contracts** | 8 | ❌ | No (Runtime) | C | PluginRegistry — not before Runtime |
| **Projection model** | 9 | ✅ | Yes | A | EWO-005 PASS — schema v1 API + snapshot |
| **Supervisor interaction** | 10 | ✅ | Observable | B | EWO-006 observation — WAIT halts region B; PX3-SUPERVISOR-OBSERVATION |
| **Failure semantics** | 11 | ❌ | Observable | B | Optional Wave B; natural paths only — not forced |
| **Recovery semantics** | 12 | ❌ | No (Qualification) | C | MB2-Q6 — not before Runtime |
| **Qualification MB2-Q*** | 13 | ❌ | No (Qualification) | C | Reference Implementation gates |
| **Layer invariants** | 3 | ✅ | Yes | A | INV-R-05/06 — Wave A; INV-R-12 Integration B |
| **Non-goals (boundary)** | 2 | ✅ | Yes | A | NG-2 observed |

### Integration evidence (Architect Wave B review)

| Cross-cutting area | Status | Evidence |
|--------------------|--------|----------|
| Integration Constraints | ✅ | EWO-004, EWO-007; INV-R-03 merge_order |
| Explorer → Explain Chain | ✅ | Integration B; progressive header/definition API |

---

## Wave A — union(EWO.covers) [retroactive]

Wave A EWOs predate the `covers` field. Retroactive attribution:

| EWO | covers (retroactive) |
|-----|----------------------|
| PX3-EWO-001 | §4.1 Program Graph; INV-R-05; class A |
| PX3-EWO-002 | §4.1 (list API); INV-R-06; class A |
| PX3-EWO-003 | §4.1; INV-R-06; class A |
| PX3-EWO-004 | §4.1 merge_order INV-R-03; §10 observable; class A/B |

Wave B+ proposals **must** include explicit `covers:` yaml (max 3 elements).

---

## Wave B — union(EWO.covers)

| EWO | covers | Status |
|-----|--------|--------|
| PX3-EWO-005 | §9; INV-R-11; MB2-Q5 | **PASS** — `.asep/reports/PX3-EWO-005-projection-conformance.md` |
| PX3-EWO-006 | §10; INV-R-16 | **PASS** — `.asep/reports/PX3-EWO-006-supervisor-interaction-observation.md` |
| PX3-EWO-007 | §9; INV-R-12 | **PASS** — `.asep/reports/PX3-INTEGRATION-B.md` |

**Wave B:** **COMPLETE** — `.asep/reports/PX3-CONFORMANCE-REVIEW-WAVE-B.md`

### Wave C (DISPATCH AUTHORIZED — EWO-008 first)

| EWO | covers (proposed) | Status |
|-----|-------------------|--------|
| PX3-EWO-008 | §4.2; INV-R-01 | **AUTHORIZED** — `.asep/reports/PX3-AUTHORIZATION-EWO-008-20260705.md` |
| PX3-EWO-009 | §5; INV-R-11 | **PENDING** (await EWO-008 PASS) |
| PX3-EWO-010 | §4.2; INV-R-12 | **PENDING** (await EWO-009 PASS) |

Backlog: `.asep/reports/PX3-WAVE-C-BACKLOG.md`  
Review: `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-C-BACKLOG-REVIEW.md`  
Dispatch: `.asep/reports/PX3-AUTHORIZATION-WAVE-C-20260705.md`

---

## Do not pursue 100% in PX-3

PX-3 gathers progressive evidence that the **Specification of Record** is precise enough
to guide product development without continuous normative change.

Class **C** and **No (Runtime)** rows transfer to **px-exec** + MB2-Q* — not forced product features.

---

## Confidence ladder

```text
Wave A     COMPLETE · 4 EWO · N=0
Wave B     COMPLETE · 3 EWO · Integration B PASS · N=0
Wave C     DISPATCH AUTHORIZED · EWO-008 first executable
Target     Assessment after Wave C
```

---

## References

- Architect decision: `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-B-FRAMEWORK.md`
- Conformance Review Wave A: `.asep/reports/PX3-CONFORMANCE-REVIEW-WAVE-A.md`
- Conformance Log: `.asep/reports/PX3-CONFORMANCE-LOG.md`
- EWO template: `.asep/templates/conformance-ewo-template.md`
- Wave B framework: `.asep/reports/PX3-WAVE-B-DESIGN-FRAMEWORK.md`
- Wave B backlog: `.asep/reports/PX3-WAVE-B-BACKLOG.md`
- SoR: `docs/superpowers/specs/mb2-engineering-runtime-spec.md`
