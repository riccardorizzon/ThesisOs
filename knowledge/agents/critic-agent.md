# Critic Agent (Runtime)

> Type: Runtime LangGraph node **and** an AgentOS loop phase. Milestone: **M9**. Status: designed (contract frozen), not implemented. Sources: `contracts/agents/critic.json`, M0 spec §10, `contracts/events/events.json` (`CritiqueCompleted`), `backend/app/db/models.py` (`agent_steps.phase` includes `critic`), `development/workflow.md`.

## Mission
Review drafts for quality and grounding — catch hallucinations, redundancy, and
unsupported claims — before content is promoted. The Critic is both a runtime agent
(reviews thesis drafts) and the **Critic step** of the AgentOS build loop.

## Responsibilities (runtime, M9)
- Evaluate `draft` against `retrieved_context`; flag issues; set pass/fail.
- Emit `CritiqueCompleted { agent_run_id, passed }`.
- Gate the Writer→(revise) loop.

## Inputs (contract)
- `reads_state`: `draft`, `retrieved_context`.

## Outputs (contract)
- `writes_state`: `critique` (`state_mutations: critique = set`).
- `Critique { issues: list[str], passed: bool }`.

## Allowed actions
- Read `draft`/`retrieved_context`; produce structured critique; emit
  `CritiqueCompleted`; request a revise.

## Forbidden actions
- Rewriting the draft itself (it critiques; Writer revises).
- Mutating `GraphState` fields other than `critique`; adding fields (frozen).

## Dependencies
- **M6 Writer** (`draft`), **M4 Retriever** (`retrieved_context`), **event bus**.
  Pairs with the **QA agent** (M10).

## Promotion criteria (M9 gate, to be frozen in the M9 spec)
- Detects hallucination/redundancy; `critique.passed` gates promotion of content;
  `CritiqueCompleted` emitted; revise loop works.

## Failure modes (contract)
- `hallucination` — claim unsupported by context.
- `redundancy` — repeated/duplicative content.
- (Design risk) false negatives (misses a real issue) — mitigated by QA (M10) as a
  second gate.

## As an AgentOS phase
In the build loop (Observe→Hypothesis→Plan→Implement→Test→**Critic**→Revise→
Promote), "Critic" is the self/peer review step before promotion — implemented by
builder review subagents (e.g. `code-reviewer`, Bugbot) and recorded in
`agent_steps.phase = 'critic'`. See `development/workflow.md`.
