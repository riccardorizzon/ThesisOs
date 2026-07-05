# PX-3 Wave C — Backlog Definition

> **Authority:** Architect  
> **Date:** 2026-07-05  
> **Status:** **APPROVED — DISPATCH AUTHORIZED (EWO-008 only)**  
> **Review:** `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-C-BACKLOG-REVIEW.md`  
> **Dispatch:** `.asep/reports/PX3-AUTHORIZATION-WAVE-C-20260705.md`  
> **Session:** Architect Wave C design (coverage-first)  
> **Program:** `.asep/programs/thesisos-product-v2.yaml`  
> **Parallel:** `.asep/programs/px3-parallel.yaml` (Wave C entries pending authorization)  
> **Precondition:** Wave B PASS — `.asep/reports/PX3-ARCHITECT-REVIEW-WAVE-B-20260705.md`

---

## Wave objective (SoR-first)

**Wave C — Execution & Job State Observation**

| Tier | Target | PX-3 exercisability |
|------|--------|---------------------|
| **Primary** | §4.2 Execution Graph | Observable |
| **Secondary** | §5 Job FSM / aggregate roll-up (§5.3) | Observable |
| **Optional** | §11 Failure semantics | Observable — natural paths only; never forced |

**Verifiable SoR delta vs Wave B:** §4.2 Execution Graph → evidenced (Observable); §5 Job FSM → evidenced (Observable).

Product vehicles (secondary): read-only **Program Trace** surface (008); **Knowledge Graph** §10 (009). Product work is a *means* to attach observation evidence — not the wave name.

---

## 1. Wave C Coverage Matrix

Legend: **Status** — ✅ evidenced · ⏳ partial · ❌ not evidenced · ⛔ deferred (Class C)  
**Target** — row state after Wave C PASS (simulated `Coverage += union(EWO.covers)`)

| SoR area | § | Pre Wave C | Target post Wave C | PX-3 exercisability | Class | Wave C action |
|----------|---|------------|----------------------|---------------------|-------|---------------|
| Program Graph | 4.1 | ✅ | ✅ (unchanged) | Yes | A | — |
| **Execution Graph** | **4.2** | **❌** | **✅ Observable** | Observable | B | **EWO-008 primary** |
| Job / Checkpoint | 4.3–4.4 | ❌ | ⛔ deferred | No (Runtime) | C | px-exec |
| Projection document | 4.5, §9 | ✅ | ✅ (unchanged) | Yes | A | — |
| **Job FSM** | **5** | **❌** | **✅ Observable** | Observable | B | **EWO-009 primary** |
| Event model | 6 | ❌ | ⛔ deferred | No (Runtime) | C | px-exec |
| Rule model | 7 | ❌ | ⛔ **excluded** | No (Runtime) | C | px-exec — no new evidence |
| Plugin contracts | 8 | ❌ | ⛔ **excluded** | No (Runtime) | C | px-exec — no new evidence |
| Projection model | 9 | ✅ | ✅ (unchanged) | Yes | A | — |
| Supervisor interaction | 10 | ✅ | ✅ (unchanged) | Observable | B | — |
| Failure semantics | 11 | ❌ | ⏳ optional | Observable | B | Integration C — natural only |
| Recovery semantics | 12 | ❌ | ⛔ **excluded** | No (Qualification) | C | MB2-Q6 — no new evidence |
| Qualification MB2-Q* | 13 | ❌ | ⛔ deferred | No (Qualification) | C | px-exec + MB2-Q |
| Layer invariants | 3 | ✅ | ✅ (unchanged) | Yes | A | — |
| Non-goals (boundary) | 2 | ✅ | ✅ (unchanged) | Yes | A | — |

### Simulated coverage delta

```text
Pre Wave C:  7 / 15 rows evidenced (✅ or ⏳ with Wave evidence)
Post Wave C: 9 / 15 rows evidenced (+§4.2, +§5)
Optional:    10 / 15 if §11 failure observed naturally during Integration C
Class C:     6 rows remain deferred — not Wave C scope
```

### Cross-cutting (Integration C)

| Area | Pre Wave C | Target |
|------|------------|--------|
| Integration Constraints | ✅ | ✅ re-verified |
| Explorer → Explain Chain | ✅ | ✅ + Graph entry |
| INV-R-12 (no ready-set in consumer) | ✅ | ✅ re-verified |

---

## 2. Candidate EWOs

### Wave C DAG

```text
PX3-EWO-008  Execution Graph Observation (§4.2)
      │
      ▼
PX3-EWO-009  Job FSM Observation (§5)
      │
      ▼
PX3-EWO-010  Conformance Integration C
```

