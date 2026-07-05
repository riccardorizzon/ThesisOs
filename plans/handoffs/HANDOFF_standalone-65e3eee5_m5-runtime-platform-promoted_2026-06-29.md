# M5 Tool Router / Orchestration — promoted as the ASEP Runtime Platform (governance + Beast skill + M5.1→M5.6)

**Date:** 2026-06-29
**Status:** COMPLETED (tag `m5-complete` created; not pushed — no remote)
**Bead(s):** none (`bd` unavailable in this repo)
**Epic:** M5 — Tool Router / Orchestration (Product Track, ADR-0026)
**Chain:** `standalone-65e3eee5` seq `1`
**Parent:** `none — first in chain`
**Prior chain:** none — first in chain

## Related Handoffs

- `plans/handoffs/HANDOFF_standalone-5ed48e27_m4-recovery-sprint-closed_2026-06-26.md` — M4 retrieval recovery sprint (closed). Separate work stream; reference only, NOT a parent of this M5 chain.

## Reference Documents

- `AGENTS.md` — repo conventions + **Governance hierarchy** (Constitution > ADR > Runtime contract > Plans) + ASEP taxonomy
- `docs/runtime-constitution.md` — **Runtime Constitution v1** (invariants C1–C8), supreme for the Runtime Platform
- `decisions/ADR-0030-agent-runtime-layer-boundaries.md` — Business/Runtime/Infrastructure layers, rules R1–R8, Event Bus model, ASEP taxonomy (Runtime Platform as ASEP subsystem)
- `decisions/ADR-0027-multi-agent-graph-topology.md` — M5 graph topology (frozen)
- `docs/runtime-contract.md` — **Frozen v1** onboarding contract (event model, Runtime API, extension points, stability)
- `docs/architecture-decision-checklist.md` — per-PR review gate (ADC)
- `docs/m5-promotion.md` — M5 promotion gates + capability/commit map
- `plans/m5-tool-router-plan.md` — full M5 plan (phases, frozen-milestones table, M5.4 A/B/C split)
- `.cursor/skills/asep/SKILL.md` + `.asep/` — the ASEP "Beast" milestone-runner skill and its pipeline

## Architecture Snapshot

Graph topology (ADR-0027), unchanged from M5.2B; M5.4C only wraps nodes for events:

```text
START → supervisor → planner → router → memory_context
          → route_after_router(state.route)
                conversation_node → END
                grounded_chat: retriever_node → conversation_node → END
```

Layer map (ADR-0030 §2) — the review lens for every PR:

```text
Business   : graph/{supervisor,planner,router,memory_context,retriever}.py,
             orchestration/*, services/{task,memory,retrieval,document}/
Runtime    : graph/conversation.py (build_graph), graph/routing.py, graph/checkpointer.py,
             services/conversation/, runtime/* (events, contracts, event_bus, instrumentation, subscribers)
Infrastructure : db/, llm/, core/config.py
```

`RunContext` rides LangGraph `config.configurable.run_context` (never GraphState). Tasks: `tasks.id == TaskRef.id`. Events → Event Bus → subscribers (`agent_steps`, logging).

## The Goal

Turn ThesisOS from a linear M4 RAG pipeline into an orchestrated, observable, governed **Agent Runtime Platform** — without changing the frozen `GraphState` (ADR-0007) or the M1 `/chat` SSE seam. M5 wires the designed Supervisor → Planner → Router hierarchy with conditional routing, persists planner output to `tasks`, and makes every turn observable via a Runtime Event Bus. Beyond the code, this session also formalized the *process*: a Runtime Constitution (invariants), ADR-0030 (layer boundaries), a runtime contract, and an automated ASEP "Beast" skill that runs any milestone end-to-end from a one-line request. End state reached: M5 promoted (`m5-complete` tag), all gates green including live dogfood.

## Where We Are

