# M2 Promotion Gate — Status

_As of 2026-06-24. Branch `m2-memory-system`. Phases 1–6 complete; merge + tag pending._

```yaml
# --- Implemented & verified (green) ---
memory_db:              green    # 0002_memory_system; drift test; Memory + MemoryVersion models
memory_service:         green    # CRUD, versioning, WriteConflictError, load_prompt_context, apply_ops hook
memory_api:             green    # thin /memory CRUD + versions; error mapping; no context/search endpoints
memory_ui:              green    # Memory Administration UI; vitest 15/15; next build green
memory_context_node:    green    # START → memory_context_node → conversation_node → END
memory_injection:       green    # editable + pinned user/thesis in LLM wire; transient_only (Critic)
domain_contracts:       green    # GraphState, RunContext, LLMClient, ConversationService unchanged
scope_creep:            green    # no embeddings, retrieval, RAG, writer, multi-agent in M2
documentation:          green    # M2 spec, ADRs 0015/0017/0018, knowledge/ updated
knowledge_updated:      green    # Phase 5 + Phase 6 knowledge mirror
tests:                  green    # backend 39 passed / 14 skipped; frontend 15 passed (local)
contracts:              additive # OpenAPI + schema.sql additive only; frozen seams intact

# --- Pending / optional (not blocking tag if waived) ---
memory_events:          pending  # MemoryUpdated → events table (event bus stub; optional close-out)
m2_tag:                 pending  # merge → main → tag m2-complete

# --- Explicitly out of M2 gate (deferred) ---
restore_version:        deferred
memory_embeddings:      forbidden
retrieval:              forbidden
conversation_titling:   optional  # Q10; not gate-blocking
cloud_deploy_m2:        optional  # follow M1 cloud deploy pattern
```

## Critic sign-off (Phase 6)

| Check | Result |
|-------|--------|
| GraphState unchanged | ✅ No new fields |
| `memory_context` transient_only | ✅ System prepend in node; not persisted by ConversationService |
| No concept/citation in prompt path | ✅ `load_prompt_context` filters operational kinds only |
| No `/memory/context` or search API | ✅ Unchanged |
| No embeddings / retrieval | ✅ None introduced |
| `conversation_node` untouched | ✅ Only `build_graph` topology extended |

## QA sign-off (Phase 6)

| Check | Result |
|-------|--------|
| `test_memory_context_node.py` | ✅ 4 passed, 1 skipped (no local Postgres) |
| `test_conversation_graph.py` | ✅ Still streams tokens |
| Full backend suite | ✅ 39 passed, 14 skipped |
| GraphState / RunContext tests | ✅ Unchanged green |

## Evidence (local, reproducible)

```bash
# Backend (from backend/)
.venv/bin/python -m pytest -v          # 39 passed, 14 skipped
.venv/bin/ruff check app/graph/memory_context.py app/graph/conversation.py

# Frontend (from frontend/)
npm run test                           # 15 passed
npm run build                          # /memory routes compile

# Graph smoke (unit — no DB)
.venv/bin/python -m pytest tests/test_memory_context_node.py tests/test_conversation_graph.py -v
```

## Promotion (when approved)

```bash
git checkout main
git merge --no-ff m2-memory-system
git tag m2-complete
# release: v0.0.3-m2
```

## Known non-blockers (carry forward)

- `MemoryUpdated` events — wire when event bus is implemented; not required for graph injection.
- Token usage on Vertex streaming (Q2) — M2 optional / M11.
- M1/M2 cloud deploy on prod — independent of local validation.

## Forbidden until M3+ specs frozen

Document ingestion (M3), embeddings (M4), `/search` (M4), RAG, writer agents (M6), citation generation (M7), Mem0, multi-agent runtime (M12).
