# ADR-0025: Builder Execution State Machine

- Status: Accepted (frozen 2026-06-25)
- Context: MB1 Phase 1 shipped CLI commands (`lint-graph`, `status`, `ready`) that encode orchestration logic. Continuing Phase 2 as command-centric risks baking ad-hoc transitions that conflict with product milestones (e.g. M4 retrieval jobs) and prevents future surfaces (API, Web UI, remote orchestration). The project is evolving from "agent skills" to a **software-engineering workflow execution engine** where agents are workers, not the architecture.
- Decision:
  1. **Introduce a formal execution state machine** for build-time **packets** (not runtime LangGraph tasks). Canonical states:
     ```text
     CREATED → READY → CLAIMED → RUNNING → VALIDATING → MERGED → DONE
                                    ↘ FAILED → DEBUGGING → READY
     ```
  2. **MB1 Phase 2+ internal runtime loop** (deterministic core):
     ```text
     State → Planner → Scheduler → Executor → Validator → StateUpdate
     ```
     CLI commands (`lint-graph`, `status`, `ready`, `schedule`, `sync`) are **views/projections** on this runtime — not the runtime itself.
  3. **STATE.yaml packet `status` maps to machine states:** `ready`≈READY, `in_progress`≈RUNNING|CLAIMED, `done`≈DONE, `blocked`≈FAILED/DEBUGGING, `cancelled` terminal.
  4. **Validators run only in VALIDATING**; merge/eligibility only after VALIDATING passes (CheckRunner). No packet reaches DONE without evidence.
  5. **Executors remain LLM agents** (Cursor Task builders). The engine never generates product code (ADR-0023).
  6. **Product milestone specs (M-series) freeze before engine phases that depend on their job/state semantics** — e.g. M4 spec before MB1 schedule/sync that might enqueue embedding validation stages.
- Consequences: One engine can serve CLI, CI, and future UI; transitions are testable without LLM; clearer separation of control vs execution. Cost: Phase 2 implementation is larger than adding `schedule`/`sync` commands alone — requires runtime module + state machine tests first.
- Alternatives considered:
  - Command-only Phase 2 (original MB1 §10) — rejected after architecture review (2026-06-25) — risks encoding wrong abstractions before M4 spec freeze.
  - External workflow engine (Temporal, etc.) — rejected in ADR-0023.
