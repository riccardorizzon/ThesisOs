# M5 Phase 1 — Investigation Report (Closed)

- **Status:** Investigation closed — implementation authorized pending this document
- **Baseline:** `main` @ `143f429` (Pre-M5 Closure Sprint complete)
- **Spec:** `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`
- **ADR:** `decisions/ADR-0027-multi-agent-graph-topology.md`
- **Plan:** `plans/m5-tool-router-plan.md`
- **Critic sign-off:** `docs/m5-critic-signoff.md` (2026-06-28)

---

## Architectural decision (summary)

M4 today runs a **linear** graph on every `/chat` turn:

```text
START → memory_context_node → retriever_node → conversation_node → END
```

M5 prepends orchestration and branches **after** the router (ADR-0027):

```text
START → supervisor → planner → router → [conditional]
  route=conversation:   memory_context → conversation → END
  route=grounded_chat:    memory_context → retriever → conversation → END
```

Execution nodes (`memory_context`, `retriever`, `conversation`, `prompt_wire`) remain **frozen**; only `build_graph()` composition changes. Routing uses a **3-node LLM pipeline** (supervisor → planner → router) plus a **deterministic post-router normalizer** (reserved routes, parse failures → `conversation`).

Key files today: `backend/app/api/chat.py` → `ConversationService.stream_turn()` → `backend/app/graph/conversation.py`.

---

## Rejected alternatives

| Alternative | Why rejected | Primary blocker |
|-------------|--------------|-----------------|
| **Routing at HTTP layer** (`chat.py` / pre-graph classifier) | Bypasses agent contracts; no `plan`/`task`; no per-node `agent_steps`; splits orchestration from LangGraph | Violates M5 spec §4.1 and M0 multi-agent hierarchy |
| **Routing inside `retriever_node`** (`if route != grounded_chat: skip`) | Retriever still scheduled every turn; mutates M4-frozen node semantics | ADR-0027 requires conditional **edge**, not node-internal gate |
| **Routing inside `conversation_node`** | Monolith; cannot skip retriever cleanly; untestable orchestration in isolation | ADR-0027 explicitly rejected |
| **Pure deterministic classifier** (regex/keywords only) | No `Plan`/`TaskRef`; no planner task upsert; brittle on natural language | Does not satisfy supervisor/planner/router contracts |
| **Router before planner** | Planner needs supervisor coarse plan | ADR-0027: hierarchy Supervisor → Planner → Router |
| **Always run retriever** (status quo M4) | Wastes embed/search on general chat; defeats M5 purpose | Spec §6.2: `conversation` path must skip retriever |
| **Multi-agent fan-out / M12 re-entry loop** | Parallel agents, writer/critic loops, supervisor re-entry | Hard M5 non-goal; deferred to M12 |
| **New GraphState fields** (`orchestration` sub-model) | Would require ADR-0007 amendment | Frozen GraphState |
| **New REST endpoints for routing** | Orchestration is graph-internal | Spec §2.2 non-goals |

**Selected:** ADR-0027 prepend chain + conditional edges + LLM orchestration nodes with deterministic normalization fallback.

---

## Quantitative KPIs (promotion criteria)

These numbers are the **product and engineering bar** for declaring M5 complete. They supplement (do not replace) the spec §7 YAML gate and `docs/m5-promotion.md`.

### How KPIs are measured

