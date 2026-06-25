# ASEP — Engineering Meta Model (L0)

- **Status:** Frozen (Architect 2026-06-25)
- **Layer:** L0 — **semantics**. The canonical objects of the platform and how they relate. Sits *above* the dynamics (`runtime-model.md`, L3) and *above* the states (ADR-0025 packet FSM, L2).
- **Scope:** **Platform plane only** (Build Control Plane + Engineering Runtime + Execution workers). The Product plane keeps its own domain model (GraphState, documents, memory, chapters) and is **out of scope** here — except `Milestone`, the single shared **boundary object**.
- **Authority:** ADR-0028. Refines the state vocabulary of ADR-0026 §6 into an object model.
- **Derivation:** This document **consolidates** concepts already present in `plans/builder/STATE.yaml`, `decisions/ADR-0025`, `builder_engine/validate.py`, and `docs/platform/runtime-model.md`. It does **not** introduce new runtime behaviour.

---

## 1. Why this layer exists

Era I has a dynamics model (`runtime-model.md`, the 10-phase cycle) and a partial state model (ADR-0025, packet-level FSM). It has **no single declaration of the objects those models operate on**. As components, ADRs, and specs multiply, the real risk is not wrong code — it is **concept drift**: two parts of the platform evolving slightly different notions of "task", "milestone", or "frozen".

L0 fixes the vocabulary as *objects with identity, states, owners, and relations*. Every L2+ artifact (state machine, event bus, policy engine, planner) is a **concretization of this model**, not a local decision.

---

## 2. Scope guard (honours Product/Platform separation)

| Plane | Modelled here? | Its own model |
|-------|----------------|---------------|
| Build Control Plane | ✅ | this document |
| Engineering Runtime | ✅ | this document + `runtime-model.md` |
| Execution workers | ✅ (as actors) | this document |
| Product plane | ❌ | `knowledge/contracts/graphstate.md`, M-series specs |

**`Milestone` is the only boundary object.** Both planes reference it: the Product Track *delivers* milestones; the Platform Track *governs and promotes* them. It is defined **once**, here, and owned by the Build Control Plane. Conflating any other product concept into this model would re-couple the two planes that ADR-0023/ADR-0026 deliberately separated.

---

## 3. Canonical objects

| Object | Definition | Identity | State home (ADR-0026 §6) | Mutated by |
|--------|------------|----------|--------------------------|------------|
| **Goal** | A strategic objective driving a chain of work (e.g. `/goal`). | name + chain | Project state | Build Control Plane (human/Architect) |
| **Milestone** *(boundary)* | A promotable unit of capability (`m{n}` / `mb{n}`). | `m4`, `mb2` | Project state | Build Control Plane (governance) |
| **Epic** | A bounded body of platform work realising part of a milestone. | `epic` in STATE | Workflow state | Build Control Plane |
| **Wave** | A synchronisation barrier; tasks in a wave run in parallel under isolation. | integer `wave` | Workflow state | Engineering Runtime (StateWriter) |
| **Task** *(Packet)* | The atomic unit of schedulable work; one worker, one outcome. | packet id `P-…` | Workflow membership + **Packet execution state** (ADR-0025) | Runtime (transitions) / Worker (output) |
| **Artifact** | A produced output: spec, ADR, code, doc, gate. May be **frozen**. | path | Filesystem / git | Worker (creates) · governance (freezes) |
| **Lock** | An exclusive claim on a file path by a task. | path → owner | Workflow state (`file_locks`) | Runtime (Schedule / Update State) |
| **Event** | An append-only, typed fact about an outcome. | type + ts | Build event bus (Era II, L4) | Runtime / Control Plane (publish) |
| **Policy** | A **tunable** decision rule (priority, timeout, concurrency, eligibility). | id | Build Control Plane config | Build Control Plane |
| **Invariant** | A **non-negotiable law** over object states/transitions (see L1). | `INV-…` | L1 invariant model | Never relaxed; only added via ADR |
| **Snapshot** *(ObservedSnapshot)* | A consistent derived read model for **one** cycle; immutable. | cycle id | Ephemeral (Observe phase) | Engineering Runtime (Observe) |
| **Worker** *(Builder)* | A non-deterministic executor (LLM agent, human, future autom1) that performs a Task. | `agent_type` | Execution plane | self (produces Artifacts) |

> `Snapshot`, `Event`, and `Policy` are the three objects that do **not** exist as first-class code in Era I — they are the L4–L5 implementation targets. Everything else already exists implicitly.

---

## 4. Relations

