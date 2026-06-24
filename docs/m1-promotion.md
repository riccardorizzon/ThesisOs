# M1 Promotion Gate — Status

_As of 2026-06-24. Local stack verified live against the **real** Vertex AI / Gemini on project
`thesisos-prod` (ADC). Nothing is self-declared: every green item has a reproducible command +
observed output (see evidence below)._

```yaml
# --- Verified locally (green), backend on python:3.12-slim via docker compose ---
docker_compose:   green     # db(healthy) + backend + frontend up; volume pgdata
health:           green     # /health -> {"status":"ok"}
ready:            green     # /ready  -> {"status":"ready","db":true,"config":true}
db_migrations:    green     # `alembic upgrade head` runs in the backend container at boot
chat:             green     # POST /chat -> real Gemini answer streamed
sse:              green     # CRLF-framed events: token … done (client parser fixed, C1)
adc_vertex:       green     # real Gemini via ADC on thesisos-prod / europe-west1 / gemini-2.5-pro
langgraph_schema: green     # checkpoint* tables created in schema `langgraph` (ADR-0012), not public
persistence:      green     # 1 conversation, 2 messages (user+assistant), 1 agent_run status=done
locking_409:      green     # single-active-run guard (unit) + full-turn lock incl. new conversations
not_configured_503: green   # /chat returns 503 llm_not_configured before opening the stream
tests:            23 passed, 1 skipped   # backend pytest (skip = live-DB integration, exercised here via compose)
ruff:             green     # ruff check app
frontend_build:   green     # next build; /chat -> HTTP 200 on :3000

# --- Cloud promotion (Fase 4) — PENDING / optional ---
cloud_run_deploy: pending   # this gate validated the stack LOCALLY vs real Vertex; Cloud Run deploy not done yet
langgraph_schema_cloud: pending  # PostgresSaver.setup() against Cloud SQL at first prod boot
```

## Evidence (verified 2026-06-24, local docker compose vs real Vertex)

```text
# docker compose ps
agentthesis-db-1        pgvector/pgvector:pg16   Up (healthy)   0.0.0.0:5432->5432
agentthesis-backend-1   agentthesis-backend      Up             0.0.0.0:8000->8000   (sh -c 'alembic upgrade head && uvicorn …')
agentthesis-frontend-1  agentthesis-frontend     Up             0.0.0.0:3000->3000

# curl localhost:8000/health  -> {"status":"ok"}
# curl localhost:8000/ready   -> {"status":"ready","db":true,"config":true}

# curl -N -X POST localhost:8000/chat -d '{"message":"Rispondi in una frase: chi sei?"}'
event: token
data: {"text": "Sono un grande modello linguistico, addestrato da Google."}

event: done
data: {"conversation_id":"13c6296b-…","message_id":"47a47322-…","usage":{}}

# psql (db container)
checkpoint tables -> langgraph.checkpoints, langgraph.checkpoint_blobs,
                     langgraph.checkpoint_writes, langgraph.checkpoint_migrations   # schema=langgraph (not public)
schemata          -> public, langgraph
counts            -> conversations=1, messages=2, agent_runs=1
agent_runs        -> status=done, graph=conversation, trigger=chat, output={}

# curl localhost:3000/chat -> HTTP 200   (next build; UI live)
# backend/ : pytest -> 23 passed, 1 skipped ; ruff check app -> All checks passed
```

## Local run wiring

```bash
# Vertex/Gemini for the local stack is wired via docker-compose.override.yml (gitignored):
#   backend.environment: GOOGLE_CLOUD_PROJECT=thesisos-prod, VERTEX_LOCATION=europe-west1,
#                        GEMINI_MODEL=gemini-2.5-pro, GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/adc.json
#   backend.volumes:     ~/.config/gcloud/application_default_credentials.json -> /var/secrets/adc.json:ro
docker compose up --build -d
docker compose down            # stop (data persists in the pgdata volume)
```

## Known non-blockers (M2 follow-ups)

- **Token usage not captured** (`agent_runs.output = {}`): LiteLLM's Vertex streaming did not surface
  a usage chunk; needs `stream_options={"include_usage": True}` (or a non-stream usage call) to fill
  `agent_runs.output.usage`. Accounting fidelity only — does not affect the chat loop.
- **Disconnect/cancel finalization** (I1) is validated by reasoning + the success path (status=done);
  the true client-disconnect path (status=cancelled) was not exercised in the smoke.
- **Cloud promotion (Fase 4)** not done: buildx amd64 → Artifact Registry → `gcloud run deploy`, plus
  ensuring `PostgresSaver.setup()` lands the `langgraph` schema on Cloud SQL at first prod boot.

## Promotion (after the gate is green)

```bash
git checkout main
git merge --no-ff m1-conversation-system
git tag m1-complete
# release: v0.0.2-m1
```
