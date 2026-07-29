# ADR-0056: Critic Loop & Approval Gate (M9)

- Status: **Proposed** (2026-07-29) — not Accepted; freeze at M9.0 before implementation.
- Governance: Consistent with ADR-0027 (reserved `critic` route), ADR-0031 (writer purity), ADR-0032 (`approved` lifecycle), ADR-0014 (RunContext vs GraphState), ADR-0006 (events), ADR-0007 (frozen GraphState — `critique` already exists).
- Context: M6 reserved `approved` for the Critic gate and kept the writer free of persistence. `critic.json` freezes reads `draft,retrieved_context` and writes `critique`, with errors `hallucination`/`redundancy`. Without a frozen loop bound and approval rule, builders risk unlimited revise cycles (M12 scope) or GraphState pollution.

- Decision:

  ### 1. Activate reserved `critic` route

  ```text
  route=critic ──► memory_context → retriever_node → critic_node → END
  ```

  Review-only path for an existing draft in state/checkpoint.

  ### 2. Critic is a CAPABILITY port

  ```text
  CriticCapability: async critique(brief: CriticBrief) -> CritiqueResult
  ```

  - `make_critic_node` adapts to `{critique, errors}` per `critic.json`.
  - No DB / `ChapterService` / outbox imports inside the capability (outbox via composition root / instrumentation layer after node returns).

  ### 3. Bounded revise loop on `writer` route only

  - After `writer_node`, run `critic_node`.
  - If `critique.passed` → END.
  - If not passed and `revise_count < MAX_AUTO_REVISE` → re-enter `writer_node` then `critic_node` once more → END.
  - **`MAX_AUTO_REVISE = 1`** for M9 (Architect may set 2 at freeze; never unbounded).
  - `revise_count` stored in RunContext / config, **not** GraphState.
  - `conversation` / `grounded_chat` / `citation` routes do **not** gain this loop.

  ### 4. Pass/fail & errors

  - Map unsupported claims → error `hallucination`, `passed=false`.
  - Map substantive repeated content → error `redundancy`, `passed=false` (Wave 1 blocking).
  - `Critique.issues` carries human-readable bullet strings for UI.

  ### 5. `CritiqueCompleted` event

  - Emit `{ agent_run_id, passed }` when critic node finishes (success or fail path).
  - `agent_run_id` from RunContext.

  ### 6. Approval gate

  - `status=approved` remains a `ChapterService.update_metadata` transition.
  - After M9 promotion, default policy: transition `review → approved` **requires** a recorded passing critique for the chapter's current `version`.
  - **Receipt storage (LOCKED):** `chapter_versions.metadata` on the critiqued version head — keys `critic_passed`, `agent_run_id`, `at`. No `critique_receipts` table in M9.
  - Critic never writes `approved` itself.

  ### 7. Separation from M10 QA

  - Critic = groundedness + redundancy on draft vs retrieved context.
  - M10 QA = independent process/phase verification (`agent_steps.phase='qa'`). Must not be implemented under M9.

- Consequences: Trustworthy approval path; latency bounded; writer stays a pure capability. Cost: extra LLM calls on writer route; false positives need fixture tuning.

- Alternatives considered:
  - **Critic-only route, no writer loop** — rejected as sole design; backlog requires revise loop (T083).
  - **Unlimited revise until pass** — rejected (cost/latency; M12 territory).
  - **Put revise_count in GraphState** — rejected (ADR-0007/0014).
  - **Auto-publish on pass** — rejected; `published` is M8/user explicit.

- References: M9 design spec `docs/superpowers/specs/2026-07-29-thesisos-m9-critic-design.md`; `contracts/agents/critic.json`; ADR-0032 §3; `contracts/events/events.json`.
