# Builder Memory Integration — Design Spec

- **Date:** 2026-06-24
- **Status:** Approved (Architect 2026-06-24) — ADR-0019; V1 BM25-only, SQLite episodic, no Mem0
- **Scope:** Retrieval-only memory layer for **Builder Agents** (Cursor / BuilderOS). **Excludes** ThesisOS runtime memory (M2 `MemoryService`, `/memory` API, `memory_context_node`).
- **Authors:** Builder Architect session
- **Builds on:** M0/M1 frozen seams, M2 memory design (parallel, non-overlapping), `orchestrate-builders` skill, framework analysis (`docs/research/builder-memory-framework-analysis.md`)
- **New ADR (proposed):** ADR-00XX Builder Memory Boundaries (builder-only, retrieval-only, filesystem authority)

---

## 1. Goals

1. **Accelerate builder agent onboarding** — a newly spawned agent understands project state, architecture, contracts, and ADRs without reading the entire repository.
2. **Reduce context/token consumption** — compressed, task-relevant retrieval replaces brute-force repo reads.
3. **Preserve architectural boundaries** — Builder Memory is **never** authoritative; `knowledge/`, `contracts/`, `decisions/`, `plans/`, `docs/` remain source of truth.
4. **Integrate with BuilderOS flow** — Context Builder runs before every agent execution in the Architect → Planner → Implementer → Critic → Promotion pipeline.
5. **Support all builder agent types** — Architect, Planner, Backend, Frontend, QA, Critic (and future builder roles).

---

## 2. Non-goals (hard boundary)

| Forbidden | Rationale |
|-----------|-----------|
| Authoritative storage | Filesystem + ADRs win on any conflict |
| Direct repository writes | Agents write via normal git workflow, not memory layer |
| Contract mutation | `contracts/` changes require Architect + ADR |
| ADR mutation | `decisions/` changes require explicit human/Architect action |
| Code generation in memory layer | Memory returns context strings only |
| ThesisOS runtime integration | No hooks into `/chat`, `ConversationService`, `GraphState`, M2 `MemoryService` |
| Replacing `knowledge/` | Knowledge OS remains the curated mirror; memory is indexed cache |
| Indexing generated artifacts | No `node_modules/`, `venv/`, `dist/`, `coverage/`, build outputs |
| Auto-promotion from memory | Promotion gates require evidence in git (`docs/m{n}-promotion.md`) |

---

## 3. Architecture

### 3.1 System context

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         BUILDEROS (Cursor / AgentOS)                      │
│                                                                           │
│  ┌─────────────┐    ┌─────────────────┐    ┌──────────────────────────┐  │
│  │ Builder     │───▶│ Context Builder │───▶│ Builder Memory Retrieval │  │
│  │ Agent       │    │ Service         │    │ (sidecar, gitignored)    │  │
│  │ (any role)  │    └────────┬────────┘    └────────────┬─────────────┘  │
│  └─────────────┘             │                          │                 │
│                              ▼                          │ index of        │
│                    ┌─────────────────┐                  │                 │
│                    │ Prompt Assembly │◀─────────────────┘                 │
│                    └────────┬────────┘                                    │
│                              ▼                                            │
│                    ┌─────────────────┐                                    │
│                    │ Agent Execution │                                    │
│                    └────────┬────────┘                                    │
│                              ▼                                            │
│                    ┌─────────────────┐                                    │
│                    │ Critic          │                                    │
│                    └────────┬────────┘                                    │
│                              ▼                                            │
│                    ┌─────────────────┐                                    │
│                    │ Promotion       │──▶ git tags, promotion docs        │
│                    └─────────────────┘                                    │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                    THESISOS RUNTIME (separate, frozen)                    │
│  /chat · ConversationService · LangGraph · M2 MemoryService · /memory    │
│  Builder Memory does NOT connect here.                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component model

| Component | Responsibility | Location (proposed) |
|-----------|----------------|---------------------|
| **BuilderKnowledgeIndexer** | Watch/index corpus paths; chunk; store with metadata | `builder_memory/indexer.py` |
| **Knowledge Retrieval Service** | Query index; rank; filter by kind/path | `builder_memory/retrieval.py` |
| **Context Builder Service** | Orchestrate retrieval for a task; apply token budget | `builder_memory/context_builder.py` |
| **Agent Context Assembly Service** | Role-specific prompt sections; citation headers | `builder_memory/assembly.py` |
| **BuilderEpisodicStore** | Optional session artifacts (lessons, outcomes) | `builder_memory/episodic.py` |
| **CLI** | `index`, `retrieve`, `status` for agents and CI | `builder_memory/cli.py` |