| EWO | Title | Primary (SoR) | Secondary (Product) | Class |
|-----|-------|---------------|---------------------|-------|
| **PX3-EWO-008** | Execution Graph Observation | §4.2 — observe Program→Execution structure; **do not derive ReadySet** | Read-only Program Trace API + UI (wave DAG, merge_order, depends_on) | B |
| **PX3-EWO-009** | Job FSM Observation | §5 — vocabulary alignment: projection aggregate states ↔ Job FSM subset | Knowledge Graph §10 (lifecycle badges, bounded graph) | B |
| **PX3-EWO-010** | Conformance Integration C | §4.2 + §5 union evidence; INV-R-12 re-check | Cross-surface wiring; `make ci`; coverage matrix update | A/B |

**First executable EWO (when authorized):** `PX3-EWO-008`

---

### PX3-EWO-008 — Execution Graph Observation

```yaml
covers:
  sor_sections:
    - "§4.2 Execution Graph"
  invariants:
    - INV-R-01
  mb2_gates: []
  px3_exercisability: Observable
  class: B
```

**Observable evidence contract (what PASS means):**

| Criterion | Evidence artifact |
|-----------|-------------------|
| Program Graph entities visible read-only | API returns parsed `px3-parallel.yaml` waves, workorders, merge_order, depends_on — no mutation |
| ExecutionNode traceability | Every displayed node maps 1:1 to a Program Graph EWO/integration declaration (INV-R-01 audit table in report) |
| No ReadySet computation | Consumer reads projection + program yaml only; **does not** compute scheduling decisions (INV-R-12 boundary documented) |
| Derivation boundary documented | Report states: PX-3 observes structure; Runtime derivation (ReadySet, CriticalPath) deferred to px-exec / MB2-Q1 |

**Secondary product acceptance:**

- `GET /api/conformance/program-graph` (or equivalent read-only endpoint) returns wave DAG
- Program Trace panel renders wave nodes and dependency edges (developer/conformance surface — not end-user primary nav)
- Tests assert no ready-set fields exposed to consumers

**Explicitly NOT in scope:** `ExecutionGraphDerived` event emission, Dependency Engine, MB2-Q-001…003.

---

### PX3-EWO-009 — Job FSM Observation

```yaml
covers:
  sor_sections:
    - "§5 Job FSM"
  invariants:
    - INV-R-11
  mb2_gates: []
  px3_exercisability: Observable
  class: B
```

**Observable evidence contract:**

| Criterion | Evidence artifact |
|-----------|-------------------|
| Status vocabulary alignment | Report maps projection `waves.*.status` and `jobs.*.status` to §5.3 aggregate roll-up (`waiting\|ready\|running\|pass\|fail\|locked`) and Job FSM subset |
| Read-only consumer | Job status displayed from projection snapshot / API — never written by product (INV-R-11) |
| No illegal transition proof | Document: PX-3 displays states; transition legality is Runtime scope (ADR-0025) |
| §11 optional | If a job/wave shows `fail` naturally, report §11 observation — not an acceptance gate |

**Secondary product acceptance:**

- Knowledge Graph §10 per `px3-knowledge-experience-v2.md` (default 15 nodes, 100 hard limit, List fallback)
- Lifecycle badges on graph nodes reuse §4 product lifecycle — **separate** from Job FSM; report must distinguish the two vocabularies
- Mini-graph link from Explain Page `[ Grafo ]` quick nav

**Explicitly NOT in scope:** JobState enum enforcement, `TransitionError`, `JobClaimed` events, MB2-Q-004…006.

---

### PX3-EWO-010 — Conformance Integration C

```yaml
covers:
  sor_sections:
    - "§4.2 Execution Graph"
  invariants:
    - INV-R-12
  mb2_gates: []
  px3_exercisability: Yes
  class: A
```

**Deliverable:** `.asep/reports/PX3-INTEGRATION-C.md` — conformance verdict + coverage delta.

**Integration actions:**

1. Merge Wave C worktrees (008 → 009)
2. Wire Explorer / Explain → Knowledge Graph navigation
3. Re-run Wave A + B regression spot-checks
4. Update `.asep/reports/MB2-CONFORMANCE-COVERAGE.md` from `union(EWO.covers)`
5. Verify Wave C exit criteria (below)
6. Attach updated projection snapshot if §9 union changed
7. §11: document only if failure occurred naturally during integration — never inject artificial FAIL

---

## 3. Exit Criteria

