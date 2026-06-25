# DR-001 — Constitutional Design Review

- **ID:** DR-001
- **Date:** 2026-06-25
- **Type:** Design review of the **platform constitution** (not code review)
- **Scope:** L0 `engineering-meta-model.md`, L1 `invariant-model.md`, L2 `global-state-machine.md`, L3 `runtime-model.md`, ADR-0026, ADR-0028, ADR-0025, ADR-0010, ADR-0023
- **Reviewers:** Architect (requestor), Platform review (this document)
- **Verdict:** **APPROVED** (Conditional Pass confirmed by Architect 2026-06-25). Findings M02–M04 addressed via L2.1 micro-patch + Behavioral Semantics (ADR-0029).

---

## Executive summary

The platform constitution (L0–L3) represents a genuine architectural maturity shift: **agents are execution workers**, not the centre of the model. The centre is meta-model → invariants → state transitions → cycle → traceability. This matches the project's stated evolution from "Agent OS" to ASEP.

The constitution is **semantically sufficient** for Era II Platform Track work. It is **mostly minimal**, **largely closed**, and **coherent with documented exceptions**. Fourteen findings are recorded (0 critical blockers, 4 major, 10 minor). None require reopening L0 or L1. Three optional L2 clarifications are recommended before MB2 rebase.

**Recommended pipeline (accepted):**

```text
GSM (L2 frozen)
  → DR-001 (this document)
  → Engineering Traceability Matrix
  → Rebase MB2 (total traceability)
  → Architect sign-off
  → Implementation (L4)
```

---

## 1. Semantic completeness

**Question:** Does a fundamental concept missing from L0 prevent the system from making sense?

| Candidate concept | Verdict | Disposition |
|-------------------|---------|-------------|
| **Capability** | Not missing | Delivered capability = `Milestone` outcome + `Artifact` set. Adding a separate L0 object would duplicate Milestone. |
| **Constraint** | Not missing | Split correctly: **Invariant** (law, L1) + **Policy** (tunable, L5). Merging them was the pre-ADR-0028 error. |
| **Contract** | Out of scope (correct) | Product contracts (`openapi.yaml`, `agents/*.json`) belong to Product plane. Platform references them as **Artifact** type `ART_FROZEN`, not as L0 entity. |
| **Transaction** | Pattern, not object | Atomic commit = `StateWriter` + Class B invariant pass (INV-B8). GSM **transitions** are the transaction boundaries. Document in Traceability Matrix as mechanism, not L0. |
| **Projection** | Pattern, not object | CLI commands, YAML `status` mapping (ADR-0025 §2) are **read models** of GSM state — not authoritative. L2 §11 documents this. Recommend naming "Projection" explicitly in Traceability Matrix glossary. |
| **Command** | Pattern, not object | GSM **Trigger** column (= command intent). No separate L0 object needed. |
| **Aggregate** | Implicit | **Epic** is the workflow aggregate root (contains Wave → Task). **Goal** is the project aggregate root (contains Milestone references). No DDD aggregate object required. |

**Conclusion:** No new L0 entity is required. Three **meta-patterns** (Transaction, Projection, Command/Trigger) should appear in the Traceability Matrix glossary — not in L0.

**Minor finding DR-001-M01:** L0 does not name **Projection** or **Transition** as patterns. Traceability Matrix §0 glossary closes this without L0 amendment.

---

## 2. Minimality audit

For each L0 object: *If removed, does the system still make sense?*

| Object | Removable? | Rationale |
|--------|------------|-----------|
| **Goal** | ⚠️ Optional at small scale | Short epics could run without `/goal`. But strategic intent (Era II multi-track) requires it. **Keep.** |
| **Milestone** | No | Boundary object; Product + Platform tracks converge here. |
| **Epic** | No | `STATE.yaml` epic is the workflow container. |
| **Wave** | No | Parallelism + isolation (MB1 §8.5–8.7) requires wave barrier. |
| **Task** | No | Atomic schedulable unit (ADR-0025). |
| **Artifact** | No | Freeze act (INV-B1) requires producible output entity. |
| **Lock** | ⚠️ Could merge into Task | Separate entity enables INV-B3/B4/B5 without overloading Task. **Keep.** |
| **Event** | No | L4 event bus requires typed fact entity (emission-only). |
| **Policy** | No | Tunable decisions must not live in invariants (L1 §1). |
| **Invariant** | No | L1 catalog anchor; not stateful but constitutionally required. |
| **Snapshot** | No | Observe phase (L3 §3.1) requires derived read model entity. |
| **Worker** | No | Execution plane actor; INV-B9 boundary requires explicit role. |

**Conclusion:** No L0 object should be removed. **Goal** is the only object that is *operationally optional* for tiny epics — retain for governance completeness.

**Minor finding DR-001-m02:** Worker **engagement overlay** (L2 §3.9) is not an L0 object — it is an L2 composition over Worker + Task. Acceptable; document in Traceability Matrix.

---

## 3. Closure audit