**Deployment unit:** Python package under repo root `builder_memory/` (or `tools/builder-memory/`). **Not** deployed to Cloud Run. Runs locally during Cursor sessions and CI indexing.

**Storage:** `.builder-memory/` (gitignored):
```text
.builder-memory/
  index/           # vector + FTS metadata
  episodic.sqlite  # optional session store
  manifest.json    # index_commit_sha, indexed_at, chunk_count
```

### 3.3 Two-layer memory model

| Layer | Name | Source | Mutability | Authority |
|-------|------|--------|------------|-----------|
| **A** | Corpus cache | Git-tracked markdown/YAML | Rebuilt from filesystem | **Non-authoritative** |
| **B** | Episodic builder memory | Agent session outputs | Append-only writes | **Non-authoritative**; hints only |

On conflict: **always** re-read filesystem path cited in retrieval metadata.

---

## 4. Data flow

### 4.1 Indexing flow (offline / on-demand)

```text
git HEAD
  │
  ▼
Path filter (allowlist)
  │
  ▼
File reader ──▶ Chunker (heading-aware for .md)
  │
  ▼
Metadata tagger ──▶ kind: adr|contract|knowledge|plan|doc|state|promotion
  │
  ▼
Embedder (optional Vertex 768-d) + BM25 index
  │
  ▼
.builder-memory/index/
  │
  ▼
manifest.json { commit_sha, file_count, chunk_count }
```

### 4.2 Retrieval flow (per agent invocation)

```text
Task description + agent_role
  │
  ▼
Context Builder.identify_task()
  │
  ├──▶ retrieve project knowledge (knowledge/)
  ├──▶ retrieve ADRs (decisions/, filtered by relevance)
  ├──▶ retrieve contracts (contracts/)
  ├──▶ retrieve milestone context (plans/, docs/superpowers/specs/)
  ├──▶ retrieve STATE.yaml + promotion reports
  └──▶ retrieve episodic hints (Layer B, optional)
  │
  ▼
Rank + dedupe + token budget compress
  │
  ▼
Agent Context Assembly ──▶ structured prompt blocks
  │
  ▼
Agent Execution (Cursor Task / orchestrate-builders dispatch)
```

### 4.3 Post-execution flow (Critic → optional episodic write)

```text
Agent output + Critic verdict
  │
  ▼
If promotion-worthy insight AND NOT duplicating git content:
  └──▶ EpisodicStore.append({ type, packet_id, summary, refs })
  │
  ▼
Promotion gate still requires git evidence (unchanged)
```

---

## 5. Indexing strategy

### 5.1 Allowlist paths

| Path pattern | `kind` tag | Priority |
|--------------|------------|----------|
| `knowledge/**` | `knowledge` | High |
| `contracts/**` | `contract` | Critical |
| `decisions/ADR-*.md` | `adr` | Critical |
| `decisions/**` | `decision` | High |
| `plans/**` | `plan` | High |
| `plans/builder/STATE.yaml` | `state` | Critical |
| `docs/superpowers/specs/**` | `spec` | Critical |
| `docs/m*-promotion.md` | `promotion` | High |
| `docs/research/**` | `research` | Medium |
| `docs/architecture.md` | `doc` | High |
| `docs/**` | `doc` | Medium |

### 5.2 Denylist (never index)

```text
backend/
frontend/
infra/
node_modules/
venv/
.dist/
dist/
coverage/
.builder-memory/
.worktrees/
.git/
*.pyc
package-lock.json
```

**Rationale:** Builder Memory indexes **intent and contracts**, not implementation. Agents read owned code files directly when implementing.

### 5.3 Chunking rules

| File type | Strategy |
|-----------|----------|
| Markdown | Split on `##` / `###` headings; preserve heading breadcrumb in chunk metadata |
| YAML | One chunk per top-level key for `STATE.yaml`; whole file for small packets |
| OpenAPI/JSON schema | One chunk per path/component |
| SQL schema | One chunk per `CREATE TABLE` |

### 5.4 Metadata schema (per chunk)

