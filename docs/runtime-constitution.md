# Runtime Constitution v1

> **Architectural invariants of the Runtime Platform.** This Constitution defines the
> invariants the Runtime Platform must preserve. ADRs explain *why* a decision was
> taken; the Constitution defines *what cannot change* without an explicit
> architectural decision. **In case of conflict, ADRs and implementation plans must
> remain consistent with these invariants.** ASEP remains the overall governance
> framework (ADR-0026, unchanged); this document governs the Runtime Platform only.
>
> **Scope:** the **ASEP Runtime Platform** — the Product Plane runtime subsystem
> (`backend/app/`: Event Bus, contracts, lifecycle, observability). ASEP remains the
> whole ecosystem (ADR-0026, unchanged); the Runtime Platform is a subsystem of it
> (taxonomy in ADR-0030 §0). Engineering Runtime (`builder_engine/`) keeps its own
> boundary (ADR-0023, ADR-0026).
>
> **Amendment rule:** An article changes only via a new ADR that names the article
> and bumps this document's version. Amendments are expected to be **rare**.

---

## C1 — Layering

```text
Business → Runtime → Infrastructure
```

Dependencies flow downward only. **Inverse dependencies are forbidden**
(Infrastructure → Runtime, Runtime → Business, Infrastructure → Business).

## C2 — Composition Root

Only the composition root (`build_graph()`, `ConversationService`, test fixtures)
may bind Business, Runtime, and Infrastructure together. Concrete wiring lives
nowhere else.

## C3 — Business Purity

Business Logic does not know about:

- database / persistence
- telemetry
- logging
- event bus
- LangGraph

Business depends only on injected ports, hooks, and domain types.

## C4 — Runtime Events

The Runtime emits **only canonical events**. Subscribers (telemetry, logging,
tracing, UI, export) are **replaceable** and must not be required for a turn to
succeed. The Event Bus does not know what subscribers do.

## C5 — Stable Contracts

Public agent contracts (`contracts/agents/*.json`), `GraphState`, the `/chat`
external shape, and the canonical event vocabulary are **versioned**.
Incompatible changes require an ADR.

## C6 — M4 Compatibility

Every change MUST demonstrate it does not alter validated M4 behavior, unless an
explicit architectural decision (ADR) authorizes it. This generalizes to any
milestone already qualified and frozen.

## C7 — Review Order

Every review proceeds in this order:

1. Constitution
2. Layer
3. Contracts
4. Events
5. Feature
6. Performance
7. Code

## C8 — Extension Rule

New agents, subscribers, or runtime components are added **only** through
documented extension points (`docs/runtime-contract.md`). Direct dependencies
between modules in different layers are forbidden — extension goes through the
composition root and declared ports.

---

## Status

- **Version:** v1 (2026-06-28)
- **Authority:** Defines the architectural invariants of the Runtime Platform; ADRs
  and implementation plans must stay consistent with them. ASEP-wide governance
  remains ADR-0026.
- **Enforced by:** ADR-0030 (layer rules R1–R8), `docs/runtime-contract.md`
  (extension points), `docs/architecture-decision-checklist.md` (per-PR review),
  `.github/pull_request_template.md` (review order), `make ci` gates.
- **Change log:** v1 — initial articles C1–C8.
