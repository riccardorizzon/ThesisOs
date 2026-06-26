# M4 Pipeline Freeze

> **Effective:** 2026-06-26, upon closure of the M4 Recovery Sprint.  
> **Scope:** Retrieval, grounding, embedding, and document ingestion paths delivered in M4 + recovery.

## Frozen components

No further refactoring of these areas unless a **reproducible product bug** is filed
with a failing regression test:

| Area | Key modules |
|------|-------------|
| Grounding wire | `backend/app/graph/prompt_wire.py`, `conversation_node` |
| Retriever node | `backend/app/graph/retriever.py` |
| Embedding batching | `RetrievalService._embed_chunk_rows`, `plan_embedding_batches` |
| Parser boundary | `backend/app/services/document/parsers/` |
| Index observability | `record_index_error`, `_parse_in_background` |
| Hybrid search | `RetrievalService._search`, `POST /search` |

## Allowed changes

- Bug fixes with regression tests and dogfood evidence (`make dogfood-m4`).
- Additive contract changes that do not alter frozen GraphState fields (ADR-0007).
- M5+ graph extensions that **consume** `retrieved_context` without rewriting M4 nodes.

## Forbidden without new ADR

- GraphState field additions for retrieval/grounding.
- Bypassing retriever to inject chunk text into `/chat`.
- Changing pgvector partition strategy (ADR-0024).
- Replacing batching with unbounded single-request embed calls.

## Verification

```bash
# Unit regression (53 tests)
make unit-m4-recovery

# End-to-end product smoke (stack must be up)
make dogfood-m4
```

Evidence archive: `dogfood-m4.md`, `docs/m4-recovery-final-report.md`.
