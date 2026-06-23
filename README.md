# ThesisOS

Single-user research & thesis-writing AgentOS. Runtime LLM: Vertex AI (Gemini + multilingual
embeddings). Storage: Postgres + pgvector. Runs on GCP (Cloud Run + Cloud SQL).

## Status
M0 (Foundations): architecture, contracts, scaffolding, infra. No product features yet.

## Layout
- `backend/`  — FastAPI app (Python)
- `frontend/` — Next.js app
- `contracts/` — OpenAPI, agent I/O, DB schema, events
- `decisions/` — ADRs
- `infra/` — Terraform + CI/CD
- `docs/` — architecture + specs/plans

## Local dev
    cp .env.example .env
    docker compose up --build
    curl localhost:8000/health   # {"status":"ok"}
