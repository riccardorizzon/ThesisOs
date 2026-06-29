# Agents — overview

> Sources: `docs/architecture.md` §2/§6, M0 spec §10, `contracts/agents/*.json`, `.cursor/skills/orchestrate-builders/SKILL.md`, `plans/builder/STATE.yaml`, `backend/app/db/models.py` (`agent_steps.phase`).

ThesisOS has **two distinct populations of agents**. Do not confuse them.

## 1. Builder agents (Cursor) — build-time only

The team that **writes** ThesisOS. Coordinated by the `orchestrate-builders` skill
(explorers → implementers → integrators in isolated git worktrees, a shared
`STATE.yaml` bus, and wave sync barriers). They follow the **AgentOS loop**
(`development/workflow.md`). **No deployed ThesisOS code path calls them** (ADR-0002).

| File | Role |
|------|------|
| `ceo-agent.md` | Vision, scope, final approval |
| `product-manager-agent.md` | Milestone slicing, roadmap, scope guard |
| `architect-agent.md` | Design specs, ADRs, freeze contracts |
| `planner-agent.md` | Turn a frozen spec into a TDD task plan / work packets |
| `backend-agent.md` | Implement Python/FastAPI/LangGraph |
| `frontend-agent.md` | Implement Next.js/React |
| `qa-agent.md` | Quality assurance over the loop (also a runtime phase, M10) |

## 2. Runtime agents (LangGraph nodes) — the product's orchestration

Nodes in the `StateGraph(GraphState)` that **run inside** ThesisOS. Designed in M0
(contracts frozen), wired milestone by milestone. Target hierarchy:

```text
Supervisor → Planner → Router → { Retriever · Writer · Critic · Citation · Memory · Document }
```

Each has a frozen I/O contract in `contracts/agents/<name>.json` declaring
`reads_state` / `writes_state` / `errors` / `state_mutations`.

| Runtime agent | Milestone | Contract | Documented here |
|---------------|-----------|----------|-----------------|
| Supervisor | M5 | `supervisor.json` | this file (below) |
| Planner | M5 | `planner.json` | this file (below) + `planner-agent.md` (builder sense) |
| Router | M5 | `router.json` | this file (below) |
| Retriever | M4 | `retriever.json` | `retrieval-agent.md` |
| Writer | M6 | `writer.json` | `writer-agent.md` |
| Critic | M9 | `critic.json` | `critic-agent.md` |
| Citation | M7 | `citation.json` | `citation-agent.md` |
| Memory | M2 | `memory.json` | `memory-agent.md` |
| Document | M3 | `document.json` | this file (below) |

> Per-file docs exist for the runtime agents in the requested set. The three not
> given their own file — **Supervisor, Router, Document** — are documented here so
> nothing is lost.

### Supervisor (M5) — `contracts/agents/supervisor.json`
Reads `messages, task`; writes `plan, route`; error `no_objective`; mutations
`plan=set, route=set`. Top of the hierarchy: turns the user objective into a plan
and a route.

### Router (M5) — `contracts/agents/router.json`
Reads `plan, messages`; writes `route`; error `no_route`; mutation `route=set`.
Picks which specialized agent handles the next step.

### Document (M3) — `contracts/agents/document.json`
Reads `task`; writes `errors`; errors `parse_failed, unsupported_format`; mutation
`errors=append`. Drives ingestion/parsing; the contract exists in M0 though
implemented in M3.

## Status today (M5)
The orchestrated graph is wired (`backend/app/graph/conversation.py`):
`supervisor → planner → router → [conditional] → memory_context → (retriever) →
conversation`. Supervisor/Planner/Router (M5.1), conditional routing (M5.2),
TaskService persistence via planner hook (M5.3), and the Runtime Event Bus +
observability subscribers (M5.4) are implemented and qualified (M5.5).

The runtime is **observable**: each node execution emits canonical events
(`app/runtime/events.py`) through the Event Bus to subscribers — `AgentStepsSubscriber`
writes `agent_steps`, `LoggingSubscriber` logs. Business agents never emit
(ADR-0030 R8); emission is wrapped at the composition root. Writer/Critic/Citation
remain **designed (contract frozen), not yet implemented** (M6/M9/M7).

## Standard agent doc shape
Every per-agent file defines: **Mission · Responsibilities · Inputs · Outputs ·
Allowed actions · Forbidden actions · Dependencies · Promotion criteria · Failure
modes**.
