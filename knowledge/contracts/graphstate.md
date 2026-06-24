# Contract: GraphState (FROZEN — ADR-0007)

> Sources: `backend/app/schemas/graph_state.py`, M0 spec §10, `docs/architecture.md` §6, `contracts/agents/*.json`, ADR-0007/0011/0014.

`GraphState` is the **single shared Pydantic state object** threaded through the
LangGraph. It is **frozen**: no field may be added/removed/retyped without a new
ADR. Each agent declares which fields it reads/writes in `contracts/agents/<name>.json`.

## Definition (current code)

```python
class GraphState(BaseModel):
    messages: list[Message]
    plan: Plan | None = None
    route: str | None = None
    retrieved_context: list[RetrievedChunk] = Field(default_factory=list)
    draft: str | None = None
    citations: list[CitationRef] = Field(default_factory=list)
    memory_ops: list[MemoryOp] = Field(default_factory=list)
    critique: Critique | None = None
    task: TaskRef | None = None
    errors: list[AgentError] = Field(default_factory=list)
```

## Field ownership (which agent/milestone writes each)

| Field | Type | Written by | Milestone |
|-------|------|-----------|-----------|
| `messages` | `list[Message]` | conversation_node (caller-built from DB) | M1 |
| `plan` | `Plan?` | supervisor, planner | M5 |
| `route` | `str?` | supervisor, router | M5 |
| `retrieved_context` | `list[RetrievedChunk]` | retriever | M4 |
| `draft` | `str?` | writer (conversation_node sets it in M1) | M6 |
| `citations` | `list[CitationRef]` | writer, citation | M6/M7 |
| `memory_ops` | `list[MemoryOp]` | memory | M2 |
| `critique` | `Critique?` | critic | M9 |
| `task` | `TaskRef?` | planner | M5 |
| `errors` | `list[AgentError]` | document, any node | M3+ |

## Sub-models

```python
Message(role: str, content: str)
Plan(steps: list[str] = [])
RetrievedChunk(chunk_id: str, score: float, content: str)
CitationRef(source_id: str, locator: str | None = None)
MemoryOp(op: str, kind: str, key: str, content: str | None = None)   # op: upsert|delete
Critique(issues: list[str] = [], passed: bool = False)
TaskRef(id: str, title: str)
AgentError(agent: str, message: str)
```

## Invariants (do not violate)

1. **Frozen shape (ADR-0007).** No new fields without an ADR. M1 deliberately did
   NOT add fields for streaming/usage/execution.
2. **Serializable with defaults intact (M1 spec §5/§9).** Every field has an
   explicit default so it round-trips cleanly through the checkpointer; in M1 only
   `messages` is populated.
3. **No execution metadata here (ADR-0014).** `conversation_id`, `trace_id`,
   `request_id`, etc. live in `RunContext`, never in `GraphState`. (Tested:
   `"conversation_id" not in GraphState.model_fields`.)
4. **No `add_messages` reducer (M1).** The caller owns history (DB = system of
   record); nodes use replace semantics on `messages`.
5. **Usage is not a GraphState field.** Token usage is carried via the custom
   stream and recorded on `agent_runs` (ADR-0014).

## Why frozen
Freezing `GraphState` early lets M2–M18 add nodes that read/write existing fields
without churning the checkpoint format or every node signature — the seam-first
strategy (M1 spec §1, ADR-0001).