Wave C is **PASS** only when **all** of:

1. **PX3-EWO-008**, **PX3-EWO-009**, **PX3-EWO-010** each report PASS  
2. **Conformance Integration C** (EWO-010) verdict PASS  
3. Conformance Log: **no N-class** entries attributable to Wave C  
4. `MB2-CONFORMANCE-COVERAGE.md`: **≥2 new** rows at **Observable** (✅) vs post–Wave B baseline — specifically **§4.2** and **§5**  
5. **No Runtime extension** — `builder_engine/` unchanged; no Event Bus, Scheduler, Plugin Registry, or Rule Engine code  
6. **No SoR or governance modification** — unless N-class forces stop (expected: 0)  
7. INV-R-12 boundary re-verified — no consumer computes ReadySet or scheduling decisions  

```text
Coverage_after := union(Wave C EWO.covers)
Requirement: |{§4.2, §5 newly ✅ Observable}| ≥ 2
Optional bonus: §11 → ⏳ if natural failure documented
```

**Post Wave C artifact:** `.asep/reports/MB2-CONFORMANCE-ASSESSMENT.md` (design authorized; authoring after Wave C PASS).

---

## 4. Integration C Scope

| Dimension | In scope | Out of scope |
|-----------|----------|--------------|
| **EWOs merged** | 008, 009 | — |
| **Merge order** | 008 → 009 (sequential) | Parallel sub-agents |
| **Cross-module links** | Explain `[ Grafo ]` → `/knowledge/graph`; Explorer concept → Graph focus; Program Trace reachable from conformance/dev context | New top-level nav (ADR-0036) |
| **Regression** | Wave A (Sources, Explorer); Wave B (Explain, projection API, supervisor WAIT); PX-2 cite flow; ContextBar untouched | PX-2 feature additions |
| **CI** | `make ci` green after merge | builder_engine MB2 tests |
| **Coverage** | Update live matrix; attach observation reports for §4.2, §5 | Class C row closure |
| **Projection** | Snapshot at gate time if union changed | Projection rebuild engine |
| **§11 Failure** | Report natural failures only | Forced FAIL injection |
| **Conformance Log** | I/S/A/N entries if any | SoR edits |

### Integration C verdict template

Follow `.asep/templates/integration-review-template.md` — same structure as Integration A/B.

---

## 5. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| **R-C1** | INV-R-12 violation — product computes ReadySet or "next executable" | Medium | High (N-class) | EWO-008 tests forbid ready-set fields; Program Trace is display-only; explicit boundary in report |
| **R-C2** | Vocabulary collision — PX-3 §4 lifecycle vs MB2 §5 Job FSM | Medium | Medium | EWO-009 report must contain explicit mapping table; badges labeled by domain |
| **R-C3** | Scope creep — Knowledge Graph pulls canvas/PX-5 features | Medium | Medium | Hard limits per product spec §10; List fallback at 100 nodes; no expansion beyond 1-hop default |
| **R-C4** | False conformance — claiming MB2-Q1 pass via observation | Low | High | `covers` excludes MB2-Q1; report states Observable ≠ Qualified |
| **R-C5** | Forced §11 failure paths for coverage | Low | Medium | Optional tier only; Integration C template forbids artificial FAIL |
| **R-C6** | Runtime pressure — implement yaml parser in `builder_engine/` | Low | High | Product-only parser in `backend/app/services/conformance/`; read governance yaml, not execute |
| **R-C7** | Wave C closes insufficient rows — assessment still shows 6 Class C gaps | Expected | Low | By design; assessment documents px-exec handoff; not a Wave C failure |
| **R-C8** | EWO oversized — §4.2 + §5 + §11 in one EWO | Medium | Medium | Three-EWO cap enforced; max 3 `covers` elements each |

---

## 6. Architect Recommendation

### Decision

```text
Wave C backlog design: APPROVED — Backlog Review PASS 2026-07-05
Wave C dispatch: AUTHORIZED — EWO-008 only (2026-07-05)
Wave C implementation: EWO-008 authorized; EWO-009/010 WITHHELD
```

### Rationale

1. **Coverage-first:** Wave C closes the only remaining **Class B** rows with clear Observable evidence paths (§4.2, §5). This maximizes MB2 coverage within PX-3 bounds without extending Runtime.

2. **Exclusions honored:** Rule Model (§7), Plugin Contracts (§8), and Recovery Model (§12) remain Class C — no new normative evidence justifies PX-3 pursuit. Job/Checkpoint (§4.3–4.4), Event model (§6), and Qualification (§13) defer to px-exec.

