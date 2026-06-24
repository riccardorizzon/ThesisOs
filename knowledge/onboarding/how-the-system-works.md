# Onboarding: How the System Works

> A 10-minute orientation for a new agent/engineer. Pointers into the rest of the knowledge base and the repo.

## The one-liner
Single-user, Cloud-native research/thesis **AgentOS**: chat + memory + ingestion +
RAG + citations + outline + multi-agent orchestration, on Vertex AI (Gemini) +
Postgres/pgvector, built Contract-First and promoted milestone by milestone.

## Mental model in 6 facts
1. **Two agent worlds.** *Runtime* agents are LangGraph nodes inside the product
   (`contracts/agents/*.json`). *Builder* agents are Cursor agents that write the
   code (build-time only). Don't confuse them. (`agents/README.md`)
2. **One LLM vendor, behind a seam.** Everything LLM goes through
   `backend/app/llm/` → LiteLLM → Vertex. Swap by config. (ADR-0002)
3. **One graph state, frozen.** `GraphState` is the single object threaded through
   the graph; execution metadata is a separate `RunContext`. (ADR-0007/0014)
4. **Postgres is the truth.** 14 domain tables; `messages` is the chat system of
   record; the `langgraph` schema holds checkpoints (tool-owned). (ADR-0012)
5. **Contract-First + gates.** Specs/contracts freeze before code; each milestone
   passes an evidence-backed YAML gate before the next starts. (ADR-0001/0010)
6. **Seam-first.** M1 wired the whole orchestration path with **one node** so M2+
   add nodes around it without rewriting `/chat`. (M1 spec §1)

## Where things live (repo)
```text
backend/app/   api · core · llm · schemas · graph · db · services · agents · main.py
frontend/      app (App Router) · components · lib (api, store)
contracts/     openapi · agents · db (schema.sql, langgraph-owned.md) · events
decisions/     ADR-0001..0014
docs/          architecture.md · m0/m1 runbooks & promotion gates · superpowers/specs & plans
infra/         terraform · ci (cloudbuild.yaml)
plans/builder/ STATE.yaml · packets (parallel build orchestration)
knowledge/     ← you are here (the operating knowledge base)
```

## A chat turn end-to-end (the live path)
`React /chat` → `POST /chat` (SSE) → `ConversationService.stream_turn`
(persist user msg + open AgentRun, load history) → `graph.astream(... custom)` →
`conversation_node` streams via `get_stream_writer()` → `LiteLLMClient.astream` →
Vertex → tokens rise as `event: token` → on `done`, persist assistant msg +
finalize AgentRun. Lock per conversation; `409` if busy; `503` if LLM unconfigured.
(`architecture/graph.md`, `architecture/backend.md`.)

## Run it locally
```bash
cp .env.example .env
docker compose up --build
curl localhost:8000/health    # {"status":"ok"}
curl localhost:8000/ready     # {"status":"ready","db":true,"config":true}
# real chat needs GOOGLE_CLOUD_PROJECT + ADC (see docker-compose.override.yml);
# otherwise /chat returns a graceful 503 llm_not_configured
```
Backend tests: from `backend/`, `.venv/bin/python -m pytest -q` and
`.venv/bin/ruff check app`.

## Reading order for depth
`context/current-state.md` → `memory/project-memory.md` → `project/roadmap.md` →
`architecture/system-overview.md` → `development/workflow.md` +
`development/promotion-gates.md` → `context/next-actions.md`.

## Golden rules
- Don't change frozen contracts without a new ADR. Extend additively.
- Don't start the next milestone before the current gate is green + tagged.
- Don't claim "done" without a re-runnable command + observed output.
- Stay in your `owned_files` during parallel builds; respect STATE `decisions`.
