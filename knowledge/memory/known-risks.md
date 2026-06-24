# Known Risks

> Sources: M0 spec §19, M1 spec §11, `docs/m1-promotion.md` (known non-blockers), `docs/m0-promotion.md`, ADR-0009/0012. Ranked by impact × likelihood.

## Active / open risks

| # | Risk | Impact | Status / mitigation | Owner milestone |
|---|------|--------|---------------------|-----------------|
| R1 | **pgvector index vs model-agnostic embeddings** — HNSW/IVFFlat needs a fixed dim, but `embeddings` is model/dimension-tagged | High (retrieval perf/correctness) | Strategy chosen: **partition by `model`** (each partition fixed-dim + own index); decide detail when retrieval is built | M2/M4 (spec §19) |
| R2 | **Token usage not captured** on Vertex streaming | Medium (accounting only) | Add `stream_options={"include_usage": True}` or a non-stream usage call | M2 |
| R3 | **Streaming path under-tested** (`stream_turn` no e2e unit test; disconnect→cancelled reasoned only) | Medium (regressions slip) | Add an integration test with a fake LLM + DB | M2 |
| R4 | **M1 not yet on Cloud Run** — validated locally vs real Vertex; prod deploy + `langgraph` schema on Cloud SQL pending | Medium (not really shipped) | buildx amd64 → AR → `gcloud run deploy`; verify `PostgresSaver.setup()` on Cloud SQL | M1 close |
| R5 | **Frontend prod API URL** not a Docker `ARG` | Medium (prod UI can't reach backend) | Add `ARG/ENV NEXT_PUBLIC_API_BASE_URL` before `npm run build`; pass backend URL | M1/M2 |
| R6 | **Job durability** — in-process worker only | Medium (lost heavy jobs at scale) | Durable queue (Cloud Run Jobs / Cloud Tasks) | before M11 (ADR-0009) |
| R7 | **Cloud Build CI disabled** (org policy) | Low/Medium (manual deploys) | Re-enable when org policy allows; grant CB SA roles | when allowed |
| R8 | **`db-f1-micro` limits** under ingestion/embedding load | Medium | Reassess instance size | M3/M4 |
| R9 | **Cloud Run cold starts** | Low (single-user tolerant) | Revisit (min instances / warmups) | M11 |
| R10 | **Terraform state holds DB password** (local + gitignored) | Low (single-user) | Encrypt if a remote backend is added (GCS) | when remote backend added |
| R11 | **SSE through Cloud Run buffering/idle timeouts** | Low | `ping=15` heartbeat; verify in prod | M1 close |
| R12 | **LiteLLM ↔ Vertex streaming shape drift** between versions | Low/Medium | Pin versions; map `delta/finish_reason/usage` defensively | ongoing |
| R13 | **PostgresSaver custom-schema support** across versions | Low | Pin `langgraph-checkpoint-postgres`; fallback to documented `public` tables (still excluded from drift) | ADR-0012 |
| R14 | **Vertex insufficient for Italian academic prose** | Low | Re-evaluate provider only then; LiteLLM seam keeps swap cheap | spec §19 |

## Risk-management principles
- Risks are **scheduled, not ignored** — each maps to the milestone that resolves it.
- Open questions live in `context/open-questions.md`; closed ones move to
  `decisions/`.
- Architecture risks are mitigated structurally (frozen contracts, seams, ownership
  boundaries) before they become incidents.
