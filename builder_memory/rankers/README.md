# Rankers (M3+ extension point)

V1 uses `bm25.Bm25Ranker` only. Future rankers plug in here without changing `retriever/`:

| Module (planned) | Strategy |
|------------------|----------|
| `bm25.py` | ✅ V1 — FTS5 BM25 + role kind weights |
| `recency.py` | BM25 + file mtime / snapshot distance |
| `milestone.py` | BM25 + milestone proximity from epic tag |
| `hybrid.py` | BM25 + Vertex embeddings (deferred) |

Swap ranker in `ContextBuilder` when a later milestone proves lexical retrieval is insufficient.
