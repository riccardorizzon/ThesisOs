# Builder Memory — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. **Phase 4 is blocked** until framework analysis + design spec are Architect-approved.

**Goal:** Ship a retrieval-only Builder Memory layer that accelerates Cursor builder agents without touching ThesisOS runtime or frozen contracts.

**Architecture:** Two-layer sidecar — `BuilderKnowledgeIndexer` (corpus cache from git allowlist) + optional `BuilderEpisodicStore` (session artifacts). Exposes Context Builder, Knowledge Retrieval, and Agent Context Assembly services. Storage in gitignored `.builder-memory/`.

**Tech Stack:** Python 3.11+, optional Vertex embeddings (768-d, ADC), SQLite FTS5 + LanceDB or Chroma (local), Typer CLI, pytest.

**Spec:** `docs/superpowers/specs/builder-memory-integration-design.md`  
**Analysis:** `docs/research/builder-memory-framework-analysis.md`  
**New ADR (proposed):** ADR-00XX Builder Memory Boundaries

**Branch:** `builder-memory` (from `main` after M2 merge or current `m2-memory-system` — coordinate with active epic)  
**Conventions:** No imports from `backend.app`; M0+M1+M2 tests must stay green; additive docs only until gate passes.

---

## Prerequisite gate (before any code)

```yaml
framework_analysis: approved    # docs/research/builder-memory-framework-analysis.md
design_spec: approved         # docs/superpowers/specs/builder-memory-integration-design.md
implementation_plan: approved # this document
architect_signoff: true
```

**Do not start Phase 1 implementation until all four are green.** ✅ All green (2026-06-24).

---

## Phase 1 — ADR, package scaffold, indexer MVP

### Objective
Establish boundaries in an ADR; create `builder_memory/` package; implement path allowlist/denylist indexing with BM25-only retrieval and CLI `index` + `status`.

### Files affected

| Action | Path |
|--------|------|
| Create | `decisions/ADR-00XX-builder-memory-boundaries.md` |
| Create | `builder_memory/__init__.py` |
| Create | `builder_memory/config.py` — allowlist/denylist, paths |
| Create | `builder_memory/indexer.py` — walk, chunk, FTS index |
| Create | `builder_memory/manifest.py` — commit sha, counts |
| Create | `builder_memory/cli.py` — Typer: `index`, `status` |
| Create | `pyproject.toml` or extend root — `builder-memory` entry point |
| Modify | `.gitignore` — `.builder-memory/` |
| Create | `builder_memory/tests/test_indexer.py` |
| Create | `builder_memory/tests/test_config.py` |

### Risks
- Chunking ADR files incorrectly splits decisions from context → use heading-aware chunker with minimum chunk size.
- Indexing `contracts/` OpenAPI YAML as text may produce large chunks → per-path/component splitting in Phase 2.

### Tests
- `test_config.py` — allowlist includes `decisions/ADR-0001-contract-first.md`; denylist excludes `backend/`.
- `test_indexer.py` — index fixture tree; manifest written; chunk count > 0.
- `test_indexer.py` — incremental skips unchanged files (mtime + sha).

### Promotion criteria
```yaml
adr_boundaries: complete
cli_index: green           # builder-memory index on repo
cli_status: green          # shows commit_sha, chunk_count
denylist_respected: green  # backend/ not in index
gitignore: present
runtime_import_guard: green  # no backend.app imports in builder_memory/
```

---

## Phase 2 — Retrieval + Context Builder + Assembly

### Objective
Implement hybrid retrieval (BM25; embedding hook stubbed), Context Builder orchestration, Agent Context Assembly with `NON-AUTHORITATIVE` header, CLI `retrieve`.

### Files affected

| Action | Path |
|--------|------|
| Create | `builder_memory/retrieval.py` — query, rank, role bias |
| Create | `builder_memory/context_builder.py` — task → retrieval plan |
| Create | `builder_memory/assembly.py` — prompt blocks, citations |
| Create | `builder_memory/chunking.py` — heading-aware markdown |
| Create | `builder_memory/metadata.py` — kind tagging by path |
| Modify | `builder_memory/cli.py` — add `retrieve` |
| Create | `builder_memory/tests/test_retrieval.py` |
| Create | `builder_memory/tests/test_context_builder.py` |
| Create | `builder_memory/tests/test_assembly.py` |

