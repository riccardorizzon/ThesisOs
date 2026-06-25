# MB1 — Build Workflow Engine — Design Spec

- **Date:** 2026-06-25
- **Status:** Frozen (Architect-approved 2026-06-25). **Terminology supersession (2026-06-25):** legacy "Build-time Agent OS / BuilderOS" → **ASEP** with **Build Control Plane** + **Engineering Runtime** (ADR-0026). Implementation gated behind §13 promotion criteria.
- **Scope:** The **Build Control Plane + Engineering Runtime** side of ASEP — the Cursor-agent system that *builds* ThesisOS. Introduces a deterministic **Build Workflow Engine** (`builder_engine/`) that owns orchestration decisions currently described as prose in the `orchestrate-builders` skill. **Excludes** the ThesisOS runtime product (system A: `/chat`, `ConversationService`, LangGraph graph, M2 `MemoryService`, `tasks`/`agent_runs`/`agent_steps`). The runtime is never modified or called by the engine.
- **Authors:** Builder Architect session
- **Builds on:** `orchestrate-builders` skill (`.cursor/skills/orchestrate-builders/SKILL.md`), Builder Memory (ADR-0019, `builder_memory/`), Promotion Gates (ADR-0010), State/Run-context discipline (ADR-0007, ADR-0014), Contract-First (ADR-0001), Vertex-runtime-only boundary (ADR-0002), the M0/M1/M2/M3 frozen seams.
- **New ADR:** ADR-0023 Build Workflow Engine (build-time deterministic orchestration; filesystem authority; runtime isolation).
- **Milestone track:** **MB-series** — build-time Agent OS milestones, orthogonal to the M-series (M0–M18) product milestones. MB1 = this engine.

---

## 0. Naming & boundary (read first)

There are two agent systems in this repository. This spec concerns only **(B)**.

| | (A) ThesisOS runtime | (B) Build-time Agent OS — **this spec** |
|---|----------------------|------------------------------------------|
| Role | The product (research/thesis assistant) | The factory (Cursor agents that build A) |
| Lives in | `backend/app/`, `frontend/` | `.cursor/skills/orchestrate-builders/`, `plans/builder/`, `builder_memory/`, `builder_engine/` (new), `knowledge/`, `decisions/` |
| "Planner" | LangGraph node (M5+) | Builder Planner (epic → packets) |
| "tasks" | runtime DB table (M5+) | build-time packet DAG |
| "AgentOS loop" | future `agent_steps` tracing | the build workflow `Observe→…→Promote` |

**Hard rule:** if it runs inside `backend/app/` for an end user at request time, it is (A) and out of scope. If it lives under `.cursor/`, `plans/builder/`, or the build-time sidecars, it is (B).

---

## 1. Goals

1. **Make orchestration deterministic and repeatable.** Ready-set detection, ownership/lock assignment, wave advancement, merge, and validation-check execution become engine-computed, not LLM-eyeballed.
2. **Make validation mandatory.** No work packet reaches `done` and no worktree merges without its `required_checks` passing — enforced by code, surfaced in CI and a pre-commit hook.
3. **Move intelligence into the workflow.** The orchestrator LLM executes the engine's plan; LLMs remain the execution tool for parallel code-writing.
4. **Preserve everything that already works.** STATE/packet YAML schema, worktree isolation, ownership model, ADR governance, milestone freeze, and Builder Memory are reused unchanged.
5. **Evolve incrementally, backward-compatibly.** Five additive phases; the prose `orchestrate-builders` flow keeps working after every phase.
6. **Respect existing boundaries.** Filesystem stays authoritative (ADR-0019); no runtime coupling (ADR-0002); governance through ADRs and frozen specs (ADR-0001, ADR-0010).

---

## 2. Non-goals (hard boundary)

