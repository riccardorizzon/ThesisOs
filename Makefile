# ThesisOS — developer + CI validation pipeline (MB1 Phase 0).
# Single deterministic entry point for every validation stage. Reuses the
# existing toolchain (backend/.venv, frontend/node_modules) — no new deps.
# Spec: docs/superpowers/specs/2026-06-25-thesisos-mb1-workflow-engine-design.md (§7)
# ADR:  decisions/ADR-0023-build-workflow-engine.md

SHELL    := /bin/bash
PYTHON   ?= python3
BACKEND  := backend
FRONTEND := frontend
RUFF     := $(BACKEND)/.venv/bin/ruff

.DEFAULT_GOAL := help

.PHONY: help install ensure-test-db lint format format-fix typecheck unit unit-frontend unit-builder-engine test \
        drift scope isolation check ci up down status unit-m4-recovery dogfood-m4 qualify-m5 dogfood-m5 qualify-m6 dogfood-m6 dogfood-m7

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- setup -------------------------------------------------------------------
install: ## Install backend (editable, dev) + frontend deps
	cd $(BACKEND) && $(PYTHON) -m venv .venv && .venv/bin/pip install -e ".[dev]"
	cd $(FRONTEND) && npm ci

ensure-test-db: ## Create thesisos_test and run Alembic migrations
	bash bin/ensure-test-db.sh

# --- validation stages (reuse existing commands) -----------------------------
lint: ## ruff lint (backend app)
	$(RUFF) check $(BACKEND)/app

format: ## ruff format --check (backend app) — NOT yet in the enforced gate
	$(RUFF) format --check $(BACKEND)/app

format-fix: ## Apply ruff formatting to the backend (adoption step)
	$(RUFF) format $(BACKEND)/app

typecheck: ## tsc --noEmit (frontend)
	cd $(FRONTEND) && npx tsc --noEmit

unit: ensure-test-db ## backend pytest (isolated thesisos_test DB)
	cd $(BACKEND) && .venv/bin/python -m pytest -q

unit-frontend: ## frontend vitest
	cd $(FRONTEND) && npm run test

unit-builder-engine: ## builder_engine pytest (MB1 Phase 1)
	cd builder_engine && (test -d .venv || python3 -m venv .venv) \
		&& .venv/bin/pip install -q -e ".[dev]" \
		&& .venv/bin/pytest -q

drift: ## DB schema / contract drift test
	cd $(BACKEND) && .venv/bin/python -m pytest -q tests/test_schema_snapshot.py

scope: ## scope-creep guard (informational: stubs must be milestone-tagged)
	@echo "Scope-creep scan (review any matches — must be intentional milestone stubs):"
	@rg -n "NotImplementedError|wired post-M|wired in M[0-9]" $(BACKEND)/app \
		--glob '!**/__pycache__/**' || echo "  (none)"

isolation: ## build-time sidecars must not import the runtime (ADR-0019/0023)
	@for dir in builder_memory builder_engine; do \
		! rg -n "^[[:space:]]*(from|import)[[:space:]]+backend([[:space:].]|$$)" $$dir 2>/dev/null \
			|| { echo "isolation FAIL: $$dir imports backend.app"; exit 1; }; \
	done

# --- aggregates --------------------------------------------------------------
# NOTE: `format` is intentionally NOT in `check`/`ci` yet — the M0–M2 code
# predates ruff-format. Adopt it deliberately: run `make format-fix`, commit the
# reformat as one isolated change, then add `format` back to the gate below.
check: lint typecheck unit drift isolation ## Fast local gate (pre-commit / pre-push)

test: unit unit-frontend unit-builder-engine ## All unit suites

ci: lint typecheck unit unit-frontend unit-builder-engine drift scope isolation validate-platform-classification ## Full CI gate

validate-platform-classification: ## ASEP registry ↔ proposal platform_contract (governance)
	cd builder_engine && (test -d .venv || python3 -m venv .venv) \
		&& .venv/bin/pip install -q -e ".[dev]" \
		&& .venv/bin/builder-engine validate-classification --repo-root ..

unit-m4-recovery: ## M4 recovery regression suite (53 tests; needs Postgres for some)
	cd $(BACKEND) && .venv/bin/python -m pytest -q \
		tests/test_grounding.py \
		tests/test_embedding_batching.py \
		tests/test_retrieval_service.py \
		tests/test_index_observability.py \
		tests/test_markdown_ingestion.py \
		tests/test_document_parsers.py \
		tests/test_retriever_node.py \
		tests/test_search_api.py \
		tests/test_packaging.py

dogfood-m4: ## End-to-end M4 product smoke (requires: make up, Vertex ADC)
	@bash bin/dogfood-m4-run.sh

qualify-m5: ensure-test-db ## M5 Runtime Qualification suite (runtime + integration + routing eval)
	cd $(BACKEND) && .venv/bin/python -m pytest -q \
		tests/test_runtime_event_contract.py \
		tests/test_runtime_event_bus.py \
		tests/test_runtime_subscribers.py \
		tests/test_runtime_observability.py \
		tests/test_conversation_task_lifecycle.py \
		tests/test_m5_chat_integration.py \
		tests/test_m5_routing_eval.py

dogfood-m5: ## End-to-end M5 orchestrated chat smoke (requires: make up, Vertex ADC)
	@bash bin/dogfood-m5-conversation-run.sh

qualify-m6: ensure-test-db ## M6 Writing Qualification suite (writer route + chapter store + eval)
	cd $(BACKEND) && .venv/bin/python -m pytest -q \
		tests/test_writer_node.py \
		tests/test_m6_writer_route.py \
		tests/test_chapter_service.py \
		tests/test_chapters_api.py \
		tests/test_m6_writing_integration.py \
		tests/test_m6_writing_eval.py

dogfood-m6: ## End-to-end M6 writing smoke: draft a chapter + save (requires: make up, Vertex ADC)
	@bash bin/dogfood-m6-writing-run.sh

dogfood-m7: ## M7 full workflow smoke: API dogfood + Playwright UI (requires: stack or Vertex ADC for indexing)
	@bash bin/dogfood-m7-run.sh
	@cd tests/e2e && npx playwright test m7-product-flow.spec.ts

beta-validator-rc: ## RC beta validation — staging health + 6 surfaces + context API
	@bash bin/beta-validator-rc.sh

# --- developer cockpit -------------------------------------------------------
status: ## "Where are we?" — read-only product/ASEP/infra snapshot
	@bash bin/status.sh

# --- local stack -------------------------------------------------------------
up: ## Start local stack (docker compose)
	docker compose up --build -d

down: ## Stop local stack
	docker compose down
