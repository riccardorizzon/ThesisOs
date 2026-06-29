# Roadmap (M0 → M18)

> **Platform context (ADR-0026):** This table is the **Product Track** (M0–M18) within **ASEP** (Adaptive Software Engineering Platform). Build-time platform evolution (MB-series) is tracked separately on the **Platform Track** — see `docs/platform/era-model.md` and `decisions/ADR-0026-platform-model-terminology.md`.
>
> Sources: `docs/superpowers/specs/2026-06-23-thesisos-m0-foundations-design.md` §18 (roadmap alignment); `docs/architecture.md`; `contracts/openapi/openapi.yaml` (`x-milestone`); `contracts/agents/*.json` (`milestone`); `contracts/events/events.json`.

The roadmap is a sequence of **vertical slices**. Each milestone delivers one
usable capability end-to-end against frozen contracts and passes a promotion gate
(ADR-0010) before the next begins.

## Status legend
- ✅ complete & promoted   🟢 functionally complete, gate partially open   🟡 planning (spec/ADRs drafted, no implementation)   ⬜ not started

| M | Name | Status | Headline deliverable | Key contracts wired |
|---|------|--------|----------------------|---------------------|
| **M0** | Foundations | ✅ | Architecture, contracts, schema, infra, deployed `/health` shell | All contracts frozen; ADR-0001..0010 |
| **M1** | Conversation System | ✅ | Streaming chat: `POST /chat` → LangGraph (1 node) → Gemini → SSE → React | `/chat`, `GraphState` (messages only), `RunContext`, checkpointer; ADR-0011..0014 |
| **M2** | Memory | ✅ | Memory foundation: DB, Service, API, Admin UI, `memory_context_node` | `/memory`, ADR-0015/0017/0018; tag `m2-complete` |
| **M3** | Ingestion | ✅ | Document upload → parse → chunks + events; tag `m3-complete` | `/upload`, `/documents`, events |
| **M4** | Retrieval | ✅ | Embed + hybrid search + retriever; promoted tag `m4-complete` | `/search`, `retriever`, ADR-0024 |
| **M5** | Tool Router / Orchestration | ✅ | Orchestrated runtime: supervisor/planner/router + conditional routing + TaskService + Runtime Event Bus/observability. Promoted — `m5-complete` @ `bf12c13`, live dogfood B_lat=9.89s/B_ground=6.54s | ADR-0027/0030, `contracts/agents/*`, `docs/runtime-contract.md` (Frozen v1) |
| **M6** | Writing Workspace | ✅ | Writer capability drafts grounded chapters/sections; versioned chapter store + `/chapters` + Workspace UI. Promoted — `m6-complete` / `m6-main` @ `79fb52a`, live dogfood B_write=63.6s | ADR-0031/0032/0033, `writer` route, `/chapters`, `docs/m6-promotion.md` |
| **M7** | Grounding Engine | 🟡 | Provenance, evidence, confidence, validation hooks, bibliography — citations as one output of a general traceability system (design phase) | `/citations`, `/bibliography`, `citation` agent, Grounding Engine port |
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

## Post-M18 horizon: generalizing to a Knowledge OS (uncommitted)

> Source: 2026-06-25 vision brief. **Not scheduled** — no committed milestones, no
> frozen scope. Listed only so the direction stays traceable, per `vision.md`
> *Two-layer vision*.

M0–M18 deliver the **thesis instance**. Once that instance proves the
acquire → organize → retrieve → produce pipeline, the *same architecture* can be
generalized into a domain-agnostic **Knowledge OS**. The generalization axes
(each a potential future milestone band — none committed):

| Axis | Thesis instance today | Generalized Knowledge OS |
|------|-----------------------|--------------------------|
| Domain model | `chapters` / outline tree | generic `project` / `section` model, domain-pluggable |
| Output templates | academic citations (APA7/MLA/Chicago) | per-domain output + citation templates |
| Language | Italian-first embeddings | multi-language embedding strategy |
| Tenancy | single-user, no auth | optional multi-tenant for team / enterprise domains |
| Target domains | academic thesis | research, legal, consulting, technical docs, software, enterprise KM |

**Discipline:** this stays a horizon, not a backlog. It is implemented only if and
when the thesis instance is complete *and* a concrete second domain is chosen —
which would then get its own frozen spec + promotion gates like any milestone
(ADR-0001, ADR-0010).

## Caveats / unknowns
- M13 (Research), M14 (NotebookLM-like), M17 (Voice) are named in the roadmap but
  have **no detailed scope** in the repository yet. **M2 spec is frozen** (`docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md`); M3+ still need specs before implementation.
