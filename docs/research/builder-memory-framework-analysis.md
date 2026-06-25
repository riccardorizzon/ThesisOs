# Builder Memory — External Framework Analysis

- **Date:** 2026-06-24
- **Status:** Approved (Architect 2026-06-24) — hybrid custom indexer selected; Mem0 rejected V1
- **Scope:** Framework discovery for **BuilderOS** retrieval layer only (Cursor build-time agents). **Not** ThesisOS runtime memory (M2 / ADR-0003).
- **Authors:** Builder Architect session
- **Trigger:** Clarify whether “Tencent memory” means TencentDB Agent Memory, DB-GPT, or another product before integration.

---

## 1. Executive summary

### 1.1 What we are actually building

Builder Memory is a **retrieval accelerator** for Cursor builder agents (Architect, Planner, Backend, Frontend, QA, Critic). It indexes **static repository knowledge** (`knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/`) plus optional **episodic builder artifacts** (lessons learned, task outcomes, failure analyses). It must **never** become the source of truth.

This is **not** the same problem as ThesisOS M2 runtime memory (Postgres `memories` table, user-facing, ADR-0003). M2 is domain truth for the product; Builder Memory is a **cache/index** for developers.

### 1.2 Repository finding: no framework is pre-selected

A full-text search of this repository finds **no existing integration** with TencentDB Agent Memory, DB-GPT, Letta, Mem0, or Zep. References to Mem0 appear only as **deferred runtime scope** (M15–M16, ADR-0003 rejection of Mem0 in core). There is no `builder-memory` code path today.

### 1.3 “Tencent memory” disambiguation

| Name | What it is | Relation to DB-GPT |
|------|------------|-------------------|
| **TencentDB Agent Memory** | Standalone agent memory service (L0–L3 pipeline, SQLite/BM25 default, optional TCVDB). GitHub: `TencentCloud/TencentDB-Agent-Memory`. | **Independent project.** Not part of DB-GPT. |
| **DB-GPT** | Full multi-agent application framework (`eosphoros-ai/DB-GPT`) with embedded `AgentMemory`, RAG, AWEL flows, serve layer. | **Different product.** Memory is one module inside a large framework. |
| **DB-GPT Memory** | `SensorMemory` / `ShortTermMemory` / `LongTermMemory` / `HybridMemory` + `GptsMemory` for conversation/plan storage. | Submodule of DB-GPT; pulling it in typically means adopting DB-GPT agent runtime. |

**Conclusion:** If the intent was “Tencent memory,” the likely target is **TencentDB Agent Memory** (v1.0.0, June 2026), **not** DB-GPT. They should be evaluated separately.

### 1.4 Recommendation (preview)

| Tier | Recommendation | Rationale |
|------|----------------|-----------|
| **Primary** | **Hybrid: custom corpus indexer + lightweight episodic store** | Best fit for “filesystem is source of truth” + indexed markdown/YAML. No framework forces conversation-derived truth over git. |
| **External episodic (optional)** | **Mem0 self-hosted (Apache-2.0)** | If a branded external memory product is required for builder session recall only — smallest integration surface, broad Python SDK. |
| **Do not adopt as primary** | TencentDB Agent Memory, DB-GPT, Letta, Zep/Graphiti as the **corpus** layer | Optimized for conversational/persona memory or full agent runtimes; high coupling, wrong authority model, or license/ops risk. |

Full comparison and decision matrix below. **No implementation until this document is approved.**

---

## 2. Evaluation criteria (ThesisOS-specific)

| Criterion | Weight | Builder Memory requirement |
|-----------|--------|---------------------------|
| **Authority model** | Critical | Retrieval-only; filesystem wins on conflict |
| **Corpus indexing** | Critical | Index markdown/YAML from `knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/`, `STATE.yaml`, ADRs, promotion reports |
| **Runtime isolation** | Critical | Must not touch ThesisOS backend graph, M2 `MemoryService`, or frozen contracts |
| **Agent integration** | High | HTTP or Python library callable from Cursor agent prompts / orchestration skill |
| **Maintenance** | High | Re-index on git changes; clear staleness detection |
| **Complexity** | High | Minimal moving parts; no second agent runtime |
| **Licensing** | Medium | Prefer Apache-2.0 / MIT; avoid unclear licenses in production path |
| **Operational cost** | Medium | Local-first; no mandatory SaaS for build loop |

---

## 3. Framework profiles

