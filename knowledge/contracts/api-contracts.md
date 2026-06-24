# API Contracts

> Sources: `contracts/openapi/openapi.yaml`, `backend/app/api/*`, M0 spec §9, M1 spec §6–§8, ADR-0001.

The REST contract is OpenAPI 3.1 at `contracts/openapi/openapi.yaml`. Deferred
paths are declared now with an `x-milestone` extension and currently return `501`
(Contract-First, ADR-0001). **The OpenAPI file is the contract; this is a summary.**

## Implemented endpoints

| Method/Path | Status | Behavior |
|-------------|--------|----------|
| `GET /health` | M0 | `200 {"status":"ok"}` |
| `GET /ready` | M0 | `200 {"status":"ready","db":bool,"config":true}`; `503` if DB down |
| `GET /metrics` | M0 | Prometheus/OpenMetrics |
| `POST /jobs` | M0 (stub) | `501` — job execution wired post-M0 (ADR-0009) |
| `GET /jobs/{id}` | M0 (stub) | `501` |
| `POST /chat` | **M1** | SSE token stream (see below) |

## Deferred endpoints (contract-only, 501)

| Path | Milestone |
|------|-----------|
| `POST /upload`, `GET /documents`, `GET /documents/{id}`, `POST /summarize` | M3 |
| `POST /search` | M4 |
| `GET/POST /memory` | M2 |
| `POST /chapters` | M6 |
| `GET /outline` | M8 |
| `POST /citations`, `GET /bibliography?style=apa7` | M7 |

## `POST /chat` (M1)

**Request:** `{ "message": string (1..32000), "conversation_id"?: string }`.

**Responses:**
- `200 text/event-stream` — SSE stream.
- `409 { code: "conversation_busy", message }` — a response is already streaming
  for this conversation (single-active-run guard).
- `503 { code: "llm_not_configured", message }` — Vertex runtime not configured
  (fail-fast before opening the stream).
- `422`/`400` — empty/oversized message (Pydantic validation, `Error` schema).

### SSE event protocol (M1 spec §7)

Named events so future signals slot in without breaking the client:

```text
event: token   data: {"text": "<delta>"}
event: ping    data: {}                                       # heartbeat ~every 15s
event: done    data: {"conversation_id","message_id","usage"}
event: error   data: {"code","message"}
```

Client rule: ignore `ping`, append on `token`, finalize on `done`, banner on
`error`. **Future channels reserved (not M1):** `event: tool`, `event: retrieval`,
`event: critic`.

> **Framing caveat (resolved bug C1):** events are CRLF-framed; the frontend parser
> was fixed to handle this (`f26885c`). Keep CRLF compatibility in any new SSE client.

## Error schema (frozen)

`Error { code: string, message: string }` — required for all error bodies. Never
return stack traces to the client (M1 spec §8). Known codes: `llm_not_configured`,
`conversation_busy`, `stream_error`, `setup_error`.

## Contract change rules
- Adding endpoints / realizing an `x-milestone` stub is **additive** and allowed.
- Changing frozen domain contracts (`GraphState`, domain DB models, ADR-0001..0010)
  is **forbidden** without a new ADR (M1 spec §6).
- Keep OpenAPI in sync with the router in the milestone that implements a path.