### Risks
- Token budget math inaccurate → use conservative char/4 estimate; test with fixed budget.
- Mandatory injections bloat small tasks → cap mandatory block at 30% of budget.

### Tests
- Query `"GraphState frozen"` returns chunk from `ADR-0007` or `knowledge/contracts/graphstate.md`.
- `agent_role=architect` boosts ADR scores vs `agent_role=backend`.
- Assembly output contains `NON-AUTHORITATIVE` header and `Source:` paths.
- `token_budget=1000` truncates without dropping mandatory STATE/spec injections.

### Promotion criteria
```yaml
retrieval_smoke: green     # ADR-0007 retrievable
role_bias: green           # architect vs backend scoring differs
assembly_format: green     # header + citations present
cli_retrieve: green
phase1_tests: green
```

---

## Phase 3 — Optional embeddings + episodic store

### Objective
Add Vertex embedding layer (optional, ADC); implement `BuilderEpisodicStore` for allowed write types; wire post-Critic append API.

### Files affected

| Action | Path |
|--------|------|
| Create | `builder_memory/embeddings.py` — Vertex via LiteLLM or google-genai |
| Modify | `builder_memory/retrieval.py` — hybrid BM25 + cosine |
| Create | `builder_memory/episodic.py` — SQLite append-only |
| Create | `builder_memory/write_policy.py` — validate allowed write types |
| Modify | `builder_memory/context_builder.py` — merge episodic hints |
| Modify | `builder_memory/cli.py` — `episodic append`, `index --embeddings` |
| Create | `builder_memory/tests/test_episodic.py` |
| Create | `builder_memory/tests/test_embeddings.py` (mock Vertex) |

### Risks
- Vertex ADC unavailable in CI → embeddings tests mocked; BM25 fallback required.
- Episodic store duplicates git content → dedup hash against corpus chunks before append.

### Tests
- With mocks: hybrid score differs from BM25-only.
- Episodic append rejects `type=contract_mutation`.
- Episodic entry requires `source_refs` when `type=lesson_learned`.
- Fallback: `embeddings` disabled → retrieval still works.

### Promotion criteria
```yaml
hybrid_retrieval: green    # mocked embedding test
episodic_policy: green     # forbidden writes rejected
bm25_fallback: green
phase2_tests: green
```

---

## Phase 4 — BuilderOS integration

### Objective
Integrate with `orchestrate-builders` wave dispatch; document agent prompt template; add freshness check before `wave`.

### Files affected

| Action | Path |
|--------|------|
| Modify | `.cursor/skills/orchestrate-builders/SKILL.md` — Step 2D retrieval hook |
| Modify | `.cursor/skills/orchestrate-builders/references/agent-prompt-templates.md` |
| Create | `.cursor/skills/orchestrate-builders/scripts/builder-memory-preflight.sh` |
| Create | `knowledge/development/builder-memory.md` — operator guide |
| Create | `docs/builder-memory-promotion.md` — gate evidence |

### Risks
- Stale index in long sessions → preflight script exits non-zero if `manifest.commit_sha != HEAD` (warn, not block, configurable).
- Prompt bloat → default `token_budget=6000` for implementers, `8000` for architect/critic.

### Tests
- `builder-memory-preflight.sh` detects stale manifest (fixture).
- Manual smoke: `orchestrate-builders status` + retrieve for active epic in `STATE.yaml`.

### Promotion criteria
```yaml
preflight_script: green
skill_docs_updated: true
manual_wave_smoke: documented  # evidence in docs/builder-memory-promotion.md
m0_m1_m2_tests: green
scope_creep: false
```

---

## Phase 5 — Optional Mem0 episodic backend (only if approved)

### Objective
If stakeholders require external episodic memory: swap `BuilderEpisodicStore` SQLite for Mem0 self-hosted adapter behind interface.

### Files affected

