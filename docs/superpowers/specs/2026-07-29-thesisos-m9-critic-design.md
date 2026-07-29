# ThesisOS — M9 "Critic" Design Spec

- **Date:** 2026-07-29
- **Status:** **Proposed** — Architect freeze required before implementation (ADR-0001).
- **Scope:** Milestone **M9 Critic** — activate reserved `critic` route; `CriticCapability` reviews `draft` against `retrieved_context` for hallucination/redundancy; write frozen `GraphState.critique`; emit `CritiqueCompleted`; bounded writer→critic→revise loop with pass/fail gate; wire lifecycle path toward `approved` (ADR-0032). **NOT** outline (M8), citation styles (M7), or M10 QA phase.
- **Builds on:** M6 writer (`DraftResult`, `draft`/`citations`), M4 `retrieved_context`, `contracts/agents/critic.json`, `Critique` model in GraphState, event `CritiqueCompleted`.
- **New ADR (Proposed):** ADR-0056 (Critic Loop & Approval Gate).
- **Authors:** ThesisOS Builder Team

---

## 1. Vision

M9 is the **trust gate** before a chapter is considered approved:

```text
… → WRITE (M6) → CITE (M7) → OUTLINE (M8) → CRITIQUE (M9) → QA (M10)
```

The Critic checks that claims in `draft` are supported by `retrieved_context` and flags redundancy. A bounded revise loop can re-invoke the writer once (or N≤2) when critique fails. Pass may authorize `status=approved` via `ChapterService` (explicit service call — not silent DB from the node).

**Success criterion (one sentence):** a turn on the critic path produces `critique={issues, passed}` per contract, emits `CritiqueCompleted`, blocks approval when `passed=false`, and a failing critique can trigger at most **one** automatic revise (writer) before returning to the user — with no GraphState schema change and no M10 QA conflation.

---

## 2. Objective, scope & non-goals

### 2.1 In scope (M9 MUST ship)

| # | Deliverable |
|---|-------------|
| 1 | **`CriticCapability` + `critic` node** — `critique(brief) -> CritiqueResult`; errors `hallucination`, `redundancy` |
| 2 | **Activate `critic` route** — grounded: `memory_context → retriever → critic_node → END` (or critic after existing context if draft already grounded) |
| 3 | **Bounded revise loop** — when entered from writer flow or `route` policy: writer → critic → (if fail ∧ retries left) → writer → critic → END; **max automatic revises = 1** (N=1) unless freeze raises to 2 |
| 4 | **`CritiqueCompleted` event** — `{ agent_run_id, passed }` via outbox |
| 5 | **Approval gate** — `passed=true` enables explicit `ChapterService` transition `review → approved` (API/helper); never skip critic for `approved` when M9 policy flag on |
| 6 | **Tests** — unsupported claims detected on fixtures; redundancy fixture; `passed` gating; loop bound |
| 7 | **Promotion** — `docs/m9-critic-promotion.md`, tag `m9-complete` |

### 2.2 Non-goals

| Forbidden in M9 | Deferred to |
|-----------------|-------------|
| Independent QA phase / `agent_steps.phase='qa'` as product gate | M10 |
| Outline tree / `ChapterCreated` | M8 |
| Citation style engine | M7 |
| Unlimited revise loops / M12 multi-agent re-entry | M12 |
| New GraphState fields | Frozen — use existing `critique` |
| Auto-`published` | M8 publish remains explicit/user |

```yaml
qa_phase: false
outline_ops: false
unlimited_revise: false
graphstate_change: false
```

---

## 3. Architecture

### 3.1 Topology

**A. Standalone critic route (required):**

```text
route=critic ──► memory_context → retriever_node → critic_node → END
```

**B. Bounded writer revise loop (required):**

Implemented as conditional edges **within** an M9 execution subgraph (not M12 supervisor re-entry):

```text
route=writer ──► … → writer_node → critic_node → [critique.passed?]
                      ├─ true  → END
                      └─ false ∧ revise_count < 1 → writer_node → critic_node → END
                      └─ false ∧ revise_count ≥ 1 → END (return critique to user)
```

`revise_count` lives in **RunContext / node config**, not GraphState (ADR-0014).

Exact wiring at freeze must preserve C6 for `conversation` / `grounded_chat`. Prefer: only the `writer` route gains the critic tail; `critic` route remains review-only (no writer).

### 3.2 Capability port (ADR-0056)

```text
CriticCapability:  async critique(brief: CriticBrief) -> CritiqueResult

CriticBrief:  draft, retrieved_context, citations?, messages?
CritiqueResult:
  critique: Critique   # issues: list[str], passed: bool  (frozen GraphState model)
  error_kind: hallucination | redundancy | None
```

- Node maps to `{critique, errors}` only.
- Pure: no DB/ChapterService imports inside capability.

### 3.3 Pass / fail semantics

- `passed=true` iff no blocking hallucination issues (redundancy may be warning-only or blocking — **default: redundancy blocking** for Wave 1; Architect may soften at freeze).
- Unsupported factual claims (no support in retrieved chunks) → `hallucination` error + `passed=false`.
- Event `CritiqueCompleted` always emitted at end of critic node (pass or fail).

### 3.4 Approval wiring (**LOCKED**)

- When user/API requests `status=approved` and project policy `require_critic_pass=true` (default true after M9): require a recorded passing critique for the chapter's current `version`.
- **Receipt storage (LOCKED):** write `{ critic_passed, agent_run_id, at }` into the head `chapter_versions.metadata` on the version that was critiqued (no new table in M9).
- Critic node does not UPDATE chapters; `ChapterService.update_metadata(status="approved")` remains sole writer and checks the receipt.

---

## 4. Internal milestones

| Sub | Name | Output |
|-----|------|--------|
| **M9.0** | Spec + ADR-0056 Accepted | freeze + Critic sign-off |
| **M9.1** | Critic capability + node | unit + fixture evals |
| **M9.2** | `critic` route + Event Bus | topology tests |
| **M9.3** | Bounded revise loop on writer route | loop bound tests |
| **M9.4** | Approval gate + `CritiqueCompleted` | API + event tests |
| **M9.5** | Qualification + promotion | tag `m9-complete` |

---

## 5. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Latency (writer+critic+revise) | Cap revises at 1; stream tokens; smoke benchmark `B_critique` |
| False positive hallucinations | Fixture suite + allowlist quotes from retrieved_context |
| Conflating Critic with M10 QA | Spec boundary: Critic = groundedness/redundancy; QA = process/phase audit |
| GraphState temptation (`revise_count`) | RunContext only |
| Auto-approve chapters | Forbidden; explicit ChapterService transition |

---

## 6. Critic checklist (pre-implementation)

- [ ] Uses existing `Critique` model only
- [ ] Max automatic revises ≤ 1 (or freeze-approved 2)
- [ ] `CritiqueCompleted` payload matches events.json
- [ ] No M10 `qa` phase implementation
- [ ] Chapter approval not written from graph node
- [ ] Existing non-writer routes unchanged

---

## 7. References

- `contracts/agents/critic.json` · `contracts/events/events.json`
- ADR-0027, ADR-0031, ADR-0032, Proposed ADR-0056
- `backend/app/schemas/graph_state.py` (`Critique`)
- `docs/m9-critic-promotion.md`
- M6 Writing Workspace design spec