| KPI | Target | Measurement method | When evaluated |
|-----|--------|-------------------|----------------|
| **Retrieval avoided on normal chat** | ≥ 90% | Eval set **E_conv** (≥ 30 generic prompts: greetings, meta, brainstorming). Assert `route=conversation` and retriever mock/`agent_steps` shows retriever **not** executed. | Phase 2+ CI; pre-promotion |
| **Routing accuracy (overall)** | ≥ 95% | Eval set **E_route** (≥ 50 labeled prompts, gold label ∈ `{conversation, grounded_chat}`). Accuracy = correct final route / total. | Pre-promotion benchmark job |
| **False negative grounded** | < 2% | Subset **E_ground** ⊆ E_route where gold = `grounded_chat`. FN rate = routed `conversation` / \|E_ground\|. | Pre-promotion (critical — grounding loss) |
| **False positive grounded** | monitor, no hard fail | Subset where gold = `conversation` but routed `grounded_chat`. Track cost/latency impact. | Pre-promotion (informational) |
| **M4 regressions** | **0** | `make unit-m4-recovery` + `builder-engine check embed` + `builder-engine check search-smoke` — all PASS; no changes to retriever/memory/prompt_wire bodies | Every phase |
| **`make ci`** | **100%** | `make ci` exit 0 on clean `thesisos_test` DB | Every commit / phase gate |
| **Dogfood — grounded path** | **100%** | `make dogfood-m4` PASS (existing Sennett corpus smoke) | Pre-promotion |
| **Dogfood — conversation path** | **100%** | New smoke: generic prompt through `/chat`, assert reply without retriever step, no crash | Phase 5; pre-promotion |
| **Supervisor parse failure** | < 0.5% | Over **E_route** runs: count turns where supervisor JSON parse fails (or `no_objective` from parse, not content) / total turns | Pre-promotion |
| **Planner parse failure** | < 0.5% | Same for planner JSON parse failures | Pre-promotion |
| **Router fallback rate** | **monitored** | Count turns where final route = `conversation` due to `no_route`, parse error, or `route_normalized` / total turns. Target: establish baseline; alert if > 10% on E_route. | Ongoing via `agent_steps` + `errors` |
| **P95 latency — conversation path** | ≤ M4 p95 − retriever cost | Benchmark **B_lat**: 20 turns × E_conv. Compare M5 `conversation` p95 vs M4 baseline (retriever always on). Expect improvement. | Pre-promotion |
| **P95 latency — grounded path** | ≤ M4 p95 + 25% | Benchmark **B_ground**: 20 turns × E_ground. M5 adds 3 orchestration LLM calls; acceptable overhead cap. | Pre-promotion |
| **Orchestration token overhead** | **documented** | Sum usage from orchestration LLM calls (supervisor + planner + router) per turn; report mean/p95 on E_route. No hard fail — publish in promotion doc. | Pre-promotion |

### Eval set ownership

- **E_conv**, **E_ground**, **E_route** live in `backend/tests/fixtures/m5_routing_eval.yaml` (created Phase 2).
- Gold labels are **human-reviewed**, not LLM-generated.
- Routing accuracy tests run in CI as **non-blocking benchmark** until Phase 5; **blocking** at promotion gate.

### Failure policy

| Condition | Action |
|-----------|--------|
| FN grounded ≥ 2% | **Block promotion**; tune router prompt/normalizer |
| Routing accuracy < 95% | **Block promotion** |
| M4 regression or `make ci` red | **Block merge** immediately |
| Retrieval avoided < 90% on E_conv | **Block promotion** |
| Latency grounded path > M4 p95 + 25% | Investigate; block if UX unacceptable in dogfood |

---

## M5 Definition of Done

M5 is **complete** when **every** item below is checked. This is the authoritative closure checklist — not open to reinterpretation at promotion time.

### Orchestration graph

- [ ] **Supervisor always executed** — every `/chat` turn runs `supervisor_node` before execution subgraph; `agent_steps` row with `agent=supervisor`, `phase=plan`
- [ ] **Planner always executed** — every turn runs `planner_node` after supervisor; `agent_steps` row with `agent=planner`
- [ ] **Router always executed** — every turn runs `router_node` after planner; `agent_steps` row with `agent=router`
- [ ] **Retriever only on `grounded_chat`** — on `route=conversation`, retriever node is **not** invoked (mock test + `agent_steps` absence); on `grounded_chat`, retriever behavior **identical to M4**

### M4 preservation

- [ ] **Conversation path invariant** — `conversation_node` + `compose_prompt_wire()` unchanged; SSE events `token`, `sources`, `done` shape unchanged
- [ ] **Memory path invariant** — `memory_context_node` unchanged; operational memory (editable, pinned user/thesis) injected on **both** routes
- [ ] **GraphState frozen** — no new fields; drift test green
- [ ] **No scope creep** — no writer/critic/citation nodes; no M12 re-entry; no new REST endpoints

### Persistence & observability