### 3.1 TencentDB Agent Memory

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | 4-tier pipeline: L0 Conversation → L1 Atomic facts → L2 Scenario blocks → L3 Persona. Symbolic short-term memory (Mermaid compression). v1.0+ is standalone Gateway + HTTP v2 API + TS/Python SDKs. |
| **Storage** | Default SQLite + BM25; optional Tencent Cloud Vector DB (TCVDB). Redis HA in service mode. |
| **Retrieval** | Layered drill-down (symbol → scenario index → raw text). BM25 + optional vectors. Designed for **session-derived** memory, not git corpus mirroring. |
| **Agent integration** | OpenClaw/Hermes plugins; generic HTTP v2; `local` vs `client` modes. Docker images available. |
| **Maintenance** | Pipeline workers (L1/L2/L3 extraction), timer scanners, async pipelines — **opinionated lifecycle** for conversation distillation. |
| **Complexity** | High for our use case. TypeScript-heavy service; extraction pipelines assume ongoing agent dialogue. |
| **Licensing** | GitHub shows **“Other (NOASSERTION)”** — not Apache/MIT. Legal review required before adoption. |
| **Operational cost** | Self-host possible (Docker); LLM API key required for extraction pipelines. TCVDB is cloud-cost optional. |

**Fit for Builder Memory:** **Poor as corpus indexer.** Good at compressing tool logs and distilling user personas — orthogonal to “index ADRs and contracts.” Risk of **memory authority inversion** (distilled L2/L3 treated as truth over `decisions/ADR-*.md`).

---

### 3.2 DB-GPT (full framework)

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | 6-package monorepo: core, serve (REST), client, app, ext, accelerator. Agents, RAG, AWEL workflows, datasource connectors. |
| **Storage** | Pluggable via `dbgpt_ext/storage` — Chroma and others. `LongTermMemory` writes to vector store from `MemoryFragment`. |
| **Retrieval** | `read_memories` / `write_memories` on `ConversableAgent`; hybrid memory with sensory → short → long transfer; `TimeWeightedEmbeddingRetriever`. |
| **Agent integration** | **Replaces** much of your stack — DB-GPT agents, serve layer, flows. Not a drop-in retrieval library. |
| **Maintenance** | Large upstream surface; version pinning across packages; Chinese/English docs split. |
| **Complexity** | **Very high.** Adopting DB-GPT for “memory only” means fighting the framework boundary. |
| **Licensing** | MIT (DB-GPT). |
| **Operational cost** | Full stack deployment (serve + storage + models); overkill for BuilderOS. |

**Fit for Builder Memory:** **Reject.** Violates “memory is NOT part of ThesisOS runtime” and “retrieval only” — DB-GPT is an application platform, not a sidecar indexer.

---

### 3.3 DB-GPT Memory module (in isolation)

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | `AgentMemory` = `Memory` + `GptsMemory`. Four memory structures + hybrid consolidation. |
| **Storage** | In-process fragments + vector store for long-term. `GptsMemory` holds conversation/plan strings. |
| **Retrieval** | Observation-triggered read from long-term; merge with short-term for LLM context. |
| **Agent integration** | Requires DB-GPT `ConversableAgent` subclassing — not standalone HTTP service. |
| **Maintenance** | Coupled to DB-GPT release cycle; no independent v2 Gateway. |
| **Complexity** | Medium within DB-GPT; **high** to extract without the rest of the framework. |
| **Licensing** | MIT (as part of DB-GPT). |
| **Operational cost** | Low if embedded — but extraction cost is framework adoption. |

**Fit for Builder Memory:** **Reject as external integration.** The module is not published as a standalone package. Copying code creates a fork maintenance burden with no clear win over a 200-line indexer.

---

### 3.4 Letta (formerly MemGPT)

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | **Full agent runtime** with OS-style tiers: core (editable blocks), recall, archival. Agent self-manages memory via tool calls. |
| **Storage** | PostgreSQL-backed; memory blocks in agent state. |
| **Retrieval** | Agent-driven paging between tiers — memory is part of the agent loop, not a sidecar. |
| **Agent integration** | You run **Letta agents**, not Cursor builders with a memory plug-in. Conversations API (2026) for shared memory across parallel agents. |
| **Maintenance** | Self-host requires Postgres + ops; cloud free tier (~3 agents). |
| **Complexity** | **High coupling** — second agent runtime parallel to Cursor/AgentOS orchestration. |
| **Licensing** | Apache-2.0. |
| **Operational cost** | Cloud per-second tool pricing or self-host VM (~$5–10/mo). |

**Fit for Builder Memory:** **Reject.** Conflicts with BuilderOS orchestration (`orchestrate-builders` skill, `STATE.yaml`, worktrees). Letta wants to *be* the agent executor.

---