For every L0 entity: states → transitions → events → invariants → owner → lifecycle?

| Entity | States | Trans | Events | Inv | Owner | Lifecycle | Status |
|--------|--------|-------|--------|-----|-------|-----------|--------|
| Goal | ✅ | G-01–05 | ✅ | ⚠️ partial | ✅ | ✅ | **Major DR-001-M02** |
| Milestone | ✅ | M-01–04 | ✅ | ✅ | ✅ | ✅ | OK |
| Epic | ✅ | E-01–03 | ✅ | ⚠️ E-01 | ✅ | ✅ | Minor |
| Wave | ✅ | W-01–03 | ✅ | ✅ | ✅ | ✅ | OK |
| Task | ✅ | T-01–12 | ✅ | ✅ | ✅ | ✅ | OK |
| Artifact | ✅ | A-01–03 | ✅ | ✅ | ✅ | ✅ | OK |
| Lock | ✅ | L-01–02 | ✅ | ✅ | ✅ | ✅ | OK |
| Snapshot | ✅ | S-01–03 | ⚠️ S-03 | ✅ | ✅ | ✅ | Minor |
| Worker | overlay K-* | ✅ | ✅ | ✅ | ✅ | ✅ | OK (overlay) |
| Event | emission-only | — | — | — | publisher | — | OK by design |
| Policy | per-cycle | C-03–04 | ✅ | orthogonal | Policy Engine | eval only | OK by design |
| Invariant | static | all guards | `InvariantViolation` | self | Invariant layer | — | OK by design |

### Closure gaps (detailed)

**DR-001-M02 (Major) — Goal transitions lack invariant coverage**

| Transition | Has invariant? |
|------------|----------------|
| G-01, G-03, G-04, G-05 | None declared |
| G-02 | INV-B2 |

**Recommendation:** Add governance preconditions to L2 §5.1 (L2 patch, not L0/L1):
- G-01: require ≥1 linked Milestone in `MS_PLANNED` or `MS_SPEC_FROZEN`
- G-03: require no Task in `TASK_RUNNING`/`TASK_CLAIMED` (or explicit force flag — policy, not invariant)
- G-05: require all Tasks terminal or cancelled

**DR-001-M03 (Major) — No explicit Task birth transition**

`TASK_CREATED` exists as state but no transition `* → TASK_CREATED`. Packets appear when Build Control Plane adds them to STATE.yaml.

**Recommendation:** Add **T-00** `create_packet`: `(none) → TASK_CREATED`, owner Build Control Plane, event `TaskCreated`. Or document packet creation as **out-of-band governance act** exempt from runtime FSM (preferred minimal fix: L2 §3.5 note + Traceability row).

**DR-001-M04 (Major) — Milestone ↔ Epic linkage not in transition table**

L0 §4: `Milestone ──decomposed into──▶ Epic`. GSM has parallel FSMs (M-* and E-*) with no coupling transition.

**Recommendation:** Document as **intentional orthogonality**: Product milestones (M4) and Platform epics (mb1-phase2) evolve on different tracks (ADR-0026 §3). Add Traceability rows; optional L2 **coupling guard** on E-01: Epic may open only if governing Milestone ≥ `MS_SPEC_FROZEN`.

**DR-001-M05 (Major) — Policy entity has no lifecycle**

By design: Policy is config, not stateful entity. Policy **evaluation** is cycle-scoped (C-03, C-04).

**Recommendation:** Accept. Document in Traceability Matrix under "Policy (evaluation pattern)" — not a closure gap.

**Minor gaps:**
- **DR-001-m03:** E-01 has no invariant → add INV-B8 on STATE write
- **DR-001-m04:** S-03 emits no event → accept (ephemeral discard) or add `SnapshotDiscarded`
- **DR-001-m05:** G-01–G-05 not persisted in engine today → projection gap (already in L2 §12)
- **DR-001-m06:** C-07 owner "Worker → Runtime" — two actors; split into K-03 then T-04 trigger (ownership ambiguity)
- **DR-001-m07:** `TASK_FAILED` vs `TASK_DEBUGGING` YAML both `blocked` — projection debt (L2 §12)

---

## 4. Coherence — hierarchy and exceptions

**Canonical chain (L0 §4):**

```text
Goal → Milestone → Epic → Wave → Task
```

| Relation | Unidirectional? | Exception / debt |
|----------|-----------------|------------------|
| Goal → Milestone | Intended | No formal FK in STATE.yaml; manual in `knowledge/` |
| Milestone → Epic | Intended | **Orthogonal tracks** — M-series vs MB-series epics (ADR-0026) |
| Epic → Wave | Yes | Wave is integer on Task, not nested object in YAML |
| Wave → Task | Yes | `packet.wave` field |
| Task → Artifact | Yes | `owned_files`, worker output |
| Task → Lock | Yes | `file_locks` |
| Task → Event | Yes | emission on transition |

**Exceptions are real but governed:**

