# Promotion Gates (ADR-0010)

> Sources: ADR-0010, M0 spec §17, M1 spec §10, `docs/m0-promotion.md`, `docs/m1-promotion.md`, `docs/m0-runbook.md`.

A milestone transition is gated by **explicit, machine-checkable criteria**. A gate
is a YAML block; **every item must be green and backed by a reproducible command +
observed output** — nothing is self-declared. No work on the next milestone starts
before the current gate passes (prevents contract drift / architectural debt).

## The gate pattern

1. Architect defines the gate YAML in the milestone spec (`## Promotion Criteria`).
2. Implementers make each item green.
3. QA/verification records evidence in `docs/m{n}-promotion.md` (commands + output).
4. Promote: `git checkout main && git merge --no-ff m{n}-… && git tag m{n}-complete`
   (+ release `v0.0.x-m{n}`).

## M0 → M1 gate (✅ all green — `docs/m0-promotion.md`)

```yaml
architecture: approved
contracts: frozen
adr: complete                 # ADR-0001..0010
terraform_apply: success
docker_compose: green
cloud_run: deployed
health: green
db_migrations: green          # alembic 0001_initial
zero_feature_debt: true
```
Verified live on `thesisos-prod`: 2 Cloud Run services READY (private), Cloud SQL
RUNNABLE, 15 public tables, pgvector 0.8.1, `embeddings=vector(768)`, backend 8/8,
ruff clean.

## M1 → M2 gate (🟢 local green; cloud pending — `docs/m1-promotion.md`)

```yaml
chat: working              # POST /chat streams a real Gemini response
sse: working               # token/done/error framed correctly (CRLF)
history: persistent        # messages persisted; reload in order
langgraph: single_node     # START -> conversation_node -> END
graphstate: serializable   # round-trips through the checkpointer
checkpointer: working      # PostgresSaver in `langgraph` schema; restart recovery
contracts: unchanged       # domain contracts intact (= domain_contracts)
adc: working               # Vertex via ADC; no vertex-config secret
tests: green               # M1 + M0 suites; ruff clean  (23 passed/1 skipped)
scope_creep: false         # nothing from the forbidden list shipped
```
Local stack verified against **real Vertex/Gemini** (`gemini-2.5-pro`,
`europe-west1`). **Open:** `cloud_run_deploy: pending`, `langgraph_schema_cloud:
pending`; then merge + tag `m1-complete`.

## Evidence standard (what "green" means)
- A command you can re-run + the output you observed. Examples used in the gates:
  `docker compose ps`, `curl /health` `/ready` `/chat`, `psql` schema/count checks,
  `pytest -q`, `ruff check app`, `terraform validate/apply`, `next build`.

## Zero-feature-debt check
`rg -n "NotImplementedError|wired post-M0|wired in M1" backend/app` — only intentional
stubs should appear; no half-built features.

## Anti-patterns the gate prevents
- Self-declared "done" (rubber-stamping) → every item needs evidence.
- Starting the next milestone early → contract drift; forbidden until tag exists.
- Shipping forbidden scope → `scope_creep: false` + IS-NOT lists.