### 3.5 Mem0

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | Memory layer: extract facts from conversations → vector + graph (Pro) + KV. Plugs in front of any LLM call. |
| **Storage** | 20+ vector backends (self-host); managed cloud (SOC 2, HIPAA options). |
| **Retrieval** | Semantic + keyword; entity linking; ~200ms p95 cited. Strong **episodic** recall; weaker as deterministic doc mirror. |
| **Agent integration** | Python/JS SDK; LangChain/LlamaIndex/CrewAI adapters; minimal code to `add`/`search`. |
| **Maintenance** | Active community (~48k+ GitHub stars). Cloud-first product velocity; self-host supported. |
| **Complexity** | **Low** for episodic memory. Medium if used as full doc RAG (not its sweet spot). |
| **Licensing** | Apache-2.0 (open source). |
| **Operational cost** | Free self-host; cloud from $0 → $19/mo Starter → $249/mo Pro (graph features). |

**Fit for Builder Memory:** **Good for episodic builder memory only** (lessons learned, task outcomes, failure analyses). **Poor as sole corpus indexer** — auto-extraction can diverge from git truth; no native “index this repo path on commit” semantics without custom wrappers.

**ThesisOS note:** ADR-0003 explicitly defers Mem0 for **runtime** user memory to M15–M16. Using Mem0 for **builder-only** sidecar does not violate ADR-0003 if boundaries are documented in a new ADR.

---

### 3.6 Zep / Graphiti

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | **Temporal knowledge graph** (Graphiti engine, Apache-2.0). Bi-temporal facts (`valid_from` / `valid_to`). Zep Cloud is managed wrapper. |
| **Storage** | Graph DB + embeddings; enterprise compliance (SOC 2, HIPAA BAA). |
| **Retrieval** | Hybrid semantic + keyword + graph traversal; strong “what was true at time T” queries. |
| **Agent integration** | Official LangChain/LlamaIndex; HTTP API on Zep Cloud; Graphiti self-host. |
| **Maintenance** | Graphiti is actively developed; temporal model adds schema/evolution complexity. |
| **Complexity** | **High** for static ADR corpus — temporal graph is power users’ tool for evolving conversational facts, not frozen markdown files. |
| **Licensing** | Graphiti Apache-2.0; Zep Cloud proprietary. |
| **Operational cost** | ~$25/mo Flex cloud; self-host Graphiti on your infra. |

**Fit for Builder Memory:** **Overkill for corpus retrieval.** Valuable if builder agents must reason about **how decisions evolved over time** — but ADRs already capture that in git. Risk of duplicate truth (graph facts vs `decisions/`).

---

### 3.7 Custom corpus indexer (not in original list — evaluated because no listed framework fits)

| Dimension | Assessment |
|-----------|------------|
| **Architecture** | `BuilderKnowledgeIndexer` watches git-tracked paths → chunk → embed (optional) → local store (SQLite FTS + LanceDB/Chroma). Separate `BuilderEpisodicStore` (SQLite JSON) for session artifacts. |
| **Storage** | Local `.builder-memory/` (gitignored) — explicitly **not** Cloud SQL / M2 tables. |
| **Retrieval** | BM25 + optional embeddings; metadata filters (`kind: adr`, `path: contracts/`). Deterministic re-index from filesystem. |
| **Agent integration** | Python CLI + library: `builder-memory retrieve --task "..." --budget 8k`. Called from Context Builder before agent dispatch. |
| **Maintenance** | Re-index on `git diff` or manual `builder-memory index`. Staleness = `index_commit_sha` vs `HEAD`. |
| **Complexity** | **Medium** implementation, **low** operational — no third-party agent runtime. |
| **Licensing** | Project-owned; deps MIT/Apache (Chroma, LanceDB, rank-bm25). |
| **Operational cost** | ~$0 self-host; optional Vertex embedding API (same ADC as ThesisOS) for semantic layer. |

**Fit for Builder Memory:** **Best primary fit.** Aligns with Contract-First, promotion gates, and “filesystem wins.”

---

## 4. Comparison matrix

| Framework | Corpus index | Episodic builder memory | Retrieval-only | Isolated from M2 | Integration complexity | License clarity | Ops cost | **Score** |
|-----------|:------------:|:-----------------------:|:--------------:|:----------------:|:----------------------:|:---------------:|:--------:|:---------:|
| **Custom hybrid** | ✅✅ | ✅ | ✅✅ | ✅✅ | Medium build | ✅ | Low | **9/10** |
| **Mem0 (self-host)** | ⚠️ | ✅✅ | ⚠️ | ✅ | Low | ✅ | Low | **6/10** (episodic only) |
| **Zep/Graphiti** | ⚠️ | ✅ | ⚠️ | ✅ | Medium–High | ✅ (Graphiti) | Medium | **5/10** |
| **TencentDB Agent Memory** | ❌ | ✅ | ❌ | ✅ | High | ❌ unclear | Medium | **3/10** |
| **DB-GPT Memory** | ⚠️ | ✅ | ❌ | ❌ | Very High | ✅ | High | **2/10** |
| **DB-GPT (full)** | ⚠️ | ✅ | ❌ | ❌ | Very High | ✅ | Very High | **1/10** |
| **Letta** | ❌ | ✅✅ | ❌ | ⚠️ | Very High | ✅ | Medium | **2/10** |