- Branch `m5-tool-router`, working tree **clean**, HEAD `bf12c13`. Tag `m5-complete` → `bf12c13` (annotated, local-only; **no git remote configured**).
- M5 fully shipped across sub-milestones M5.1–M5.6, each its own commit + a docs/baseline commit (see Evidence table).
- Orchestrated graph wired in `backend/app/graph/conversation.py::build_graph`: `START → supervisor → planner → router → memory_context → [route_after_router] → conversation | retriever→conversation → END`.
- `TaskService` (`backend/app/services/task/service.py`): `upsert_from_task_ref` (INSERT…ON CONFLICT) + `mark_done`; planner persists via a composition-root hook `PlannerTaskPersistHook` (planner does NOT import TaskService).
- Runtime Event Contract: `backend/app/runtime/events.py` (`RuntimeEvent` frozen pydantic + `EventType` 7-event vocabulary), `contracts.py` (`RuntimeSubscriber`, `RuntimeEventEmitter` Protocols).
- Runtime Event Bus: `backend/app/runtime/event_bus.py` (`RuntimeEventBus`) — fan-out, registration order, non-blocking subscriber failures, zero-subscriber = valid/silent.
- Observability (M5.4C): `backend/app/runtime/instrumentation.py` wraps Business nodes (signature-transparent via `functools.wraps`) to emit Node/Route events; `backend/app/runtime/subscribers/{agent_steps,logging}.py`; `ConversationService` emits RunStarted/RunCompleted and passes `RunContext` via LangGraph config.
- `agent_runs.graph` renamed to `orchestrated_conversation`.
- Governance stack created: `docs/runtime-constitution.md` (C1–C8), `decisions/ADR-0030-…md` (R1–R8 + Event Bus + taxonomy), `docs/runtime-contract.md` (Frozen v1), `docs/architecture-decision-checklist.md`, `.github/pull_request_template.md` (layer declaration + C7 review order), `AGENTS.md` governance hierarchy.
- ASEP "Beast" skill: `.cursor/skills/asep/SKILL.md` (78-line director) + `.asep/` pipeline (`resolvers/`, `capabilities/runtime-platform.yaml` capability graph, `governance/manifest.yaml`, `pipeline/{executor,qualification,promotion}.md`, `templates/`, `reports/`).
- Test counts: backend `make ci` green (~230+ tests); `make unit-m4-recovery` = **43 passed**; `make qualify-m5` = **43 passed**; runtime contract tests 14, event bus 8, subscribers 8, observability 3, M5 integration 6 (3 params + 3), routing eval 2.
- Live dogfood (`make dogfood-m5`) PASS on the running stack (Vertex configured): **B_lat = 9.89s**, **B_ground = 6.54s** (evidence `/tmp/dogfood-m5-evidence.jsonl`).
- Local stack running via docker compose (`agentthesis-backend/frontend/db`, up ~2 days); `/chat` returns 200 with real Vertex Gemini.
- GraphState UNCHANGED; verified `"run_context" not in GraphState.model_fields` and Business agents do not import `app.runtime`.

## What We Tried (Chronological)

