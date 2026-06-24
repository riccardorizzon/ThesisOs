# Contract: RunContext (ADR-0014)

> Sources: `backend/app/schemas/run_context.py`, M1 spec §5, ADR-0014, `backend/app/services/conversation/service.py`.

`RunContext` is the **runtime-only execution object**, kept strictly separate from
`GraphState`. It carries *who/which run/trace* — never domain reasoning state.

## Definition (current code)

```python
class RunContext(BaseModel):
    conversation_id: str
    agent_run_id: str
    trace_id: str
    request_id: str
    user_id: str | None = None      # always None while single-user (ADR-0001)
    metadata: dict = Field(default_factory=dict)
```

## Rules (ADR-0014)

1. **Separate from GraphState.** Domain fields never go into `RunContext`;
   execution fields never go into `GraphState`.
2. **Runtime-only.** It is passed alongside the graph invocation (LangGraph
   config/`configurable`) and **MUST NOT** be persisted into the checkpoint.
   Checkpoints carry domain working state only; execution metadata lives only for
   the duration of the run.
3. **Accounting attaches here, not on domain rows.** Token usage / run bookkeeping
   records on `agent_runs` (via `RunContext`), not on `messages`, so future
   per-agent accounting (planner/retriever/critic) needs no domain change.

## Current usage (M1)

In `ConversationService.stream_turn`, a `RunContext` is built per turn:
- `agent_run_id` generated up front so the run id is consistent across the
  transaction.
- `trace_id` / `request_id` generated as UUIDs.
- `conversation_id` from the (created or existing) conversation.
- `trace_id` + `request_id` are stored on `agent_runs.input`
  (`{"trace_id":..., "request_id":...}`) — trace propagation.

> M1 builds and records `RunContext` but does not yet pass it *into* the graph
> config; that wiring deepens in M11 (tracing) / M12 (per-agent accounting). The
> contract and boundary are frozen now so that retrofit is unnecessary.

## Why it exists
Without `RunContext`, execution ids would bloat the frozen `GraphState`, pollute
every checkpoint with transport data, and force frozen-contract changes in M12. The
clean execution/domain boundary is established now (seam-first).
