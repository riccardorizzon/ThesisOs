# Roadmap (M0 → M18)

> Sources: `docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md` §18 (roadmap alignment); `docs/architecture.md`; `contracts/openapi/openapi.yaml` (`x-milestone`); `contracts/agents/*.json` (`milestone`); `contracts/events/events.json`.

The roadmap is a sequence of **vertical slices**. Each milestone delivers one
usable capability end-to-end against frozen contracts and passes a promotion gate
(ADR-0010) before the next begins.

## Status legend
- ✅ complete & promoted   🟢 functionally complete, gate partially open   ⬜ not started

| M | Name | Status | Headline deliverable | Key contracts wired |
|---|------|--------|----------------------|---------------------|
| **M0** | Foundations | ✅ | Architecture, contracts, schema, infra, deployed `/health` shell | All contracts frozen; ADR-0001..0010 |
| **M1** | Conversation System | ✅ | Streaming chat: `POST /chat` → LangGraph (1 node) → Gemini → SSE → React | `/chat`, `GraphState` (messages only), `RunContext`, checkpointer; ADR-0011..0014 |
| **M2** | Memory | 🟡 | Memory foundation: DB, Service, API, Admin UI; graph node pending | `/memory`, ADR-0015/0017/0018; `memory_context_node` Phase 6 |
| **M3** | Ingestion | ⬜ | Document upload → parse (Docling/PyMuPDF/OCR) → chunks | `/upload`, `/documents`, `/summarize`, `document` agent, `DocumentUploaded`/`ChunkCreated` |
| **M4** | Retrieval | ⬜ | Hybrid search over embeddings; pgvector index strategy | `/search`, `retriever` agent |
| **M5** | Tool Router / Orchestration | ⬜ | Supervisor → Planner → Router wired; multi-node graph | `supervisor`/`planner`/`router` agents |
| **M6** | Writing | ⬜ | Writer agent drafts chapters from plan + context | `/chapters`, `writer` agent |
| **M7** | Citations | ⬜ | CSL-JSON → APA7/MLA/Chicago; bibliography | `/citations`, `/bibliography`, `citation` agent |
| **M8** | Outline | ⬜ | Outline/chapter tree management | `/outline`, `ChapterCreated` event |
| **M9** | Critic | ⬜ | Critic agent reviews drafts (hallucination/redundancy) | `critic` agent, `CritiqueCompleted` event |
| **M10** | QA | ⬜ | Quality-assurance phase/agent over the loop | `qa` phase (see `agent_steps.phase`) |
| **M11** | GCP Hardening | ⬜ | Full tracing/exporters, cold-start, durable jobs, instance sizing | telemetry, jobs durability |
| **M12** | Multi-Agent | ⬜ | Full Supervisor-led multi-agent execution | full agent graph + RunContext per-agent accounting |
| **M13** | Research | ⬜ | Research mode | — |
| **M14** | NotebookLM-like | ⬜ | NotebookLM-style experience | — |
| **M15–M16** | Editable KB + Mem0 | ⬜ | Editable knowledge base + Mem0-style auto-extraction | ADR-0003 deferral lands here |
| **M17** | Voice | ⬜ | Voice interaction | — |
| **M18** | Autonomous Assistant | ⬜ | Self-improving autonomous research assistant | full AgentOS loop |

## The "usable product" line

> "M0–M6 is already a usable product for a real thesis." — M0 spec §18

M1–M6 (chat → memory → ingestion → retrieval → tool router → writing) is the
minimum slice that lets the user actually write a thesis with grounded help.
M7–M11 make it trustworthy; M12–M18 make it autonomous.

## Roadmap mechanics

- **Seam-first.** M1 froze the orchestration architecture (LangGraph + checkpointer
  + `ConversationService` + SSE + RunContext). Later milestones *extend the graph*
  (add nodes/state usage), they do not rewrite the `/chat` seam (M1 spec §1, §10).
- **Milestone tags on contracts.** Every deferred OpenAPI path carries
  `x-milestone`; every agent contract carries a `milestone`; every event carries a
  `milestone`. Use these to find exactly what a milestone must implement.
- **Open questions are scheduled, not lost.** E.g. the pgvector index/partition
  strategy is explicitly deferred to M2/M4 (M0 spec §19). See
  `context/open-questions.md`.

## Caveats / unknowns
- M13 (Research), M14 (NotebookLM-like), M17 (Voice) are named in the roadmap but
  have **no detailed scope** in the repository yet. **M2 spec is frozen** (`docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`); M3+ still need specs before implementation.