| Action | Path |
|--------|------|
| Create | `builder_memory/episodic_mem0.py` — adapter |
| Modify | `builder_memory/config.py` — `EPISODIC_BACKEND=sqlite|mem0` |
| Create | `builder_memory/tests/test_episodic_mem0.py` (integration, optional) |
| Update | `docs/research/builder-memory-framework-analysis.md` — record decision |

### Risks
- Mem0 auto-extraction diverges from git → **corpus stays on custom indexer**; Mem0 episodic only.
- Extra Docker dependency → document in operator guide; default remains SQLite.

### Tests
- Adapter implements same interface as `episodic.py`.
- `EPISODIC_BACKEND=sqlite` remains default and passes all Phase 3 tests.

### Promotion criteria
```yaml
mem0_explicitly_approved: true   # separate Architect decision
adapter_tests: green
sqlite_default_unchanged: green
```

**Skip this phase unless Mem0 is explicitly approved.**

---

## Phase 6 — Gate, tag, handoff

### Objective
Record promotion evidence; tag builder-memory v1; handoff to next epic.

### Files affected

| Action | Path |
|--------|------|
| Create | `docs/builder-memory-promotion.md` |
| Modify | `knowledge/context/current-state.md` — note Builder Memory available |
| Modify | `knowledge/context/completed-work.md` |
| Modify | `plans/builder/STATE.yaml` — if epic tracked there |

### Promotion criteria (final)
```yaml
framework_analysis: approved
design_spec: approved
implementation_plan: approved
adr_boundaries: complete
index_freshness: verified
retrieval_smoke: green
runtime_isolation: verified
integration_smoke: green
m0_m1_m2_tests: green
scope_creep: false
documentation: complete
```

### Commands (evidence template)
```bash
# Index
builder-memory index --incremental
builder-memory status

# Retrieval smoke
builder-memory retrieve --task "GraphState frozen contract" --role architect --budget 8000

# Isolation
rg "backend\.app" builder_memory/ && exit 1 || true

# Regression
cd backend && pytest -q
```

---

## Dependency graph

```text
Prerequisite gate
       │
       ▼
Phase 1 (ADR + indexer)
       │
       ▼
Phase 2 (retrieval + assembly)
       │
       ├──▶ Phase 3 (embeddings + episodic) ──▶ Phase 4 (BuilderOS integration)
       │                                              │
       │                                              ▼
       │                                    Phase 5 (Mem0, optional)
       │                                              │
       └──────────────────────────────────────────────┴──▶ Phase 6 (gate)
```

---

## Explicitly out of scope

- ThesisOS `/memory` API changes
- LangGraph `memory_context_node` changes
- Cloud Run deployment of Builder Memory
- Indexing `backend/`, `frontend/`, generated code
- Replacing `knowledge/` curation workflow
- TencentDB Agent Memory or DB-GPT integration (rejected in framework analysis unless re-opened by Architect)

---

## Success criteria (from objective)

A newly spawned builder agent can:

1. **Read task** — via orchestrator prompt + `STATE.yaml`
2. **Retrieve relevant knowledge** — `builder-memory retrieve` or auto-injected context
3. **Understand project state** — mandatory `current-state.md` + `STATE.yaml` injections
4. **Understand architecture** — `knowledge/architecture/*`, system spec excerpts
5. **Understand contracts** — OpenAPI, GraphState, schema chunks
6. **Understand ADRs** — ranked ADR excerpts with source paths
7. **Execute task** — without reading the entire repository

**Verification:** New agent session test script in `docs/builder-memory-promotion.md` — spawn agent with retrieval only (no `@codebase` glob), confirm it cites correct ADR paths for a checklist task.

---

## Estimated effort

| Phase | Effort | Blocker |
|-------|--------|---------|
| Prerequisite | 0 dev (review) | Architect approval |
| Phase 1 | 1–2 days | — |
| Phase 2 | 2–3 days | Phase 1 |
| Phase 3 | 1–2 days | Phase 2 |
| Phase 4 | 1 day | Phase 2 (Phase 3 optional) |
| Phase 5 | 1–2 days | Explicit Mem0 approval |
| Phase 6 | 0.5 day | All prior gates |

**Total (without Mem0):** ~5–8 dev days after approval.