3. **Pattern continuity:** Three-EWO wave (2 observation + 1 integration) mirrors Wave B success (N=0, 0 SoR amendments). Observable primary objectives stay secondary-tier per taxonomy; Integration C carries class A verification of INV-R-12.

4. **Product value preserved:** Knowledge Graph §10 is the natural PX-3 product continuation and provides a legitimate secondary vehicle for Job FSM vocabulary display without conflating product lifecycle with Runtime JobState.

5. **Terminal conformance wave:** After Wave C PASS, produce `MB2-CONFORMANCE-ASSESSMENT.md`. Expected outcome: **9/15 rows evidenced**; **6 Class C rows explicitly deferred** to px-exec + MB2-Q*. This is sufficient to decide Runtime Reference Implementation authorization — not 100% matrix fill.

### Authorization gates (future — not this session)

| Gate | Status |
|------|--------|
| Wave C backlog design | ✅ |
| Backlog review | ✅ `.asep/reports/PX3-ARCHITECT-DECISION-20260705-WAVE-C-BACKLOG-REVIEW.md` |
| Program Graph registered | ✅ EWO 008–010 |
| `px3-parallel.yaml` wave_c_* | ✅ |
| `AUTHORIZE PX-3 Wave C` dispatch | ✅ `.asep/reports/PX3-AUTHORIZATION-WAVE-C-20260705.md` |
| First executable EWO | ✅ **PX3-EWO-008** |
| EWO-009 / EWO-010 | ⏳ WITHHELD — await prior PASS |
| Runtime Engineering | ❌ **NOT AUTHORIZED** |
| PX-4 | ❌ **NOT AUTHORIZED** |
| MB2 SoR revision | ❌ **NOT AUTHORIZED** (unless N-class) |

### Next steps (operator)

1. Architect backlog review of this document  
2. On PASS → register EWO 008–010 in program graph  
3. Explicit `AUTHORIZE PX-3 Wave C` (or wave-specific authorization)  
4. First executable: **PX3-EWO-008**  
5. After Wave C PASS → author `MB2-CONFORMANCE-ASSESSMENT.md`

---

## Explicit exclusions (Wave C)

| Exclusion | Reason |
|-----------|--------|
| Rule model (§7) | No (Runtime) — excluded unless new normative evidence |
| Plugin contracts (§8) | No (Runtime) — excluded unless new normative evidence |
| Recovery semantics (§12) | No (Qualification) — MB2-Q6 |
| Job / Checkpoint (§4.3–4.4) | No (Runtime) |
| Event model (§6) | No (Runtime) |
| MB2-Q1…Q4, Q6 gates | Qualification — not product-conformable |
| ReadySet / CriticalPath derivation | INV-R-12 — Runtime only |
| Forced §11 FAIL paths | Optional / natural only |
| `builder_engine/` changes | PX-3 product-only |
| SoR / governance edits | Frozen unless N-class |

---

## Authoritative sources

| Artifact | Role |
|----------|------|
| `docs/superpowers/specs/mb2-engineering-runtime-spec.md` | SoR §4.2, §5, §5.3, §11 (read-only) |
| `docs/product/specs/px3-knowledge-experience-v2.md` | Knowledge Graph §10 (product vehicle) |
| `.asep/templates/conformance-ewo-template.md` | EWO contract |
| `.asep/reports/MB2-CONFORMANCE-COVERAGE.md` | Live matrix |
| `.asep/reports/PX3-WAVE-B-BACKLOG.md` | Precedent structure |
| `.asep/programs/px3-parallel.yaml` | Program Graph observation source |

---

## Registration (pending authorization)

| Artifact | Path |
|----------|------|
| PX3-EWO-008 proposal | `.asep/proposals/PX3-EWO-008-execution-graph-observation.md` |
| PX3-EWO-009 proposal | `.asep/proposals/PX3-EWO-009-job-fsm-observation.md` |
| PX3-EWO-010 proposal | `.asep/proposals/PX3-EWO-010-conformance-integration-c.md` |
| Program entries | `thesisos-product-v2.yaml` workorder_backlog |
| Parallel waves | `px3-parallel.yaml` wave_c_* |

---

## WO-TRACE

```text
Wave B Architect Review PASS
  → Wave C design session (this document)
  → Backlog review (future)
  → AUTHORIZE Wave C (future)
  → PX3-EWO-008 (first)
  → … → Integration C → MB2-CONFORMANCE-ASSESSMENT.md
```

**STOP — backlog design complete. No implementation. No dispatch.**
