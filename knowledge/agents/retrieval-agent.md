# Retrieval Agent (Runtime)

> Type: Runtime LangGraph node. Milestone: **M4**. Status: designed (contract frozen), not implemented. Sources: `contracts/agents/retriever.json`, M0 spec §7/§19, `contracts/openapi/openapi.yaml` (`/search`), ADR-0002/0007.

## Mission
Ground the assistant's answers in the document corpus: given the user's need,
retrieve the most relevant chunks via hybrid (vector + keyword) search.

## Responsibilities
- Embed the query (`text-multilingual-embedding-002` via the LLM seam) and run
  hybrid retrieval over `chunks`/`embeddings`.
- Populate `GraphState.retrieved_context` with scored chunks.
- Back the `POST /search` endpoint (M4).

## Inputs (contract)
- `reads_state`: `messages`, `route`.

## Outputs (contract)
- `writes_state`: `retrieved_context` (`state_mutations: retrieved_context = set`).
- Each item: `RetrievedChunk { chunk_id, score, content }`.

## Allowed actions
- Read `chunks`/`embeddings`; call `embed()`; rank/filter results.

## Forbidden actions
- Writing drafts or citations (Writer/Citation own those).
- Mutating `GraphState` fields other than `retrieved_context`.
- Adding `GraphState` fields (frozen, ADR-0007).
- Hardcoding embedding dimension (rows are model/dimension-tagged).

## Dependencies
- **M3 ingestion** (chunks must exist), **embeddings table + pgvector index**
  (index strategy is an open question — partition by `model`, decided M2/M4, spec
  §19), **LLM `embed()`** (wired M2/M4), **Router** (sets `route`).

## Promotion criteria (M4 gate, to be frozen in the M4 spec)
- Hybrid search returns ranked chunks; `retrieved_context` populated and
  serializable; pgvector index decision implemented; `/search` working.

## Failure modes (contract)
- `embed_failed` — embedding call failed.
- `no_results` — nothing relevant retrieved.
- (Design risk) dimension/index mismatch on model swap — mitigated by per-model
  partitioning.