1. **Pre-M5 closure (commit `143f429`, prior to this chain's feature work):** fixed Makefile/test-DB isolation, migrations, M4 regression; M5 critic sign-off. Established cadence: implement → unit → integrate → regression → commit → review, with **ASEP implicit** from M5.2 on (short work orders, no long narrative).
2. **M5.1 (`9e2aa9b`):** supervisor/planner/router nodes + `orchestration/` helpers. Decided silent route normalization in router (Option C) — no `route_normalized` error.
3. **M5.2A (`c3097ea`):** `routing.py` (`route_after_router`/`resolve_route`) in isolation; no `build_graph` change.
4. **M5.2B (`c1075d1`):** wired topology + conditional edges. Graph tests needed a fake LLM (`OrchestrationLLM`) returning contract JSON from `generate()` for supervisor/planner/router before `astream()`.
5. **M5.3 (`c4d5e68`):** TaskService + planner hook. Initial version imported `TaskService` directly in `planner.py`; **corrected** after user review to a composition-root hook (`PlannerTaskPersistHook`). Added stream lifecycle behavior tests (success/exception/disconnect/mark_done-failure). Early test bug: FK violation because `Conversation` row needed `flush()` before `AgentRun` insert — fixed with `await db_session.flush()`.
6. **Governance (`05a1249`):** after user pushed for "runtime as a product", created Runtime Constitution + ADR-0030 + runtime-contract + ADC + PR template. User then refined: Constitution governs the **Runtime Platform** (not "supreme over ADRs"); ASEP stays the ecosystem (ADR-0026 unchanged) with "Runtime Platform" as a subsystem (taxonomy, no rename, no new ADR).
7. **ASEP skill v1 (`4985d79`):** parametric milestone-runner skill + `.asep/` templates.
8. **ASEP Beast refactor (`a91e40a`):** shrank SKILL.md 164→78 lines; externalized logic into `.asep/` (intent resolver, **capability graph**, governance manifest, pipeline stages). Reason on capabilities, not milestone numbers.
9. **M5.4A (`0339643`):** Runtime Event Contract only (no bus). Frozen `RuntimeEvent`, `EventType`, Protocols. Purity tests (no langgraph/db/business imports).
10. **M5.4B (`520d3bb`):** Runtime Event Bus only. Test bug: purity test asserted `"subscribers" not in source` but the word legitimately appears — narrowed to `app.runtime.subscribers`/concrete class names.
11. **M5.4C (`630d647`):** subscribers + lifecycle emission. Test bug: `memory_context_node(state, config)` takes a 2nd `config` arg; the node wrapper dropped it → `TypeError`. **Fixed** with `functools.wraps` so LangGraph re-injects `config`. Removed the obsolete M5.4A "no dependents yet" test (M5.4C intentionally wires the Runtime layer).
12. **M5.5 (`82c3dd3`):** qualification. Used **JSON not YAML** for the routing eval fixture (no PyYAML in backend). Kept HTTP-shim coverage in existing `test_chat_endpoint.py`; integration done at service level (errors) + graph level (both routes). Renamed `agent_runs.graph`.
13. **M5.6 (`dd1cfbe`):** promotion docs + freeze runtime-contract + knowledge mirror. Initially marked benchmarks/dogfood/tag PENDING (no live stack assumed) — honesty over green-washing.
14. **M5.6 live close (`bf12c13`):** discovered stack already up + Vertex configured; relaxed dogfood conversation assertion (route is an LLM decision, not deterministic) and ran `make dogfood-m5` → recorded real benchmarks. Then created `m5-complete` tag after user approval + full re-verification.

## Key Decisions

- **Business never emits telemetry (Constitution C3 + ADR-0030 R8).** Emission is wrapped at the composition root (`build_graph` node wrappers, `ConversationService`), never inside agent bodies. Rejected: planner/nodes calling `telemetry.record(...)`.
- **Planner → TaskService via hook, not direct import.** Keeps Business unaware of persistence. Rejected: `from app.services.task import TaskService` in `planner.py`.
- **Event Bus is the M5.4 deliverable, telemetry is a subscriber.** Rejected telemetry-first wiring (couples runtime to storage; blocks future OTel/UI subscribers).
- **Constitution governs the Runtime Platform; ASEP unchanged.** Rejected renaming ASEP (would break frozen ADR-0026). "Runtime Platform" added as taxonomy (ADR-0030 §0), no new ADR.
- **Capability graph over milestone numbers.** The Beast skill resolves requests to capability nodes (deps/requires/baseline), not phase numbers — future-proof.
- **M5.4 split A/B/C** for smallest shippable diffs (contract → bus → subscribers+lifecycle), even though the plan originally bundled them.
- **JSON eval fixture, not YAML** — avoid adding PyYAML to backend deps.
- **Tag withheld until explicit approval + live benchmarks** (verification-before-completion). Created only after `make dogfood-m5` PASS and user go-ahead.
- **Author identity via inline `-c`**, never `git config` (rule). All commits authored `ThesisOS Agent <agent@thesisos.local>` to match history.

## Evidence & Data

### Commit chain (this session)

| Commit | Milestone | Summary |
|--------|-----------|---------|
| `9e2aa9b` | M5.1 | supervisor/planner/router + orchestration helpers |
| `c3097ea` | M5.2A | routing infrastructure (`route_after_router`) |
| `c1075d1` | M5.2B | graph wiring + conditional routing |
| `c4d5e68` | M5.3 | TaskService + planner persistence hook |
| `05a1249` | governance | Runtime Constitution + ADR-0030 + runtime contract |
| `bc3da7a` | baseline | record M5.3 + governance logical baseline |
| `4985d79` | asep | ASEP milestone-runner skill + templates |
| `a91e40a` | asep | Beast architecture — director skill + `.asep` pipeline |
| `0339643` | M5.4A | Runtime Event Contract |
| `520d3bb` | M5.4B | Runtime Event Bus |
| `6da64b7` | docs | record Event Bus baseline; split M5.4 A/B/C |
| `630d647` | M5.4C | Event Bus wired — subscribers + lifecycle emission |
| `809e510` | docs | record Observability baseline; M5.4 complete |
| `82c3dd3` | M5.5 | runtime qualification — integration, error contracts, routing eval |
| `e934c47` | docs | record Runtime Qualification baseline |
| `dd1cfbe` | M5.6 | promote — promotion doc, freeze runtime contract, knowledge mirror |
| `bf12c13` | M5.6 | record live dogfood benchmarks; tag remains (← `m5-complete`) |

### Frozen capability baselines (`.asep/capabilities/runtime-platform.yaml`)

| Capability | Phase | Status | Baseline |
|------------|-------|--------|----------|
| event-contract | M5.4A | done | `0339643` |
| event-bus | M5.4B | done | `520d3bb` |
| observability | M5.4C | done | `630d647` |
| lifecycle-instrumentation | M5.4C | done | `630d647` |
| qualification | M5.5 | done | `82c3dd3` (B_lat=9.89s, B_ground=6.54s) |
| promotion | M5.6 | done | tag pending→created |

### Gates (final)

| Gate | Result |
|------|--------|
| `make ci` | PASS (exit 0) |
| `make unit-m4-recovery` | 43 passed |
| `make qualify-m5` | 43 passed |
| `make dogfood-m5` (live) | PASS — B_lat 9.89s / B_ground 6.54s |
| ruff | clean |
| scope-creep scan | only intentional milestone stubs |

### Canonical event vocabulary (7)

`RunStarted · NodeStarted · RouteSelected · TaskPersisted · NodeCompleted · NodeFailed · RunCompleted`

### Dogfood evidence (`/tmp/dogfood-m5-evidence.jsonl`)

```json
{"step":"conversation","b_lat_s":9.886319472}
{"step":"grounded","b_ground_s":6.544413311}
{"step":"complete","verdict":"pass"}
```

### Existing release tags

`m0-complete · m1-complete · m2-complete · m3-complete · m4-complete · m5-complete` (l4-phase0-complete also present)

### Routing eval set (`backend/tests/fixtures/m5_routing_eval.json`, accuracy 1.0)

| Case | user_message | llm_route | expected |
|------|--------------|-----------|----------|
| wired_conversation | "Summarize what we discussed" | conversation | conversation |
| wired_grounded | "What do my documents say about craftsmanship" | grounded_chat | grounded_chat |
| reserved_route_to_default | "Write me a short poem about the sea" | writer | conversation |
| reserved_route_with_retrieval_keyword | "According to my sources, summarize the argument" | critic | grounded_chat |
| unknown_route_to_default | "hello there, how are you" | banana | conversation |
| unknown_route_with_retrieval_keyword | "search my library for the citation" | banana | grounded_chat |
| no_route_null | "hi" | null | conversation |
| malformed_json | "hi" | "__malformed__" | conversation |

### Errors resolved during the session (don't re-discover)

| Symptom | Cause | Fix |
|---------|-------|-----|
| FK violation inserting `AgentRun` (M5.3 test) | `Conversation` row not flushed before `AgentRun` | `await db_session.flush()` before adding the run |
| Purity test false-positive (M5.4B) | word "subscribers" appears in bus docstring | assert only `app.runtime.subscribers` / concrete class names absent |
| `TypeError: memory_context_node() missing 'config'` (M5.4C) | node wrapper had `(state)` and dropped LangGraph's 2nd `config` arg | `functools.wraps(node_fn)` + `*args/**kwargs` so signature unwraps and `config` is re-injected |
| Obsolete "no dependents yet" test (M5.4C) | M5.4A asserted nothing imports `app.runtime`; M5.4C intentionally wires the Runtime layer | removed it; durable Business-purity test lives in `test_runtime_subscribers.py` |
| dogfood conversation `sources_count == 0` would fail (M5.6) | routing is an LLM decision; live LLM grounded a generic question | relaxed live assertion to "received a reply" (route correctness stays in `test_m5_routing_eval.py`) |

## Code Analysis

- `RuntimeEvent` (events.py): `model_config = ConfigDict(frozen=True, extra="forbid")`; fields `event_type: EventType`, `run_id: str`, `timestamp: datetime` (default UTC), `correlation_id: str|None`, `metadata: dict`. Event-specific data lives in `metadata` (envelope stays stable — Constitution C5).
- `RuntimeEventBus.emit` (event_bus.py): sequential `await subscriber.on_event(event)` in registration order, each in `try/except` that logs+swallows (R6). `subscribe()` for composition-root registration. Imports only `contracts`/`events`.
- `instrument_node` (instrumentation.py): `@functools.wraps(node_fn)` + `async def wrapped(*args, **kwargs)` so `inspect.signature` unwraps to the node → LangGraph still injects `config`. Emits NODE_STARTED → (node) → NODE_COMPLETED/NODE_FAILED with `duration_ms`; `route_event=True` (router only) emits ROUTE_SELECTED from `result["route"]`.
- `build_graph(..., emitter=None, run_context=None)`: when both present, wraps every node via local `node(name, fn, phase, route_event=)`; phases `plan` (supervisor/planner/router) vs `implement` (memory_context/retriever/conversation). With no emitter → byte-for-byte M5.2B topology (existing tests unaffected).
- `ConversationService.__init__(*, task_service=None, event_bus=None)`: default bus = `RuntimeEventBus([AgentStepsSubscriber(), LoggingSubscriber()])`. `stream_turn` emits RunStarted after setup, RunCompleted on done/error/cancelled; `cfg={"configurable":{"thread_id":conv_id,"run_context":rc.model_dump()}}`.
- `AgentStepsSubscriber.on_event`: persists one `agent_steps` row only for NODE_COMPLETED (status done) / NODE_FAILED (status error); `started_at = now - duration_ms`; ignores run-level events; guarded so it never raises.
- `coerce_m5_route` (orchestration/coerce.py): wired route → as-is; else if `RETRIEVAL_KEYWORDS` in user msg → `grounded_chat`; else `conversation`. Router emits `no_route` only on missing/empty route or JSON parse failure.
- M4 execution node bodies (`memory_context.py`, `retriever.py`, `prompt_wire.py`, conversation node) unchanged.

## Governance Quick Reference (do not violate without an ADR)

**Runtime Constitution C1–C8** (`docs/runtime-constitution.md`):
- C1 Layering: Business → Runtime → Infrastructure (no inverse deps)
- C2 Composition Root: only it binds the three layers
- C3 Business Purity: no db / telemetry / logging / event bus / LangGraph in Business
- C4 Runtime Events: emit canonical events only; subscribers are replaceable
- C5 Stable Contracts: incompatible change to agent JSON / GraphState / `/chat` / event vocab → ADR
- C6 M4 Compatibility: no change to validated M4 behavior without an ADR
- C7 Review Order: Constitution → Layer → Contracts → Events → Feature → Performance → Code
- C8 Extension Rule: add via documented extension points; no direct cross-layer deps

**ADR-0030 rules R1–R8:** R1 nodes pure over ports · R2 composition root wires concretes · R3 no Business→Infra imports in agents · R4 domain services are Business (may use Infra internally) · R5 RunContext out of GraphState (via config) · R6 subscribers non-blocking · R7 `builder_engine`/control plane never import `backend.app` · R8 Business never emits telemetry/events directly.

## Running the ASEP Beast Skill (next milestone)

- Invoke with a one-liner: e.g. `ASEP: implementa M6 Writer agent`. Intent is deduced (develop/review/design/qualify/promote/status) — no commands.
- Pipeline (skill reads each stage file): `.asep/resolvers/intent.md` → `.asep/resolvers/capability.md` (→ `.asep/capabilities/runtime-platform.yaml`) → `.asep/governance/manifest.yaml` → `.asep/templates/work-order-template.md` → `.asep/pipeline/executor.md` → `.asep/pipeline/qualification.md` → `.asep/pipeline/promotion.md`.
- It **STOPs** (report, no code) on: Constitution violation, required cross-layer dep, public-contract change without ADR, dirty tree / wrong baseline, red gate, or plan/ADR inconsistency.
- For M6: add a `writer` capability node (depends_on the M5 runtime; requires a `writer.json` contract + new route) to the capability graph before running.

## Files Changed

### Source — runtime (new package `backend/app/runtime/`)
- `events.py` — RuntimeEvent + EventType + EVENT_VOCABULARY
- `contracts.py` — RuntimeSubscriber, RuntimeEventEmitter Protocols
- `event_bus.py` — RuntimeEventBus
- `instrumentation.py` — node wrappers + emit_safely + make_event
- `subscribers/__init__.py`, `subscribers/agent_steps.py`, `subscribers/logging.py`

### Source — business/runtime wiring
- `backend/app/graph/planner.py` — optional `on_task_ref` hook (no TaskService import)
- `backend/app/graph/orchestration/task_persistence.py` — `PlannerTaskPersistHook` type
- `backend/app/graph/conversation.py` — `build_graph` emitter/run_context + node wrapping + task-hook TaskPersisted
- `backend/app/services/task/__init__.py`, `service.py` — TaskService
- `backend/app/services/conversation/service.py` — bus, RunStarted/RunCompleted, RunContext-in-config, graph name `orchestrated_conversation`

### Tests
- `test_task_service.py`, `test_conversation_task_lifecycle.py` — TaskService + stream lifecycle
- `test_runtime_event_contract.py` (14), `test_runtime_event_bus.py` (8), `test_runtime_subscribers.py` (8), `test_runtime_observability.py` (3)
- `test_m5_chat_integration.py` (error contracts + both routes), `test_m5_routing_eval.py` (eval harness)
- `backend/tests/fixtures/m5_routing_eval.json` — 8 labeled routing cases
- `backend/tests/support/orchestration_llm.py` — shared fake LLM (from M5.2B)

### Governance & docs
- `docs/runtime-constitution.md`, `docs/runtime-contract.md` (Frozen v1), `docs/architecture-decision-checklist.md`, `docs/m5-promotion.md`
- `decisions/ADR-0030-agent-runtime-layer-boundaries.md`; ADR-0027 §4.1 wording aligned
- `.github/pull_request_template.md`; `AGENTS.md` governance hierarchy
- `knowledge/architecture/graph.md`, `knowledge/project/roadmap.md`, `knowledge/agents/README.md`, `knowledge/contracts/graphstate.md`

### ASEP skill / process
- `.cursor/skills/asep/SKILL.md`; `.asep/` (README, resolvers/, capabilities/, governance/, pipeline/, templates/, reports/)

### Ops
- `bin/dogfood-m5-conversation-run.sh`; `Makefile` (`qualify-m5`, `dogfood-m5`); `plans/m5-tool-router-plan.md`

## User Feedback & Preferences (REQUIRED)

- "procedi con lo stesso metodologia di prima" — keep the short work-order / implicit-ASEP cadence; don't restate the whole process each time.
- Strong on **architecture purity**: caught that Planner must not know persistence; wanted the rule "Business produces TaskRef → TaskService persists", not "Planner knows how to save".
- Pushed the project from "feature delivery" to **"runtime as a product"**; review order = layer → contracts → events → feature.
- Wanted a **Runtime Constitution** above ADRs, but corrected the wording: not "supreme over ADRs" — "defines invariants; ADRs/plans stay consistent". Precision matters to them.
- Keep **ASEP** name (ADR-0026); introduce "Runtime Platform" as a subsystem via taxonomy, NOT a rename or new ADR. Prefers minimal terminological churn.
- Beast skill = **smaller, smarter**: "L'errore è mettere tutta la logica dentro SKILL.md" — externalize to `.asep/`, skill is just the director; reason on a **capability graph**.
- Wanted the strong Event Bus rule: "L'Event Bus non deve conoscere alcun subscriber concreto."
- Before M5.6: "sei sicuro che tutto a posto … il resto è frozen?" — wants explicit verification (run the gates) before advancing, and frozen scopes respected.
- "fai tutto il necessario prima di iniziare m5.6" — willing to run live gates; expects me to actually execute, not just document.
- On the tag: confirmed creating an **annotated, immutable** `m5-complete` after the full checklist; if bugs arise post-tag, new tag (`m5.0.1`/`m5-hotfix`), never move `m5-complete`. Mentioned optional `v0.5.0` versioned tag (deferred to their versioning strategy).
- Tone: concise milestone reports with a status block (Milestone Status / Repository Status / Remaining Scope / Known Risks / Recommended Next Action). Italian throughout.

## Where We're Going

1. **(Optional) Configure a git remote** then `git push` the branch + `m5-complete` tag (only on explicit request — git safety + no remote currently).
2. **(Optional) Merge `m5-tool-router` → `main`.** If the tag should mark the merge, re-tag the merge commit; otherwise leave `m5-complete` on `bf12c13`.
3. **M6 — Writing** (`writer` agent): `contracts/agents/writer.json`, drafts chapters from `plan` + retrieved context; writes `GraphState.draft`/`citations`. Add as a new capability node in `.asep/capabilities/runtime-platform.yaml`; wire as a route + node + edge (extension pattern in `docs/runtime-contract.md` §5). Run via `ASEP: implementa M6 …`.
4. **Later runtime hardening:** OpenTelemetry subscriber (M11), latency optimization (3 orchestration LLM calls/turn — B_lat ≈ 9.9s), possible batched `agent_steps` writes if dogfood shows overhead.

## Risks & Blockers

- **No git remote configured** — nothing pushed; tags/branch are local only.
- **Benchmarks are single-sample smoke**, not statistical (B_lat 9.89s / B_ground 6.54s). Fine for the promotion gate; revisit under load in M11.
- **Latency:** every chat turn pays 3 orchestration LLM calls (ADR-0027 known consequence) — not optimized.
- **AgentStepsSubscriber opens one DB session per node terminal event** — acceptable now; candidate for batching if it shows up in benchmarks.

## Open Questions

- Should `m5-complete` move to the eventual `main` merge commit, or stay on the branch tip? (User leaning: tag the immutable milestone state; don't move it.)
- Versioning strategy: adopt `vMAJOR.MINOR.PATCH` (e.g. `v0.5.0`) alongside `m{n}-complete`? (User flagged as optional, undecided.)

## Quick Start for Next Session

```bash
# Restore context (no beads system here)
cat plans/handoffs/HANDOFF_standalone-65e3eee5_m5-runtime-platform-promoted_2026-06-29.md

# Reference docs (governance comes first — Constitution C7 review order)
sed -n '1,80p' docs/runtime-constitution.md
sed -n '1,60p' decisions/ADR-0030-agent-runtime-layer-boundaries.md
cat docs/runtime-contract.md
cat plans/m5-tool-router-plan.md            # frozen-milestones table + M6 nothing yet

# Key files to read first
backend/app/graph/conversation.py            # build_graph: orchestration + emitter wiring
backend/app/runtime/                          # events, contracts, event_bus, instrumentation, subscribers/
backend/app/services/conversation/service.py  # turn lifecycle + event emission
.cursor/skills/asep/SKILL.md + .asep/capabilities/runtime-platform.yaml  # capability graph

# Evidence / data
docs/m5-promotion.md                          # gate map + commit/capability table
/tmp/dogfood-m5-evidence.jsonl                # live benchmarks (ephemeral)

# Verify current state
git status -s && git log --oneline -5 && git show m5-complete --no-patch
make ci && make qualify-m5 && make unit-m4-recovery

# Next action
# Start M6 (Writing) via the Beast skill:  "ASEP: implementa M6 Writer agent"
# (add a writer capability node to .asep/capabilities/runtime-platform.yaml first)
```
