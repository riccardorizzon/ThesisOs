# ThesisOS — Knowledge Operating System

> The operational knowledge base for ThesisOS. A newly spawned autonomous agent
> should be able to read this directory and understand the entire project without
> reading the whole repository.

**Status of truth.** This directory is a *consolidated, referenced mirror* of the
repository. It is NOT the source of truth. The source of truth is, in order:

1. **Frozen design specs** — `docs/superpowers/specs/*` (Architect-frozen).
2. **ADRs** — `decisions/ADR-*.md` (frozen architecture decisions).
3. **Contracts** — `contracts/` (OpenAPI, agent I/O, DB schema, events).
4. **Code** — `backend/`, `frontend/`, `infra/`.

If this knowledge base disagrees with any of the above, the source wins. Every
file here cites its sources so you can verify.

## How to read this (for a new agent)

Read in this order:

1. `context/current-state.md` — where the project is **right now**.
2. `memory/project-memory.md` — the durable model (architecture, frozen contracts, ADRs, debt).
3. `project/vision.md` + `project/roadmap.md` — what we are building and in what order.
4. `architecture/system-overview.md` — the runtime stack.
5. `development/workflow.md` + `development/promotion-gates.md` — how work moves.
6. `context/next-actions.md` — the prioritized backlog (next 100 tasks).

## Map

| Folder | Contents |
|--------|----------|
| `project/` | vision, mission, roadmap, milestones |
| `architecture/` | system overview, backend, frontend, database, graph, memory, infrastructure |
| `contracts/` | API, GraphState, RunContext, database contracts |
| `agents/` | per-agent operational docs (builder + runtime agents) |
| `development/` | coding standards, promotion gates, workflow, branching, testing, AgentOS loop |
| `decisions/` | architectural / technical / rejected decisions (ADR-derived) |
| `memory/` | project memory, lessons learned, known risks, recurring problems |
| `onboarding/` | how the system works, how to add an agent/tool/milestone |
| `context/` | current state, completed work, next actions, open questions |
| `KNOWLEDGE-HEALTH-REPORT.md` | gaps, contradictions, risks, recommendations |

## One-paragraph summary

ThesisOS is a **single-user** research and thesis-writing **AgentOS**: chat,
editable long-term memory, document ingestion (PDF/EPUB/DOCX), RAG, citation
management, outline/chapter management, and multi-agent orchestration — built on
**Google Cloud from day one** (Cloud Run + Cloud SQL Postgres/pgvector), with the
**runtime LLM = Vertex AI (Gemini + multilingual embeddings)** behind a LiteLLM
seam, and **Cursor agents as the build-time team** (never a runtime dependency).
Development is **Contract-First** and **milestone-gated** (M0…M18); each milestone
adds one vertical slice against frozen contracts. **M0 (Foundations) is complete
and deployed; M1 (Conversation System) is functionally complete and validated
locally against real Vertex/Gemini — Cloud Run promotion of M1 is the open item.**