| Forbidden | Rationale |
|-----------|-----------|
| Authoritative state storage (DB or otherwise) | Filesystem + git win on any conflict (extends ADR-0019) |
| Editing specs, ADRs, or contracts | Governed artifacts change only via Architect + ADR |
| Generating product code | Cursor Task agents (builders) write code; the engine controls flow |
| ThesisOS runtime integration | No hooks into `/chat`, `ConversationService`, `GraphState`, `MemoryService`; no `backend.app` import |
| Replacing the `orchestrate-builders` skill | The skill remains the human/LLM operator surface; it *delegates* deterministic decisions to the engine |
| Replacing Builder Memory | Memory is retrieval; the engine is control — separate sidecars |
| Adopting an external workflow runtime (Temporal/Airflow/Prefect/LangGraph-for-builds) | Heavyweight, wrong abstraction, couples build to infra (ADR-0023 alt. b) |
| Changing the STATE/packet YAML schema in a breaking way | Backward compatibility is a hard requirement; additive fields only |
| Auto-promotion of milestones | Promotion still requires evidence in git (`docs/m{n}-promotion.md`), per ADR-0010 |

---

## 3. Architecture

### 3.1 System context

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                          BUILDEROS (Cursor / Agent OS)                         │
│                                                                                │
│   ┌────────────────────────┐         reads / derives / validates              │
│   │ orchestrate-builders    │◀───────────────────────────────────────────┐    │
│   │ skill (operator surface)│                                             │    │
│   └───────────┬─────────────┘                                             │    │
│               │ invokes deterministic commands                           │    │
│               ▼                                                           │    │
│   ┌─────────────────────────┐   reads    ┌──────────────────────────┐    │    │
│   │ builder_engine (NEW)     │──────────▶ │ plans/builder/STATE.yaml │    │    │
│   │  GraphLoader             │            │ plans/builder/packets/*  │────┘    │
│   │  Validator               │            │ specs · ADRs · gate YAML │         │
│   │  Scheduler               │            └──────────────────────────┘         │
│   │  CheckRunner             │   atomic writes (status/locks/wave only)        │
│   │  StateWriter ────────────┼────────────────────────────────────────┐       │
│   │  Replanner               │                                         ▼       │
│   │  CLI (`builder ...`)      │                          plans/builder/STATE.yaml│
│   └───────────┬─────────────┘                                                  │
│               │ emits dispatch manifest                                        │
│               ▼                                                                │
│   ┌─────────────────────────┐   (LLM step)   ┌──────────────────────────┐     │
│   │ Orchestrator LLM         │──────────────▶ │ Cursor Task builders      │     │
│   │ fan-out per manifest     │                │ (explorer/implementer/…)  │     │
│   └─────────────────────────┘                └────────────┬─────────────┘     │
│                                                            │ worktrees          │
│   ┌─────────────────────────┐   retrieval                 ▼                    │
│   │ builder_memory (ADR-0019)│──────────────▶ NON-AUTHORITATIVE context block  │
│   └─────────────────────────┘                                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                     THESISOS RUNTIME (system A — separate, frozen)             │
│   /chat · ConversationService · LangGraph · M2 MemoryService · /memory        │
│   builder_engine does NOT connect here (ADR-0002, ADR-0023).                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component model

| Component | Responsibility | Location (proposed) |
|-----------|----------------|---------------------|
| **GraphLoader** | Parse `STATE.yaml` + `packets/*.yaml` into an in-memory packet DAG | `builder_engine/graph.py` |
| **Validator** | Enforce graph + ownership + DoD invariants (supersedes `validate-state.sh`) | `builder_engine/validate.py` |
| **Scheduler** | Compute ready set; assign `file_locks` from `owned_files`; emit dispatch manifest | `builder_engine/scheduler.py` |
| **CheckRunner** | Execute named validation stages and packet `required_checks`; capture results | `builder_engine/checks.py` |
| **StateWriter** | Atomic, schema-preserving edits to STATE.yaml (status/locks/wave only) | `builder_engine/state.py` |
| **Replanner** | Derive remaining work, critical path, bottlenecks from state + gates | `builder_engine/replan.py` |
| **CLI** | `builder <command>` operator + CI entry point | `builder_engine/cli.py` |

**Deployment unit:** Python package under repo root `builder_engine/`, editable-installed exactly like `builder_memory/`. **Not** deployed to Cloud Run. Runs locally during Cursor sessions, in pre-commit, and in CI.

**Storage:** none authoritative. Optional gitignored `.builder-engine/` holds run logs / last dispatch manifest for debugging only. State of record stays in git-tracked `plans/builder/STATE.yaml`.

### 3.3 Control-plane vs execution-plane

| Plane | Owner | Examples |
|-------|-------|----------|
| **Control** (deterministic) | `builder_engine` | ready-set, locks, wave advance, check execution, DoD gate, merge eligibility |
| **Execution** (agentic) | Cursor Task builders via orchestrator LLM | writing code, tests, docs in owned files |
| **Retrieval** (deterministic, advisory) | `builder_memory` (ADR-0019) | NON-AUTHORITATIVE context block per agent |

---

## 4. Closed-loop control model

The brief's closed loop maps directly onto engine commands; the existing AgentOS loop (`knowledge/development/workflow.md`: `Observe → Hypothesis → Plan → Implement → Test → Critic → Revise → Promote`) is the per-packet refinement inside it.

```text
1. Observe state      →  builder state        (unified, derived project state)
2. Compare to goal    →  builder replan       (remaining work vs frozen spec + gates)
3. Compute work       →  builder ready        (ready set from the DAG)
4. Produce tasks      →  builder schedule     (locks + dispatch manifest)
5. Execute            →  orchestrator LLM fans out Cursor Task builders (worktrees)
6. Validate           →  builder sync → CheckRunner (required_checks must pass)
7. Update state       →  StateWriter (status→done, advance wave, clear locks)
8. Repeat             →  loop until milestone gate green → promote (ADR-0010, unchanged)
```

Each iteration must reduce the distance between current state and the frozen milestone spec; the engine makes that distance computable rather than asserted.

---

## 5. Data model

### 5.1 What the engine reads (unchanged schema)

The engine consumes the **existing** STATE and packet schemas. No breaking changes.

- `plans/builder/STATE.yaml`: `epic`, `chain`, `status`, `wave`, `decisions[]`, `file_locks{prefix→packet}`, `blockers{}`, `packets{id→{wave, agent_type, status, depends_on[], owned_files[], output, checks[], integration_notes}}`.
- `plans/builder/packets/*.yaml` (per `references/packet-template.yaml`): adds `objective`, `reads[]`, `writes_state[]`, `do_not_touch[]`, `invariants[]`, `out_of_scope[]`, `required_checks[{cmd, expect}]`, `done_criteria[]`.

### 5.2 Additive fields (optional, backward-compatible)

| Field | Where | Purpose |
|-------|-------|---------|
| `checks[].status` | packet check result | `pass\|fail\|skipped` recorded by CheckRunner (today `checks` is freeform/empty) |
| `engine.last_validated_sha` | STATE top-level | provenance of last engine validation (optional) |

Absence of these fields must never break the engine (they default).

### 5.3 What the engine derives (never stored as truth)

- **Ready set** — packets where `status == ready`, all `depends_on` are `done`, and packet `wave == STATE.wave`.
- **Critical path** — longest dependency chain through the DAG to the milestone integrator packet (bottleneck surface for replanning).
- **Project-state view** — composition of STATE.yaml + git tags (`m{n}-complete`) + gate evidence (`docs/m*-promotion.md`) + `knowledge/snapshots/*.json`.

---

## 6. Capabilities / CLI surface

Each command replaces a prose step in `orchestrate-builders/SKILL.md` (cited). The skill is updated to call these.

| Command | Replaces (SKILL prose) | Deterministic output |
|---------|------------------------|----------------------|
| `builder lint-graph` | §1 packet rules, validate-state.sh | Pass/fail on all graph + ownership + DoD invariants (§8) |
| `builder status` | §"Status" | STATE summary: epic, wave, packet table, locks, blockers |
| `builder ready` | §2A "a packet is ready when…" | The computed ready set for the current wave |
| `builder schedule` | §2B–2C lock + worktree prep | Sets `file_locks`, marks `in_progress`, creates worktrees, emits dispatch manifest |
| `builder check <stage>` | §3D ad-hoc commands | Runs a named validation stage (§7); exit code + captured output |
| `builder sync` | §3 Sync Barrier | Runs `required_checks`, validates, merges eligible worktrees, advances wave, clears locks |
| `builder state` | knowledge/context/current-state.md (manual) | Derived unified project-state object (JSON/YAML) |
| `builder replan` | manual Architect→Planner cycle | Remaining work, critical path, proposed next packets (state-grounded) |
| `builder adr-index` | manual knowledge index | Regenerate/lint ADR index vs `decisions/` (fixes drift) |

The **dispatch manifest** (output of `schedule`) is the contract handed to the orchestrator LLM: `[{packet_id, agent_type, worktree_path, owned_files, do_not_touch, decisions, dep_outputs, suggested_subagent_type}]`. The LLM performs the Cursor Task fan-out; it does not decide *what* to dispatch.

---

## 7. Validation pipeline (mandatory)

A single CheckRunner exposes named stages, each built from commands that already exist in the repo. Order = the brief's ladder.

| Stage | Command (reused) | Source today |
|-------|------------------|--------------|
| `lint` | `ruff check app` (backend); (frontend lint TBD) | promotion docs, coding-standards |
| `format` | `ruff format --check` | new (additive) |
| `typecheck` | `mypy` (backend, opt-in); `npx tsc --noEmit` (frontend) | mypy in pyproject; tsc in plans |
| `unit` | `pytest -q` (backend); `npm run test` / `vitest` (frontend) | promotion docs |
| `integration` | docker-compose live smoke (M1 T17 pattern) | M1 promotion |
| `drift` | schema snapshot test (`test_schema_snapshot`) | M0+ tests |
| `scope` | `rg -n "NotImplementedError\|wired post-M\|wired in M" backend/app` | promotion-gates.md |
| `infra` | `terraform validate` + `docker compose config` | M0 plan |

**Enforcement points:**
1. **Pre-commit hook** — fast stages (`lint`, `format`, `typecheck`, `scope`).
2. **CI** — a **test stage prepended to `infra/ci/cloudbuild.yaml` before the deploy steps** (or a GitHub Actions workflow): `lint → typecheck → unit → drift → scope`. Deploy only runs if green.
3. **Packet DoD** — `builder sync` runs each packet's `required_checks`; a packet cannot become `done` on a failing check.
4. **Merge gate** — `builder sync` refuses to merge a worktree whose checks are not green.

Runtime isolation is itself a check: `builder_engine/` (and `builder_memory/`) must not import `backend.app` (grep lint), reused from ADR-0019.

---

## 8. Resource ownership & concurrency invariants

The Validator enforces (superset of today's `validate-state.sh`):

1. **Deps exist** — every `depends_on` id is a known packet. *(exists today)*
2. **Dep ordering** — `in_progress`/`done` packets have all deps `done`. *(exists today)*
3. **Lock ownership** — every `file_locks` owner is a known packet. *(exists today)*
4. **Lock overlap** — no two owners share a locked path/prefix. *(exists today)*
5. **owned_files non-overlap within a wave** — no two packets in the same wave own the same path/prefix. *(NEW — the brief's "no two builders modify the same resource")*
6. **lock ⊆ owned** — a packet may only lock paths it `owns`. *(NEW)*
7. **Wave coherence** — top-level `wave` is consistent with per-packet `wave`/status transitions. *(NEW — M1 closed at the wrong wave)*
8. **DoD presence** — a packet entering execution has non-empty `required_checks` + `done_criteria`. *(NEW — "without a Definition of Done, the task cannot enter execution")*
9. **Decisions preserved** — `decisions[]` are passed verbatim to every dispatched builder. *(exists as prose)*

Ownership expires when a packet reaches `done` and its wave advances (locks cleared by StateWriter), matching the brief's temporary-ownership model. Worktrees provide physical isolation for implementers; explorers/reviewers run read-only in the main workspace.

---

## 9. Debug philosophy integration

The brief's scientific-debugging loop is wired in as a workflow stage rather than a reactive rewrite:

```text
Check fails (builder sync)
   │
   ▼
Invoke systematic-debugging skill (observe → hypotheses → rank → 1-variable experiment → evidence → fix)
   │
   ▼
builder_memory episodic-append --type failure_analysis --summary "…" --ref <paths>
   │
   ▼
Re-run only the failed required_check (no blind full rewrite)
```

`failure_analysis` is already an allowed episodic type (ADR-0019), so this closes the currently-manual lessons-learned bridge with no new storage.

---

## 10. Migration phases

Each phase is independently shippable, additive, and leaves the prose flow working. Phase 0 and Phase 1 may proceed in parallel.

| Phase | Delivers | Fixes (gap) | DoD |
|-------|----------|-------------|-----|
| **0 — Validation pipeline** | `builder check <stage>` runner + pre-commit hook + CI test stage before deploy | G1 (no CI/test gate) | All stages runnable by name; CI fails on red; pre-commit active |
| **1 — Graph read-model** | `builder_engine/` package + `lint-graph`, `status`, `ready` (ports & extends `validate-state.sh`, invariants §8.1–8.8) | G2 (manual ready/validate), G5 (DoD) | `lint-graph` reproduces validate-state.sh results + new invariants; `ready` matches SKILL §2A by construction |
| **2 — Runtime & sync** | **Execution state machine** (ADR-0025) + internal loop `State→Planner→Scheduler→Executor→Validator→StateUpdate`; CLI `schedule`/`sync` as projections; worktree manifest + CheckRunner DoD | G2 (scheduler), G5 (DoD enforcement) | End-to-end epic with formal transitions; no packet DONE without VALIDATING pass; **blocked until M4 spec frozen** |
| **3 — Unified state** | `builder state` + knowledge-drift check added to pipeline | G3 (state drift) | One derived state object; drift check catches mirror/ADR-index divergence |
| **4 — Replanning & governance** | `replan` (critical path/bottlenecks), debug-stage wiring, `adr-index` | G4 (manual replanning), G6 (debug), G7 (ADR drift) | `replan` proposes next packets from state; ADR index lint green |

(Gap IDs G1–G7 reference the migration analysis delivered with this spec.)

### 10.1 Phase 2 runtime model (amendment 2026-06-25, ADR-0025)

Phase 1 shipped CLI commands. Phase 2 **must not** grow as a bag of commands. The engine becomes a **workflow execution runtime**; agents are plug-in workers.

**Execution state machine (packet):**

```text
CREATED → READY → CLAIMED → RUNNING → VALIDATING → MERGED → DONE
                               ↘ FAILED → DEBUGGING → READY
```

**Internal loop (deterministic core):**

```text
State → Planner → Scheduler → Executor → Validator → StateUpdate
```

| Layer | Owner | Examples |
|-------|-------|----------|
| State | StateWriter + graph loader | STATE.yaml, wave, locks |
| Planner | Replanner (Phase 4) / stub in Phase 2 | ready set, critical path |
| Scheduler | Scheduler | locks, dispatch manifest |
| Executor | Orchestrator LLM + Cursor agents | code in worktrees |
| Validator | CheckRunner | `make ci`, packet `required_checks` |
| StateUpdate | StateWriter | status transitions, wave advance |

CLI mapping: `lint-graph`/`status`/`ready`/`schedule`/`sync` invoke runtime methods — they are not the source of truth for transitions.

**Sequencing gate:** M4 product spec must be frozen before Phase 2 ships, so embedding/search validation stages are not guessed in the engine.

---

## 11. Relationship to existing components

| Component | Change |
|-----------|--------|
| `orchestrate-builders/SKILL.md` | Updated to **call engine commands** for deterministic steps; remains the operator/LLM surface and the fan-out driver. No behavior removed. |
| `scripts/validate-state.sh` | Superseded by `builder lint-graph` (kept as a thin shim or deprecated after Phase 1). |
| `builder_memory/` | Unchanged. Engine and memory are independent sidecars; `schedule` may attach memory retrieval to dispatch manifests. |
| `plans/builder/STATE.yaml`, `packets/*.yaml` | Schema unchanged; optional additive fields (§5.2). |
| `decisions/`, frozen specs | Unchanged authority; engine reads, never writes. |
| `infra/ci/cloudbuild.yaml` | Gains a test stage before deploy (Phase 0). |
| ThesisOS runtime (A) | **Untouched.** |

---

## 12. Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Engine disagrees with skill prose | Skill cites command that errors | Skill treats engine as authority; add command-existence check |
| STATE.yaml hand-edited mid-wave | `lint-graph` invariant fail | Engine refuses to `schedule`/`sync` until green |
| Check flakiness | Non-deterministic stage result | Re-run policy; flaky checks quarantined, surfaced in `status` |
| Partial STATE write (crash) | Atomic write + temp-file rename | StateWriter writes atomically; never partial |
| Worktree/merge conflict | `git merge` non-zero | `sync` halts wave, records `integration_notes`, escalates to integrator (unchanged) |
| Engine imports runtime | grep lint in pipeline | Hard fail (ADR-0002/0019/0023) |
| Over-broad ownership causing serialization | critical-path/lock contention in `replan`/`schedule` | Re-plan smaller `owned_files`; sequence into more waves |
| Missing DoD on a packet | invariant §8.8 | `schedule` refuses to dispatch the packet |

---

## 13. Promotion gates

The engine does not gate product milestones; it strengthens the ADR-0010 pattern. MB1 itself promotes via its own gate.

### 13.1 MB1 engine gate (pre-merge to main)

```yaml
design_spec: approved              # this document, frozen 2026-06-25
adr_workflow_engine: complete      # ADR-0023
phase0_pipeline: green             # builder check runs all stages; CI test stage live; pre-commit active
phase1_read_model: green           # builder lint-graph reproduces validate-state.sh + new invariants
graph_invariants: enforced         # §8.1–8.9 covered by builder_engine tests
runtime_isolation: verified        # no builder_engine import of backend.app
backward_compat: verified          # existing orchestrate-builders flow + STATE schema unchanged
m0_m1_m2_m3_tests: green           # existing suites unaffected
scope_creep: false                 # no ThesisOS runtime hooks; no external workflow runtime
skill_updated: true                # SKILL.md cites engine commands
```

### 13.2 Per-phase gates

Each phase in §10 ships only when its DoD row is demonstrably green, with evidence recorded in a phase gate doc (`docs/mb1-phaseN-gate.md`) following the M-series promotion-evidence standard (re-runnable command + observed output).

---

## 14. Open questions

1. Package name: `builder_engine` vs folding the CLI under a shared `builder` namespace alongside `builder_memory` (single `builder` console script with subcommands)?
2. CI host: extend `infra/ci/cloudbuild.yaml` with a test stage, or add a `.github/workflows/` CI (and keep Cloud Build deploy-only)?
3. Frontend lint/format: adopt ESLint/Prettier now (currently unconfigured) or defer to a later phase?
4. Should `schedule` create worktrees itself, or only emit the manifest and let the orchestrator create them (cleaner separation of control vs side-effects)?
5. Do we deprecate `validate-state.sh` immediately after Phase 1, or keep it as a zero-dependency fallback?

---

## 15. Freeze record

This spec is **Frozen** as the architectural direction for the build-time Agent OS, per the 2026-06-25 evolution brief. Freeze means the *direction and boundaries* are stable; implementation proceeds phase by phase behind §13 gates. Changes to a frozen decision require an Architect re-freeze + (where it touches a decision) a superseding ADR — never a silent edit.

- [x] Two-system boundary (A vs B) confirmed (§0)
- [x] Determinism-vs-prompting direction accepted (ADR-0023)
- [x] Filesystem authority + runtime isolation preserved (ADR-0019, ADR-0002)
- [x] Backward-compatible, phased migration (§10)
- [x] Mandatory validation pipeline defined (§7)
- [x] Architect sign-off (per brief) — unblocks Phase 0