```yaml
chunk_id: sha256(path + heading + offset)
source_path: decisions/ADR-0007-state-contract.md
source_commit: abc123
kind: adr
title: "ADR-0007: State Contract"
heading_path: ["ADR-0007", "Decision"]
token_estimate: 420
indexed_at: 2026-06-24T12:00:00Z
```

### 5.5 Refresh triggers

| Trigger | Action |
|---------|--------|
| `builder-memory index` (manual) | Full rebuild |
| `builder-memory index --incremental` | Diff since `manifest.commit_sha` |
| Pre-wave dispatch (`orchestrate-builders wave`) | Incremental if stale > 1 commit |
| CI (optional) | Verify index freshness in promotion gate |

---

## 6. Retrieval strategy

### 6.1 Query construction

Input: `{ task: str, agent_role: str, epic?: str, packet_id?: str, token_budget: int }`

1. **Role bias** — weight `kind` by agent:
   - Architect: `adr`, `spec`, `contract` ×2
   - Planner: `plan`, `spec`, `state` ×2
   - Backend/Frontend: `contract`, `knowledge/architecture/*`, `spec` ×2
   - QA: `promotion`, `plan`, `knowledge/development/testing*` ×2
   - Critic: `adr`, `promotion`, `contract` ×2

2. **Hybrid search** — `score = 0.4 * bm25 + 0.6 * cosine` (if embeddings enabled)

3. **Mandatory injections** (always include if exist):
   - `plans/builder/STATE.yaml` when `epic` or `packet_id` provided
   - Active milestone spec from `docs/superpowers/specs/` matching `epic`
   - `knowledge/context/current-state.md`

4. **Dedup** — same `source_path` → keep highest-scoring chunk per heading

5. **Compression** — truncate lowest-scoring chunks until under `token_budget`

### 6.2 Prompt assembly format

```markdown
## Builder Context (NON-AUTHORITATIVE — verify in repository)

> Indexed at commit {sha}. Filesystem wins on conflict.

### Current state
{state.yaml + current-state.md excerpts}

### Relevant ADRs
[{adr_id}] {excerpt} — Source: `{path}`

### Relevant contracts
{excerpt} — Source: `{path}`

### Milestone / plan context
{excerpt} — Source: `{path}`

### Episodic hints (session memory)
{optional lessons — labeled NON-AUTHORITATIVE}

---
## Your task
{task}
```

---

## 7. Update strategy

### 7.1 Corpus layer (Layer A)

| Event | Action |
|-------|--------|
| File added/changed/deleted in allowlist | Re-index affected files on next `index --incremental` |
| ADR accepted | Index `decisions/` — memory does not write ADR |
| Contract frozen | Index `contracts/` — memory does not write contract |
| Promotion doc merged | Index `docs/m*-promotion.md` |

**Never:** auto-sync memory → git.

### 7.2 Episodic layer (Layer B) — write policy

| Allowed writes | Forbidden writes |
|----------------|------------------|
| Lessons learned (summary + file refs) | Direct repository edits |
| Architectural observations (with ADR ref if exists) | New ADRs |
| Known risks (pointer to `knowledge/memory/known-risks.md`) | Contract changes |
| Completed milestone notes | Code generation |
| Task outcomes (`packet_id`, status, bullets) | Replacing promotion docs |
| Failure analyses | Source-of-truth replacement |

Episodic entries **must** include `source_refs: [path, ...]` when citing project facts.

---