- [ ] **TaskService wired** — planner upserts `tasks` row; `TaskRef.id == tasks.id`; successful finalize → `mark_done`
- [ ] **agent_steps complete** — one step per executed node per turn; linked to `agent_run_id` via RunContext in config (not GraphState)
- [ ] **Error contracts** — `no_objective`, `unplannable`, `no_route` append to `errors` and turn still completes with user reply

### Tests & CI

- [ ] **Unit tests** — supervisor, planner, router, routing, graph topology, task service, agent_steps, chat integration
- [ ] **`make ci` PASS** — 100%, exit 0
- [ ] **No M4 regression** — `make unit-m4-recovery`, embed check, search-smoke check all PASS
- [ ] **Routing eval** — KPI routing accuracy ≥ 95%, FN grounded < 2%, retrieval avoided ≥ 90% on E_conv

### Dogfood

- [ ] **Dogfood conversation PASS** — generic chat smoke (no corpus query); retriever skipped; assistant reply received
- [ ] **Dogfood grounded_chat PASS** — `make dogfood-m4` PASS on real corpus (Sennett / existing evidence)

### Benchmarks

- [ ] **Latency benchmark recorded** — B_lat and B_ground p50/p95 documented in promotion doc
- [ ] **Token benchmark recorded** — orchestration overhead mean/p95 documented

### Documentation & promotion

- [ ] **`docs/m5-promotion.md`** — all gates green with evidence
- [ ] **Knowledge mirror updated** — `knowledge/architecture/graph.md`, `knowledge/context/current-state.md`, roadmap
- [ ] **Promotion checklist** — spec §7 YAML criteria all green
- [ ] **Tag `m5-complete`** on `main`

---

## Implementation discipline (mandatory)

Every M5 phase must satisfy **both** rules below before merge. No exceptions.

### 1. Shippable phases

At the end of **each** phase:

- `make ci` is green (exit 0)
- M4 regression is green (`make unit-m4-recovery`, `builder-engine check embed`, `builder-engine check search-smoke`)
- The branch is **merge-ready** — no half-wired graph, no feature flags left dangling, no “will connect later” imports from production paths

Do **not** wait until promotion to have a working tree. Each phase lands as a complete, reviewable unit.

### 2. No dead code

Code added in a phase that is not yet wired (e.g. `supervisor.py` before graph wiring) must still be:

- **Fully unit-tested** against its agent contract
- **Contract-compliant** (`contracts/agents/*.json` reads/writes/errors)
- **Free of structural TODOs** and unused placeholders — if it ships, it is done

Orphan modules, stub classes, and “Phase N will wire this” comments in production code are forbidden.

### Gate (every phase)

```bash
make ci && make unit-m4-recovery
```

**Process note:** From M5.2 onward, ASEP is implicit in every milestone — prompts specify scope only; the cycle is not restated each time.

---

## Authorized implementation sequence

Investigation is closed. Implementation proceeds in this order (routing infrastructure **before** `build_graph()` changes):

| Step | Phase | Deliverable |
|------|-------|-------------|
| 1–3 | M5.1 @ `9e2aa9b` | supervisor, planner, router (**frozen**) |
| 4 | **M5.2A** | `routing.py` + unit tests; graph unchanged |
| 5 | **M5.2B** | `build_graph()` conditional edges + graph integration tests |
| 6 | Phase 6 | TaskService |
| 7 | Phase 7 | Telemetry (`agent_steps`) |
| 8 | Phase 8 | `/chat` integration |
| 9 | Phase 9 | Eval dataset + routing benchmark |
| 10 | Phase 10 | Dogfood + latency/token benchmark |
| 11 | Phase 11 | Promotion + tag `m5-complete` |

**Branch:** `m5-tool-router` @ `9e2aa9b` (M5.2 baseline).

**Rationale for M5.2A before M5.2B:** isolate LangGraph dispatch logic from graph composition — if regressions appear, the fault domain is unambiguous.

---

## Investigation sign-off

| Role | Status | Date |
|------|--------|------|
| Architecture investigation | **Closed** | 2026-06-28 |
| M5.1 orchestration foundation | **Frozen** @ `9e2aa9b` | 2026-06-28 |
| M5.2A / M5.2B plan documented | **Complete** | — |
| Code start (M5.2A) | **Awaiting authorization** | — |

**Next action (when authorized):** M5.2A — `routing.py` + `test_routing.py`; no `build_graph()` changes.
