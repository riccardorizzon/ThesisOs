## Summary

<!-- What changed and why (1–3 sentences). -->

## Layer

<!-- REQUIRED. Every PR touching backend/app MUST declare its primary layer. -->

- [ ] **Business** — domain agents, domain services, agent contracts
- [ ] **Runtime** — graph composition, lifecycle, RunContext, Event Bus, subscribers
- [ ] **Infrastructure** — DB, LLM, storage, external adapters
- [ ] **Docs / ADR only** — no runtime code

## Review checklist (Constitution C7 → ADR-0030)

Run the full **Architecture Decision Checklist** (`docs/architecture-decision-checklist.md`). Summary:

1. **Constitution** — no C1–C8 invariant violated (`docs/runtime-constitution.md`)
2. **Layer** — does this code belong to the declared layer? No new cross-layer deps?
3. **Contracts** — public contracts / event shapes unchanged or explicitly versioned (ADR for incompatible changes)?
4. **Events** — Business emits no telemetry/logging/event-bus calls directly? (C3, R8)
5. **Feature / Performance / Code** — logic, tests, no M4 regression (C6)
6. `make ci` + `make unit-m4-recovery` green (if code changed)

## Test plan

- [ ] Unit tests added/updated
- [ ] Integration / behavior tests (if applicable)
- [ ] Regression gates run locally