## 8. Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| **Stale index** | `manifest.commit_sha != HEAD` | Warn in prompt; run incremental index; show `Indexed at commit X` |
| **Missing index** | No `.builder-memory/manifest.json` | Fallback: inject `knowledge/context/current-state.md` + `STATE.yaml` only; log warning |
| **Retrieval empty** | Zero chunks above threshold | Broaden query; include mandatory injections; never hallucinate content |
| **Authority inversion** | Agent treats memory as truth | Prompt header `NON-AUTHORITATIVE`; Critic checks citations against git |
| **Index drift vs knowledge/** | Hash mismatch on indexed path | Full re-index; knowledge/ mirror is not indexed if diverges from ADR/contracts — filesystem wins |
| **Token budget exceeded** | Assembly > budget | Drop lowest scores; preserve mandatory injections |
| **Embedding API down** | Vertex error | Degrade to BM25-only; continue with warning |
| **Episodic pollution** | Duplicate of git content | Dedup against corpus chunks before append; max 500 entries with LRU |
| **M2 confusion** | Builder code imports `MemoryService` | Lint rule: `builder_memory/` must not import `backend.app` |

---

## 9. Promotion gates

Builder Memory itself does not gate milestones. It supports the existing ADR-0010 pattern.

### 9.1 Builder Memory v1 gate (new, pre-merge to main)

```yaml
framework_analysis: approved          # docs/research/builder-memory-framework-analysis.md
design_spec: approved                 # this document
implementation_plan: approved         # plans/builder-memory-implementation-plan.md
adr_boundaries: complete              # ADR-00XX builder memory boundaries
index_freshness: verified             # manifest.commit_sha == HEAD
retrieval_smoke: green                # CLI returns ADR-0007 for "GraphState frozen"
runtime_isolation: verified           # no imports from backend.app.services.memory
m0_m1_m2_tests: green                 # existing suites unaffected
scope_creep: false                    # no ThesisOS runtime hooks
```

### 9.2 Integration with `orchestrate-builders`

Before `wave` dispatch:

1. Run `builder-memory index --incremental` (or skip if fresh).
2. Context Builder attaches retrieval block to each Task agent prompt.
3. Critic packet may run `builder-memory retrieve --task "verify promotion criteria"` for checklist assist.

**Promotion still requires** `docs/m{n}-promotion.md` evidence in git — memory assists, never substitutes.

---

## 10. Agent integration points

| Agent | Context Builder inputs | Retrieval emphasis |
|-------|------------------------|-------------------|
| **Architect** | milestone scope, open questions | ADRs, specs, contracts, rejection decisions |
| **Planner** | frozen spec path, epic | plans, spec tasks, STATE.yaml, promotion pattern |
| **Backend** | packet `owned_files`, spec §backend | OpenAPI, DB schema, GraphState, backend architecture |
| **Frontend** | packet `owned_files`, spec §frontend | OpenAPI `/chat`, frontend architecture, SSE contract |
| **QA** | promotion YAML from spec | testing strategy, promotion gates, prior `m*-promotion.md` |
| **Critic** | packet output, decisions list | ADRs, contracts, anti-goals, scope forbidden lists |

### 10.1 Python API (sketch)

```python
from builder_memory.context_builder import ContextBuilder

ctx = ContextBuilder().build(
    task="Implement MemoryService CRUD",
    agent_role="backend",
    epic="m2-memory-system",
    packet_id="P-B",
    token_budget=8000,
)
# ctx.prompt_block → inject into agent system prompt
# ctx.citations → [{path, heading, commit}]
```

### 10.2 CLI (sketch)

```bash
builder-memory index [--incremental]
builder-memory status
builder-memory retrieve --task "..." --role architect --budget 8000
```

### 10.3 Cursor skill hook (future)

Extend `orchestrate-builders` Step 2D agent prompts with:

```markdown
## Retrieved context
{builder-memory retrieve output}
```

---

## 11. Relationship to M2 ThesisOS Memory

| Dimension | M2 Runtime Memory | Builder Memory |
|-----------|-------------------|----------------|
| Users | ThesisOS end user | Cursor builder agents |
| Storage | Cloud SQL `memories` | Local `.builder-memory/` |
| Authority | Domain truth (operational kinds) | Non-authoritative cache |
| API | `/memory` REST | CLI + Python library |
| ADR | 0003, 0015, 0017, 0018 | 00XX (proposed) |
| Graph | `memory_context_node` | None |

**No shared tables. No shared services. No shared index.**

---

## 12. Security & privacy

- Index contains only repository content (no secrets — `.env` is denylisted).
- `.builder-memory/` gitignored; not pushed to Cloud SQL.
- Episodic store may contain session notes — local only unless team opts into shared artifact bucket.

---

## 13. Open questions

1. Approve custom Layer A vs require Mem0 for Layer B in v1?
2. Vertex embeddings for semantic search in v1, or BM25-only MVP?
3. Should `knowledge/` be indexed if it diverges from ADRs (index anyway — filesystem path still valid)?
4. ADR number for builder memory boundaries?

---

## 14. Approval checklist

- [ ] Framework analysis reviewed
- [ ] Two-layer architecture accepted
- [ ] Index allowlist/denylist accepted
- [ ] Runtime isolation from M2 confirmed
- [ ] Implementation plan reviewed
- [ ] **Architect sign-off** — unblocks Phase 4

**Status:** Awaiting approval. Do not implement until all boxes checked.
