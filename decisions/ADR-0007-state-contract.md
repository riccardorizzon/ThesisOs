# ADR-0007: Shared Graph State Contract

- Status: Accepted (frozen 2026-06-23)
- Context: The agent hierarchy (Supervisor → Planner → Router → Retriever/Writer/Critic/Citation/Memory/Document) passes data between many nodes. If each agent invented its own payload shape, integrating nodes into the graph would be chaotic, error-prone, and impossible to reason about as the number of agents grows.
- Decision: A single shared Pydantic `GraphState` is the one state object passed through the entire graph across all agents. Each agent declares exactly which `GraphState` fields it reads and writes in its `contracts/agents/*.json` contract (input, output, errors, and state mutations).
- Consequences: There is one canonical, typed state contract, so node integration is predictable and each agent's effect on shared state is explicit and reviewable. The trade-off is that `GraphState` becomes a shared schema all agents depend on, so changes to it are coordinated rather than local — which is exactly the discipline we want.
- Alternatives considered: Per-agent ad-hoc payloads were rejected because divergent, undeclared state shapes lead to integration chaos and make it impossible to know which node touches which field.
