# ADR-0030: Agent Runtime Layer Boundaries

- Status: Accepted (2026-06-28)
- Governance: Must remain **consistent with the Runtime Constitution** (`docs/runtime-constitution.md`), which defines the architectural invariants of the Runtime Platform. This ADR provides the enforcement detail for articles C1–C8 (rules R1–R8 below); review order follows Constitution C7.
- Context: M5 wired orchestration (supervisor → planner → router → conditional execution) on top of the M4 RAG pipeline. ThesisOS is no longer a linear retrieval chatbot — it is an **Agent Runtime** with domain agents, graph dispatch, checkpointed working state, task persistence, and (next) observability. Without explicit layer boundaries, M5.4+ will introduce cross-dependencies (graph nodes importing DB clients, infrastructure leaking into business agents, concrete services wired inside node bodies) that are expensive to unwind in M6–M12. M5.3 already exposed one risk: the planner initially imported `TaskService` directly; that was corrected to a composition-root hook (`PlannerTaskPersistHook`). This ADR freezes the three-layer model and dependency rules **before** the Runtime Event Bus (M5.4). From this point, ThesisOS is described as a **runtime product** (layers + contracts + events), not a collection of feature milestones.

- Decision:

  ### 0. Terminology — ASEP taxonomy (no rename)

  **ASEP** (ADR-0026) is unchanged: it remains the name of the **entire ecosystem**.
  What M5 builds is a **subsystem** of ASEP — the **Runtime Platform** — not a new
  top-level entity. This is a taxonomy clarification, not a governance redefinition;
  ADR-0026 stays valid and no rename of `ASEP` strings is performed.

  ```text
  ASEP (ecosystem) ............................. ADR-0026 (unchanged)
  │
  ├── Governance ............................... Runtime Constitution, ADRs, review discipline
  ├── Architecture ............................. layer model, contracts
  ├── Runtime Platform ......................... ← built during M5 (this ADR's scope)
  │     ├── Event Bus .......................... canonical events + subscribers
  │     ├── Runtime Contract ................... docs/runtime-contract.md
  │     ├── Lifecycle .......................... ConversationService, RunContext, checkpoint
  │     └── Observability ...................... telemetry/logging/tracing subscribers
  ├── Qualification ............................ M5.5 runtime qualification
  └── Promotion ................................ M5.6 freeze + tag
  ```

  "Runtime Platform" is the canonical name for the Product Plane runtime subsystem
  (Event Bus, contracts, lifecycle, observability). The Runtime Constitution and
  this ADR govern the Runtime Platform specifically.

  ### 1. Three layers (Product Plane)

  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │  Business Layer — domain decisions & domain write ports   │
  │  Supervisor · Planner · Router · TaskService · MemoryService│
  │  · RetrievalService · DocumentService                       │
  └───────────────────────────────┬─────────────────────────────┘
                                  │ uses abstractions / hooks only
                                  ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Runtime Layer — graph, lifecycle, context, event bus           │
  │  LangGraph composition · RunContext · Checkpoint ·              │
  │  ConversationService lifecycle · Runtime Event Bus · subscribers│
  └───────────────────────────────┬─────────────────────────────┘
                                  │ uses service facades & drivers
                                  ▼
  ┌─────────────────────────────────────────────────────────────┐
  │  Infrastructure Layer — adapters & drivers                  │
  │  Postgres/SQLAlchemy · Vector index · LLM/Embedding clients │
  │  · Object storage · external APIs                           │
  └─────────────────────────────────────────────────────────────┘
  ```

  **Allowed dependency direction:** Business → Runtime (via declared hooks/interfaces) → Infrastructure.

  **Forbidden:** Infrastructure → Business, Infrastructure → Runtime internals (except through inversion), Business graph nodes → concrete Infrastructure or concrete domain service classes.

  ### 2. Layer membership (canonical map)

  | Layer | Responsibility | Examples (`backend/app/`) |
  |-------|----------------|---------------------------|
  | **Business** | Turn-level reasoning; agent contracts; sole writers to domain tables (ADR-0015, ADR-0020, ADR-0024) | `graph/supervisor.py`, `graph/planner.py`, `graph/router.py`, `graph/orchestration/*` (prompts, coerce, constants — **no** LangGraph wiring), `graph/memory_context.py`, `graph/retriever.py`, `graph/prompt_wire.py`, `services/task/`, `services/memory/`, `services/retrieval/`, `services/document/` |
  | **Runtime** | Graph topology, dispatch, turn lifecycle, execution context, checkpoint seam, **Runtime Event Bus** | `graph/conversation.py` (`build_graph`), `graph/routing.py`, `graph/checkpointer.py`, `services/conversation/`, `runtime/` (M5.4+ Event Bus + events), `runtime/subscribers/` (telemetry, logging, …), `schemas/run_context.py` |
  | **Infrastructure** | Technology adapters; no domain semantics | `db/`, `llm/`, `core/config.py`, LangGraph/Postgres saver driver usage inside checkpointer |

  **ConversationService** is Runtime: it is the HTTP→graph boundary and owns turn lifecycle (setup, stream, finalize, cancel). It **composes** Business services and the compiled graph; it does not encode routing or planning logic.

  **Execution nodes** (`memory_context`, `retriever`, `conversation`) are Business packaged as graph-callable functions. Their **bodies** remain frozen per milestone gates (M4 execution nodes unchanged in M5.2B); Runtime only changes **edges** around them.

  ### 3. Dependency rules (mandatory)

  | Rule | Rationale |
  |------|-----------|
  | **R1 — Business nodes are pure over ports** | Graph node factories (`make_*_node`) accept `LLMClient`, optional hooks/callbacks, and domain service interfaces — never `AsyncSession`, raw SQL, or env/config reads beyond what a port already encapsulates. |
  | **R2 — Composition root wires concretes** | `build_graph()`, `ConversationService`, and test fixtures are the only places that bind concrete `TaskService`, `MemoryService`, `RetrievalService`, telemetry recorders, and persistence hooks. |
  | **R3 — No Business → Infrastructure imports in graph agents** | `supervisor.py`, `planner.py`, `router.py` MUST NOT import `app.db`, `app.llm.factory`, or SQLAlchemy. LLM is injected; persistence is via hooks (see M5.3 `PlannerTaskPersistHook`). |
  | **R4 — Domain services are Business, not Infrastructure** | `TaskService`, `MemoryService`, etc. **may** use Infrastructure internally (SQLAlchemy sessions). External callers (graph nodes, API handlers) call the service — not the DB layer. |
  | **R5 — RunContext stays out of GraphState** | Execution metadata flows via LangGraph config / Runtime call path only (ADR-0014). Checkpoints remain domain working state. |
  | **R6 — Subscribers are non-blocking** | Event Bus subscriber failures (DB write, log sink, OTel export) MUST NOT fail user-visible turns (same class as task upsert/mark_done best-effort in M5.3). |
  | **R7 — Engineering Runtime boundary unchanged** | `builder_engine/` and Build Control Plane MUST NOT import `backend.app` (ADR-0023, ADR-0026). This ADR applies to the **Product Plane** agent runtime only. |
  | **R8 — Business never emits telemetry directly** | Business code MUST NOT call telemetry, tracing, structured logging subscribers, or `agent_steps` writers. Business exposes domain outcomes (GraphState partials, hooks). **Runtime** translates lifecycle boundaries into canonical events on the Event Bus and lets subscribers decide recording. Forbidden: `telemetry.record(...)` inside `planner.py` or any Business agent. |

  **Approved patterns:**

  ```text
  Planner  →  produces TaskRef  →  on_task_ref hook (optional)
  build_graph  →  hook → TaskService.upsert_from_task_ref(...)
  ConversationService  →  build_graph(..., task_service=...)  →  aget_state  →  mark_done
  ```

  **Rejected patterns:**

  ```text
  planner.py  →  from app.services.task import TaskService   # concrete in node
  retriever_node  →  AsyncSessionLocal()                        # infra in node body
  llm/litellm_client.py  →  app.graph.planner                   # infra → business
  GraphState  →  RunContext / agent_run_id                      # execution in checkpoint
  ```

  planner.py  →  telemetry.record(...) / agent_steps writer     # R8 violation
  GraphState  →  RunContext / agent_run_id                      # execution in checkpoint
  ```

  ### 4. Runtime as a product — PR and review discipline

  Every PR touching `backend/app/` MUST declare its **primary layer** in the description:

  ```text
  Layer: Business | Runtime | Infrastructure
  ```

  **Review order** (most important first):

  1. Layer placement — does this code belong in the declared layer?
  2. Public contracts — agent JSON, event payloads, hooks, extension points
  3. Event model — emission at Runtime boundary only (R8)
  4. Feature implementation — logic, tests, performance

  Milestone numbers (M5.1, M5.2, …) track delivery history; **layer + contract + event model** track architectural correctness.

  ### 5. Hook and port conventions

  | Concern | Business produces | Runtime wires | Persists via |
  |---------|-------------------|---------------|--------------|
  | Task from planner | `TaskRef` + `Plan.steps` | `PlannerTaskPersistHook` in `build_graph` | `TaskService` (Business) |
  | Memory ops | `MemoryOp` list in node return | node factory injects `MemoryService` | `MemoryService` |
  | Retrieval | query + filters in node | node factory injects `RetrievalService` | `RetrievalService` |
  | Run correlation | — | `RunContext` in LangGraph `configurable` | `agent_runs` (Runtime lifecycle) |
  | Runtime events | domain outcomes via hooks / node returns | Runtime Event Bus at composition root | subscribers (`agent_steps`, logs, OTel, UI) |

  Hooks are typed callables or small Protocols living in `graph/orchestration/` (Business-adjacent, graph-independent). They MUST NOT contain SQL or status-string domain rules — those stay in domain services.

  ### 6. Runtime Event Bus and canonical events (M5.4+)

  M5.4 primary deliverable is the **Runtime Event Bus** — not telemetry. Telemetry, logging, tracing, and future UI are **subscribers**.

  ```text
  Runtime composition  →  emit(event)  →  Event Bus  →  subscribers
                              │              ├── AgentStepsSubscriber → agent_steps
                              │              ├── LoggingSubscriber → structured logs
                              │              └── (future) OpenTelemetrySubscriber, TracingUI
                              │
                              └── Event Bus does not know what subscribers do
  ```

  **Canonical event vocabulary** (stable across storage backends):

  | Event | When | Key payload fields |
  |-------|------|-------------------|
  | `RunStarted` | Turn setup complete, graph invocation begins | `agent_run_id`, `conversation_id`, `trace_id` |
  | `NodeStarted` | Before node execution | `agent`, `phase` (`plan` \| `implement`), truncated input snapshot |
  | `NodeCompleted` | After successful node | `agent`, `duration_ms`, truncated output snapshot |
  | `NodeFailed` | Node raised or contract error path | `agent`, `error`, `duration_ms` |
  | `RouteSelected` | After router (or dispatch read) | `route`, `errors` (orchestration errors if any) |
  | `TaskPersisted` | After successful task hook / upsert | `task_id`, `title`, `status` |
  | `RunCompleted` | Turn finalize | `agent_run_id`, `status` (`done` \| `error` \| `cancelled`), `task_id` optional |

  **Typical sequence:**

  ```text
  RunStarted → NodeStarted → … → RouteSelected → TaskPersisted → NodeCompleted → RunCompleted
  ```

  Emission happens in **Runtime** (composition root, lifecycle, node wrappers) — never via ad-hoc calls from Business agents (R8). Onboarding contract: `docs/runtime-contract.md` (completed at M5.6).

  ### 7. M5 closure roadmap

  Remaining M5 work **qualifies the runtime** — it does not add product features:

  | Milestone | Focus |
  |-----------|-------|
  | **M5.4 — Runtime Event Bus** | Event Bus, canonical events, RunContext in config, initial subscribers (`agent_steps`, logging) |
  | **M5.5 — Runtime Qualification** | E2E integration, eval harness, KPI benchmark, dogfood, regression suite |
  | **M5.6 — Promotion** | Freeze, `docs/m5-promotion.md`, **`docs/runtime-contract.md`**, knowledge mirror, tag `m5-complete` |

  M5.4 MUST NOT begin until this ADR is accepted.

- Consequences:
  - ThesisOS Product Plane is an **Agent Runtime Framework** — layer, contract, and event reviews precede feature reviews.
  - M5.4 lands the Event Bus in `backend/app/runtime/`; telemetry becomes a subscriber, not the core abstraction.
  - PR template requires explicit layer declaration (`.github/pull_request_template.md`).
  - Slight indirection at composition root (hooks, node wrappers) — accepted; prevents graph agent rot.
  - **Amends ADR-0027 §4.1 wording:** task upsert is triggered by the planner **hook wired in `build_graph`**, not by planner importing `TaskService` directly. Semantics unchanged: `TaskRef.id == tasks.id`.
  - `docs/runtime-contract.md` becomes the onboarding doc for new agents (frozen at M5.6).

- Alternatives considered:
  - **Defer boundaries until M12** — rejected; cross-imports compound every milestone.
  - **Single "services" layer (no Runtime/Business split)** — rejected; obscures graph lifecycle vs domain reasoning.
  - **Put TaskService in Runtime** — rejected; task rows are domain state with Business ownership (like memories/documents).
  - **Embed events in GraphState** — rejected; violates ADR-0007/0014; events are execution telemetry, not domain reasoning state.
  - **Telemetry-first (no Event Bus)** — rejected; couples Runtime to storage; blocks future UI/replay/OTel subscribers without refactoring Business agents.
  - **OpenTelemetry only, no canonical event enum** — rejected; couples M5 to a vendor shape; internal event model maps to OTel via subscriber later.

- References: ADR-0007, ADR-0014, ADR-0015, ADR-0020, ADR-0024, ADR-0026, ADR-0027; `docs/runtime-contract.md`; `backend/app/graph/orchestration/task_persistence.py`; `plans/m5-tool-router-plan.md` (M5.4–M5.6); `docs/superpowers/specs/2026-06-25-thesisos-m5-tool-router-orchestration-design.md`.