1. **Dual-track orthogonality** — Product M5 and Platform MB2 run in parallel under one Goal. Not a hierarchy violation; a **track** dimension missing from L0 (present in ADR-0026 §3 as Product/Platform Track, not as L0 object). **Accept** — Track is governance metadata, not runtime entity.

2. **Wave as scalar vs entity** — Wave FSM states (W-*) are logical; persisted as `STATE.wave` integer. Coherent projection.

3. **Milestone governs freeze; Epic governs execution** — Different lifecycles by design (governance vs workflow).

**Minor finding DR-001-m08:** L0 relation "Epic serves one or more Milestones" is not enforceable in GSM today. Traceability + optional E-01 guard closes this.

---

## 5. Agents as executors (architectural observation)

**Finding (positive):** The constitution correctly demotes LLM agents from architectural centre to **Execution workers** (L0 §3, L3 §6). Workers:
- Execute Tasks (K-02, K-03)
- Produce Artifacts (A-01, A-02)
- **Never** authoritatively mutate Workflow state (INV-B9)

The Product plane retains LangGraph agents (M5+) under its own model — correctly out of L0 scope.

**Implication for traceability:** Every `builder_engine/` module must trace to GSM transitions, not to "agent behaviour". Agent prompts are **worker configuration**, not platform semantics.

---

## 6. Findings summary

| ID | Severity | Summary | Action |
|----|----------|---------|--------|
| DR-001-M01 | Minor | Projection/Command patterns unnamed in L0 | Traceability glossary |
| DR-001-M02 | **Major** | Goal transitions lack invariant coverage | L2 §5.1 patch (proposed) |
| DR-001-M03 | **Major** | Task birth (`TASK_CREATED`) implicit | Document T-00 or governance exemption |
| DR-001-M04 | **Major** | Milestone–Epic coupling not in GSM | Traceability + optional E-01 guard |
| DR-001-M05 | **Major** | Policy has no entity lifecycle | Accept by design |
| DR-001-m02 | Minor | Worker engagement is L2 overlay | Traceability note |
| DR-001-m03 | Minor | E-01 no invariant | Add INV-B8 reference |
| DR-001-m04 | Minor | S-03 no event | Accept or add event |
| DR-001-m05 | Minor | Goal states not in engine | Gap analysis §12 already |
| DR-001-m06 | Minor | C-07 dual owner | Clarify in L2 patch |
| DR-001-m07 | Minor | FAILED/DEBUGGING YAML collapse | Phase 3 YAML plan |
| DR-001-m08 | Minor | Epic–Milestone N:M not enforced | Traceability + optional guard |

**Blockers for implementation:** 0  
**Blockers for MB2 rebase:** Close M02–M04 via Traceability Matrix + optional L2 micro-patch + Architect sign-off

---

## 7. Recommendations (ordered)

1. **Accept DR-001** as conditional pass (this document).
2. **Publish** `docs/platform/engineering-traceability-matrix.md` (companion) — every L4 row must fill all columns.
3. **Optional L2 micro-patch** (Architect approval): G-01/03/05 guards, T-00 or birth exemption note, C-07 owner split, E-01 INV-B8. **Do not modify L0, L1, L3.**
4. **Rebase MB2 spec** using Traceability Matrix — each deliverable answers "why this line exists" up to Vision.
5. **Architect sign-off** on rebased MB2 + closed DR actions.
6. **Then** L4 implementation per `plans/l2-global-state-machine-plan.md`.

**Explicitly deferred:** Production code, MB2 branch work, M5 implementation.

---

## 8. Review checklist (completion criteria)

| Criterion | Result |
|-----------|--------|
| Semantic completeness verified | ✅ §1 |
| Minimality verified | ✅ §2 — no L0 removals |
| Closure verified | ⚠️ §3 — 4 major gaps documented with actions |
| Coherence verified | ✅ §4 — exceptions governed |
| Agents demoted to executors | ✅ §5 |
| Traceability requirement defined | ✅ §7 → companion matrix |
| Implementation blocked until sign-off | ✅ |

---

## 9. Sign-off record

| Role | DR-001 | ETM v1.1 | L2.1 patch | Behavioral Semantics | MB2 rebase | L4 code |
|------|--------|----------|------------|---------------------|------------|---------|
| Architect | ✅ Approved 2026-06-25 | ✅ Approved | ✅ Approved | ✅ Approved (ADR-0029) | ✅ Authorized | ⏸️ After rebase + sign-off |
| Platform review | Closed | Closed | Applied | Frozen | Next step | Blocked |

**DR-001 status:** **Approved.** MB2 rebase is the next authorized platform action.

---

## 10. References

- L0 `engineering-meta-model.md` · L1 `invariant-model.md` · L2 `global-state-machine.md` · L3 `runtime-model.md`
- ADR-0026, ADR-0028, ADR-0025, ADR-0010, ADR-0023
- `docs/platform/engineering-traceability-matrix.md` (companion)
- `knowledge/project/vision.md`
- `plans/l2-global-state-machine-plan.md`