```text
Goal ──realised by──▶ Milestone ──decomposed into──▶ Epic
                          │                            │
                    governs/promotes              contains
                          │                            ▼
                          │                          Wave ──contains──▶ Task
                          │                                               │
                          │                                produces ──────┼────▶ Artifact
                          │                                holds ─────────┼────▶ Lock
                          │                                transitions ───┼────▶ Event
                          ▼                                               ▲
                       Policy ──evaluated over──▶ Snapshot ──derived from State──┘
                                                     ▲
                       Invariant ──constrains every transition above──┘

Worker ──executes──▶ Task        StateWriter ──only writer of──▶ Workflow state
```

Relation rules (normative):

- A **Task** belongs to exactly one **Wave**, which belongs to exactly one **Epic**, which serves one or more **Milestones**.
- A **Worker** *executes* a Task but **never** authoritatively mutates Workflow state — only the runtime's StateWriter does.
- A **Snapshot** is *derived from* Project + Workflow state + git + CI; it is never the source of truth.
- **Policies** are evaluated *against* a Snapshot to yield a decision; **Invariants** *gate* every transition regardless of policy (L1).
- An **Artifact** marked **frozen** is immutable except by an explicit governance act (Architect + ADR).

---

## 5. Object lifecycles

Two lifecycles are constitutional. Detailed transition guards live in L1; the full **Global State Machine** (L2) extends these.

**Task (Packet)** — owned by ADR-0025, unchanged:

```text
CREATED → READY → CLAIMED → RUNNING → VALIDATING → MERGED → DONE
                               ↘ FAILED → DEBUGGING → READY
```

**Milestone** — boundary object, owned by governance, derived from the freeze-first pipeline + promotion gates (ADR-0010, ADR-0026 §5):

```text
PLANNED → SPEC_FROZEN → IMPLEMENTING → VALIDATED → PROMOTED
```

`STATE.yaml` packet `status` projects the Task machine (ADR-0026 §6): `ready≈READY`, `in_progress≈CLAIMED|RUNNING`, `done≈DONE`, `blocked≈FAILED|DEBUGGING`, `cancelled` terminal.

---

## 6. Component responsibilities

| Component | Owns (mutates) | Must not |
|-----------|----------------|----------|
| **Build Control Plane** | Goal, Milestone status, Policy, freeze acts | Execute code; bypass invariants |
| **Engineering Runtime** | Snapshot, Task transitions, Lock, Event publish, **invariant enforcement** | Write product code (ADR-0023); skip a transition guard |
| **Execution workers** | Artifact contents (in worktrees) | Mutate Workflow state; self-promote a Task to DONE without evidence |
| **StateWriter** (`state_io`) | Authoritative Workflow state (atomic) | Partial / non-atomic writes |
| **Invariant layer** (L1) | — (read-only veto) | Be optional; be a warning |

---

## 7. Derivation sources (grounding)

| Object/relation | Already present as |
|-----------------|--------------------|
| Epic, Wave, Task, Lock, blockers | `plans/builder/STATE.yaml` |
| Task FSM | `decisions/ADR-0025` |
| Invariants (errors) vs policy hints (warnings) | `builder_engine/validate.py` (`ValidationResult.errors` vs `.warnings`) |
| 10-phase dynamics, Snapshot, Event, Policy roles | `docs/platform/runtime-model.md` |
| State layering | `decisions/ADR-0026` §6 |

---

## 8. Non-goals

| Forbidden here | Why |
|----------------|-----|
| Product domain objects (chapters, documents, GraphState) | Product plane has its own model |
| New runtime behaviour or code | L0 is semantics only |
| Full Global State Machine transition table | That is L2 (extends ADR-0025) |
| Renaming objects in code in this commit | Mechanical migration, tracked separately |

---

## 9. Freeze record

- [x] Object catalog with identity, state home, owner
- [x] Relations (normative rules)
- [x] Task + Milestone lifecycles declared
- [x] Component responsibilities
- [x] Platform-only scope; `Milestone` as sole boundary object
- [x] Derived from existing artifacts (no invented behaviour)

**Implementation authorized:** L2 (Global State Machine) and L4+ (event bus, policy engine, planner) concretize this model. Each must trace its objects to §3.

---

## 10. References

- ADR-0028 Engineering Meta Model (this layer's decision)
- ADR-0026 §6 State vocabulary · ADR-0025 Packet FSM · ADR-0023 Sidecar boundary · ADR-0010 Promotion gates
- `docs/platform/invariant-model.md` (L1) · `docs/platform/runtime-model.md` (L3)
- `plans/builder/STATE.yaml` · `builder_engine/validate.py`
