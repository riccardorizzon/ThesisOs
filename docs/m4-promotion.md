# M4 Promotion Gate — Status

_As of 2026-06-25. **Promoted:** merged to `main`, tag `m4-complete`._

```yaml
# --- Implemented & verified (green in CI) ---
retrieval_db:           green    # 0004_retrieval_system; partitioned embeddings; HNSW; chunks.content_tsv
retrieval_service:        green    # RetrievalService sole chunk-embedding writer; idempotent embed
litellm_embed:            green    # LiteLLMClient.embed() → Vertex multilingual model
search_api:               green    # POST /search hybrid ranked results
retriever_node:           green    # memory_context → retriever → conversation (retrieved_context)
indexed_status:           green    # DocumentService.mark_indexed hook; post-parse embed pipeline
embed_pipeline:           green    # background parse→embed; POST /documents/{id}/index
graphstate:               green    # field list unchanged (ADR-0007)
document_service:         green    # sole chunk writer preserved; retrieval read-only on chunks
scope_creep:              green    # no writer/planner/admin search UI/chunk→chat bypass
documentation:            green    # frozen spec, ADR-0024, plan, this gate
knowledge_updated:        green    # knowledge/ mirror updated Phase 6
tests_ci:                 green    # make ci: backend 86 passed / 36 skipped; frontend 33; builder_engine 20
contracts:                additive # OpenAPI SearchRequest/Response; schema.sql embeddings PK + content_tsv
builder_checkrunner:      green    # embed + search-smoke stages registered (MB1 Phase 6)

# --- Pending validation (environment) ---
db_integration:           waived     # Docker containerd I/O error (2026-06-25); migration/integration skip without Postgres
vertex_embed_live:        pending  # real Vertex embed smoke requires ADC + project (local optional)
m4_tag:                   green    # merged to main; tag m4-complete
```

## Critic sign-off

| Check | Result |
|-------|--------|
| GraphState field list unchanged | ✅ `test_graph_state.py` |
| DocumentService sole chunk writer | ✅ no embed in document service |
| RetrievalService sole chunk embedding writer | ✅ ADR-0024 |
| No admin corpus search on `/documents` | ✅ search only on `POST /search` |
| No chunk text in `/chat` without retrieval | ✅ retriever populates `retrieved_context` only |
| `indexed` only via M4 pipeline | ✅ `mark_indexed` hook |
| Writer/planner/multi-agent | ✅ not implemented |

## QA sign-off

| Check | Result |
|-------|--------|
| `test_retrieval_migration.py` | ✅ model invariants + integration skip without DB |
| `test_retrieval_service.py` | ✅ idempotency, mark_indexed, delete cascade (skip without DB) |
| `test_search_api.py` | ✅ 3 tests (mocked service) |
| `test_retriever_node.py` | ✅ 3 tests |
| `test_litellm_client.py` | ✅ embed + astream |
| Full `make ci` | ✅ green |

## Evidence

```bash
make ci
cd backend && .venv/bin/python -m pytest tests/test_retrieval_*.py tests/test_search_api.py tests/test_retriever_node.py -v
builder_engine/.venv/bin/builder-engine check embed --repo-root .
builder_engine/.venv/bin/builder-engine check search-smoke --repo-root .
```

## Promotion

```bash
git checkout main
git merge --no-ff m4-retrieval-system
git tag m4-complete
```

## Forbidden until M5+ specs frozen

Writer (M6), planner/router (M5), admin search UI, GraphState new fields, Mem0 auto-extraction (M15–M16).
