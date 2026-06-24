# How to Add a (Runtime) Agent

> For adding a LangGraph node to the orchestration graph. Sources: `backend/app/graph/conversation.py`, `contracts/agents/*.json`, M1 plan Tasks 7–10, ADR-0007/0014, `architecture/graph.md`.

A "runtime agent" is a node in the `StateGraph(GraphState)`. The seam is frozen
(M1); you **extend** it — you do not rewrite `/chat`.

## Prerequisites
- The agent already has (or you add, via the Architect) a contract
  `contracts/agents/<name>.json` declaring `reads_state`, `writes_state`, `errors`,
  `state_mutations`, and `milestone`.
- A **frozen design spec** for the milestone that introduces it (ADR-0001).
- The fields it reads/writes already exist on `GraphState` (they were pre-frozen in
  M0). **Do not add `GraphState` fields without a new ADR.**

## Steps (TDD)
1. **Write the contract** (if not present): `contracts/agents/<name>.json`. Keep it
   consistent with the existing 9 (same shape).
2. **Write the failing node test** in `backend/tests/` using a **fake `LLMClient`**
   and `InMemorySaver` — assert the node's `GraphState` mutations and any streamed
   chunks. (Pattern: `test_conversation_graph.py`.)
3. **Implement the node** in `backend/app/graph/` (or `backend/app/agents/`):
   ```python
   def make_<name>_node(deps):
       async def <name>_node(state: GraphState) -> dict:
           # read only the contract's reads_state fields
           # ... do work (call services / llm via the seam) ...
           return {"<written_field>": ...}   # only writes_state fields; replace/append per contract
       return <name>_node
   ```
   - Stream user-visible tokens via `get_stream_writer()` ({"type":"token",...}) if
     it produces text.
   - Put execution metadata in `RunContext`, never in `GraphState` (ADR-0014).
   - Respect the mutation semantics in the contract (`set` vs `append`).
4. **Wire it into the graph** (extend `build_graph`): `g.add_node(...)` and the
   edges that place it relative to Supervisor/Router and the conversation node. Do
   not break the existing `START → conversation_node → END` behavior for plain chat.
5. **Service integration:** if it needs DB/services, add them via the async session;
   keep `messages` as the system of record.
6. **Events/telemetry:** emit any catalog event it owns (e.g. memory →
   `MemoryUpdated`); record steps in `agent_steps` with the right `phase`.
7. **Tests green + ruff clean**, then commit (`feat(m{n}): <name> agent node`).
8. **Update OpenAPI** for any endpoint the agent backs (realize the `x-milestone`
   stub).
9. **Gate:** add the agent's behaviors to the milestone's promotion criteria.

## Hard rules
- Only read/write the `GraphState` fields your contract declares.
- Never widen `GraphState`/`TokenChunk` or persist `RunContext` into the checkpoint.
- Keep the chat seam working; new nodes go **around** it.
- Update the agent's doc under `knowledge/agents/`.

## Reference: contract shape
```json
{ "agent": "<name>", "milestone": "M<n>",
  "input":  { "reads_state":  ["..."] },
  "output": { "writes_state": ["..."] },
  "errors": ["..."],
  "state_mutations": { "<field>": "set|append" } }
```
