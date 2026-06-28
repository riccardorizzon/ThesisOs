# ThesisOS Agent Runtime Contract

> **Status:** Draft — scaffold for M5.6 promotion. Architectural invariants of the
> Runtime Platform live in `docs/runtime-constitution.md` (C1–C8); normative
> enforcement rules in `decisions/ADR-0030-agent-runtime-layer-boundaries.md`. This
> document is the **onboarding contract** for anyone adding agents, subscribers, or
> runtime extensions. Complete and freeze at **M5.6 — Promotion**.

---

## 1. What this runtime is

The ThesisOS Product Plane runtime is the **ASEP Runtime Platform** — a subsystem
of ASEP (ADR-0026 unchanged; taxonomy in ADR-0030 §0), specialized for thesis
workflows, not a linear RAG chatbot. A `/chat` turn is a **run**: orchestration
agents plan and route, execution agents implement, Runtime owns lifecycle and
emits events, Infrastructure provides adapters.

Read this document **before** adding a new agent, route, subscriber, or graph node.

---

## 2. Layer boundaries

Dependency direction is strict:

```text
Business  →  Runtime  →  Infrastructure
```

| Layer | Owns | Must not |
|-------|------|----------|
| **Business** | Domain reasoning, agent contracts, domain write ports (`TaskService`, `MemoryService`, …) | Import DB/LLM factories in graph agents; call telemetry/logging/tracing directly (R8) |
| **Runtime** | Graph topology, turn lifecycle, `RunContext`, checkpoint seam, **Runtime Event Bus**, subscribers | Encode domain rules (routing/planning logic belongs in Business nodes) |
| **Infrastructure** | Postgres, vector index, LLM/embed clients, object storage | Import Business or Runtime modules |

**Composition roots** (where concretes are wired): `build_graph()`, `ConversationService`, test fixtures.

Canonical map: ADR-0030 §2.

---

## 3. Event model

Runtime emits a **canonical event vocabulary** on the Event Bus. Business code
does not choose how events are stored — subscribers do.

### Event types

| Event | Emitted when | Key payload |
|-------|--------------|-------------|
| `RunStarted` | Graph invocation begins | `agent_run_id`, `conversation_id`, `trace_id` |
| `NodeStarted` | Before node execution | `agent`, `phase`, truncated input |
| `NodeCompleted` | Node success | `agent`, `duration_ms`, truncated output |
| `NodeFailed` | Node error | `agent`, `error`, `duration_ms` |
| `RouteSelected` | After routing decision | `route`, orchestration `errors` |
| `TaskPersisted` | Task hook / upsert success | `task_id`, `title`, `status` |
| `RunCompleted` | Turn finalize | `agent_run_id`, `status`, optional `task_id` |

### Typical sequence

```text
RunStarted
  → NodeStarted (supervisor) → NodeCompleted
  → NodeStarted (planner) → TaskPersisted → NodeCompleted
  → NodeStarted (router) → RouteSelected → NodeCompleted
  → … execution nodes …
RunCompleted
```

### Stability guarantee (M5.6+)

- Event **names and ordering semantics** are stable within a major milestone tag.
- Adding new event types is additive; renaming or removing events requires an ADR.
- Payload fields may gain optional keys; required keys are not removed without ADR.

Implementation: `backend/app/runtime/events.py` (M5.4).

---

## 4. Runtime API

### 4.1 Runtime Event Bus (M5.4)

The primary M5.4 deliverable is the **Event Bus**, not telemetry.

```text
Runtime composition  →  emit(event)  →  Event Bus  →  subscribers
```

| Component | Layer | Role | Status |
|-----------|-------|------|--------|
| `RuntimeEvent` / `EventType` | Runtime | Event contract + vocabulary | M5.4A ✅ |
| `RuntimeSubscriber` / `RuntimeEventEmitter` | Runtime | Consumer/producer Protocols | M5.4A ✅ |
| `RuntimeEventBus` | Runtime | Fan-out to subscribers; no storage logic | M5.4B ✅ |
| `AgentStepsSubscriber` | Runtime | Maps node terminal events → `agent_steps` table | M5.4C ✅ |
| `LoggingSubscriber` | Runtime | Structured logs | M5.4C ✅ |
| *(future)* `OpenTelemetrySubscriber` | Runtime | OTel export | — |
| *(future)* `TracingUISubscriber` | Runtime | Debug / replay UI | — |

The Event Bus **does not know** what subscribers do with events.

### 4.2 Turn lifecycle (`ConversationService`)

| Phase | Runtime responsibility |
|-------|------------------------|
| Setup | Persist user message, open `agent_run`, build `RunContext` |
| Stream | `build_graph` → `astream` → SSE mapping |
| Finalize | Close `agent_run`; `RunCompleted`; optional `mark_done` via Business port |

### 4.3 Graph composition (`build_graph`)

| Extension | Where to wire |
|-----------|---------------|
| New orchestration node | `conversation.py` edges + `contracts/agents/<name>.json` |
| New route | `orchestration/constants.py`, `routing.py`, router contract |
| Task persistence hook | `PlannerTaskPersistHook` in `build_graph` — not inside planner |
| Event instrumentation | Node wrappers in Runtime — not inside Business node bodies |

### 4.4 RunContext (ADR-0014)

Passed via LangGraph `configurable`. **Never** in `GraphState` checkpoint.

---

## 5. Extension points

### Adding a new Business agent

1. Freeze contract: `contracts/agents/<name>.json` (`reads_state`, `writes_state`, errors).
2. Implement `make_<name>_node(...)` with injected ports only (R1, R3).
3. Register in `build_graph()` — Runtime layer change.
4. Add Event Bus wrappers for `NodeStarted` / `NodeCompleted` at composition root.
5. Do **not** change `GraphState` fields without ADR-0007 amendment.

### Adding a new Event Bus subscriber

1. Implement subscriber interface in `backend/app/runtime/subscribers/`.
2. Register in composition root (`ConversationService` or `build_graph` factory).
3. Subscriber failure must be non-blocking (R6).

### Adding a new domain write port

Follow ADR-0015 pattern: sole writer service in Business layer; graph nodes receive injected interface.

---

## 6. Stability guarantees (M5.6 freeze)

| Surface | Guarantee |
|---------|-----------|
| `GraphState` fields | Frozen (ADR-0007) unless new ADR |
| `/chat` SSE shape | Stable external contract |
| Event model names | Stable per `m5-complete` tag |
| Layer dependency rules | R1–R8 (ADR-0030) |
| M4 execution node bodies | Frozen unless bugfix with evidence |

---

## 7. Review order (platform PRs)

For Product Plane PRs touching the agent runtime, review **in this order**:

1. **Layer** — does the code belong where it was placed?
2. **Public contracts** — agent JSON, event payloads, hooks
3. **Event model** — emission at Runtime boundary, not in Business
4. **Feature implementation** — logic, tests, performance

---

## References

- `docs/runtime-constitution.md` — **architectural invariants (C1–C8)**
- `docs/architecture-decision-checklist.md` — per-PR review gate
- `decisions/ADR-0030-agent-runtime-layer-boundaries.md`
- `decisions/ADR-0027-multi-agent-graph-topology.md`
- `decisions/ADR-0014-run-context-separation.md`
- `decisions/ADR-0007-state-contract.md`
- `knowledge/architecture/graph.md`
- `onboarding/how-to-add-an-agent.md`
- `plans/m5-tool-router-plan.md` — M5.4 Event Bus, M5.5 Qualification, M5.6 Promotion