Legend: ✅✅ excellent · ✅ good · ⚠️ partial/with guardrails · ❌ poor fit

---

## 5. Recommendation

### 5.1 Approved direction (pending Architect sign-off)

Adopt a **two-layer Builder Memory architecture**:

```text
┌─────────────────────────────────────────────────────────────┐
│  LAYER A — Corpus Retrieval (primary, ~80% of token savings) │
│  Custom BuilderKnowledgeIndexer                             │
│  Source: knowledge/ contracts/ decisions/ plans/ docs/      │
│  Store: .builder-memory/index/ (gitignored)                 │
│  Retrieval: BM25 + optional Vertex embeddings               │
└─────────────────────────────────────────────────────────────┘
                              +
┌─────────────────────────────────────────────────────────────┐
│  LAYER B — Episodic Builder Memory (secondary, optional)    │
│  BuilderEpisodicStore (SQLite) OR Mem0 self-hosted          │
│  Writes: lessons, risks, task outcomes, failure analyses    │
│  Never: code, contracts, ADRs, repo files                   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Why not a single external “agent memory” product?

1. **Wrong abstraction:** Listed frameworks optimize **conversation → distilled memory**. BuilderOS needs **git → retrieved context** with deterministic refresh.
2. **Authority risk:** Auto-extraction (Mem0, Tencent L1–L3, DB-GPT hybrid) can produce “memories” that contradict frozen ADRs. Guardrails help but the products are not designed for “always lose to filesystem.”
3. **Runtime boundary:** DB-GPT and Letta import a second agent execution model. ThesisOS already has AgentOS + Cursor orchestration.
4. **M2 separation:** Runtime memory is custom Postgres (ADR-0003, M2 spec). Builder Memory must live outside `backend/app/services/memory/`.
5. **License:** TencentDB Agent Memory’s NOASSERTION license is a blocker for default recommendation.

### 5.3 If stakeholders require one external vendor

**Fallback:** Mem0 self-hosted, **episodic layer only**, with:
- All corpus retrieval via custom indexer (Layer A)
- Mem0 `user_id=builder-{agent_type}` namespaces
- Hard rule: retrieved Mem0 facts labeled `NON_AUTHORITATIVE` in prompt assembly
- New ADR: `ADR-00XX-builder-memory-boundaries` (builder-only, not M2)

Do **not** adopt TencentDB Agent Memory or DB-GPT without explicit legal + architecture review.

### 5.4 Explicit non-recommendations

| Framework | Reason |
|-----------|--------|
| TencentDB Agent Memory | Wrong use case (persona/session pipeline); unclear license; TypeScript Gateway ops |
| DB-GPT (any form) | Full framework adoption; not retrieval-only |
| Letta | Second agent runtime; conflicts with Cursor BuilderOS |
| Zep/Graphiti as primary | Temporal graph overkill; duplicate ADR truth |

---

## 6. Open questions for approval

1. **Embeddings:** Use Vertex multilingual embeddings (768-d, aligned with M3/M4) for Layer A, or BM25-only for v1?
2. **Mem0:** Include Layer B in v1, or ship corpus-only and add episodic in v2?
3. **ADR:** Author `ADR-00XX-builder-memory-boundaries` before Phase 4 implementation?
4. **Hosting:** Keep `.builder-memory/` local-only, or optional shared team index (GCS artifact)?

---

## 7. Next steps (after approval)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| Phase 1 | This document | ✅ Draft complete |
| Phase 2 | `docs/superpowers/specs/builder-memory-integration-design.md` | See companion spec |
| Phase 3 | `plans/builder-memory-implementation-plan.md` | See companion plan |
| Phase 4 | Code implementation | **Blocked** until Phases 1–2 approved |

---

## 8. References

- `knowledge/README.md` — source-of-truth hierarchy
- `decisions/ADR-0003-custom-memory.md` — runtime memory (separate concern)
- `docs/superpowers/specs/2026-06-24-thesisos-m2-memory-system-design.md` — M2 runtime memory
- `.cursor/skills/orchestrate-builders/SKILL.md` — BuilderOS orchestration
- External: [TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory), [DB-GPT memory docs](https://docs.dbgpt.cn/docs/agents/modules/memory/), [Mem0](https://github.com/mem0ai/mem0), [Graphiti](https://github.com/getzep/graphiti), [Letta](https://github.com/letta-ai/letta)
