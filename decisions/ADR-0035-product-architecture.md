# ADR-0035: Product Architecture — Four Layers

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product (describes Product + boundaries to Runtime)
- **Context:** Product UX must hide engine complexity while respecting Runtime Constitution layer rules (C1–C8). RFC-001 defines Research OS with explicit separation of workspace, knowledge engine, AI, and runtime.
- **Decision:** ThesisOS Product architecture comprises **four layers**. The operator sees **Workspace (L1)** only; **Knowledge Engine (L2)** and **AI Engine (L3)** are invisible services; **Runtime (L4)** is the qualified v1.0 stack.

```text
L1  Workspace        Home · Research · Writing · Sources · Knowledge · AI panel
L2  Knowledge Engine Context · graph · memory · decisions · corpus · bibliography
L3  AI Engine        model router · actions · prompt_wire · inference enforcement
L4  Runtime          FastAPI · Postgres · LangGraph · retrieval · events
```

Dependency direction: **L1 → L2 → L3 → L4** (product calls knowledge services; knowledge services call runtime ports — never inverse UX imposed by runtime).

- **Invariants:**
  - **INV-PA-1:** L1 modules MUST NOT expose L2/L3/L4 internals (OR-7, vector DB, GraphState) in primary UI.
  - **INV-PA-2:** L2 Context Engine is mandatory for AI actions (ADR-0038); no ad-hoc prompt assembly in L1.
  - **INV-PA-3:** L3 models are swappable at composition/config without L1/L2 redesign.
  - **INV-PA-4:** L4 changes require Runtime ADR; L1–L3 changes require Product ADR or engineering program per P8.
  - **INV-PA-5:** Cross-layer features require dual approval (Constitution Governance P6).

- **Compliance checklist:**
  - [ ] **C1:** New product feature maps to L1 module or L2 service — documented in EWO
  - [ ] **C2:** No direct frontend → LLM bypass of Context Engine (except explicit power-mode escape hatch in Settings, logged)
  - [ ] **C3:** Runtime Constitution C1 layering preserved in backend wiring

- **Violation examples:**
  - Settings page exposing raw memory JSON as primary UX → INV-PA-1
  - New `/chat` path that skips Context Packet → INV-PA-2

- **References:** ADR-0034, ADR-0038, `docs/runtime-constitution.md`, `docs/product/specs/thesisos-product-ux-v1.md` §3
