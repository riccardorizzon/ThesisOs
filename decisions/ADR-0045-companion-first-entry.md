# ADR-0045: Companion-first Product Entry

**Status:** Accepted for Product Constitution v1.1 draft  
**Date:** 2026-07-23  
**Plane:** Product  
**Decision authority:** Explicit Architect authorization  
**Supersedes on v1.1 ratification:** ADR-0036 `INV-IA-2`; ADR-0039 `INV-AI-1`, `INV-AI-5`  
**Related:** ADR-0034, ADR-0035, ADR-0038, ADR-0044

## Context

The owned thesis project already contains chapters, sources, decisions, knowledge, memory,
Writing and Review workflows. A dashboard-first entry forces the author to reconstruct the
current task before working. The Companion can instead resume the real thesis state and route
the author to those existing modules.

This is not a repositioning of ThesisOS as a generic chatbot. ThesisOS remains a Research
Operating System; conversation becomes its default continuity and orchestration surface.

## Decision

1. `/` renders **Thesis Companion** for the active owned project.
2. The opening surface loads a canonical resume packet: project identity, progress, focus,
   next action, session summary and approved-for-continuation artifact.
3. The Companion exposes direct actions to Writing, Review and Sources. The sidebar and
   Command Palette continue to expose the complete Research OS.
4. `/ai` remains a compatibility alias for the same conversation capability; `/chat` remains
   legacy.
5. `project_id` is propagated through HTTP, conversation persistence and LangGraph config.
   Thesis knowledge must never leak into demo or other owned projects.
6. Companion pillars (`CONTINUE`, `REVIEW`, `WRITE`, `PRESERVE`, `SAVE`) are runtime
   behavior, not frontend-only prompt text.
7. Chat may draft and preserve a session artifact, but MUST NOT silently mutate a definitive
   chapter. Chapter changes continue through Writing/versioning and Review/proposal gates.
8. Sources returned by grounded generation and Companion repair replacements are visible in
   the chat stream.

## Invariants

- **INV-COMP-1:** ThesisOS remains a Research Operating System, not a generic chatbot.
- **INV-COMP-2:** The Companion is the default entry, not the sole workspace.
- **INV-COMP-3:** Writing, Review, Sources, Knowledge and Research remain independently
  addressable product modules.
- **INV-COMP-4:** Knowledge files are authoritative for thesis identity and progress; runtime
  DB/memory are versioned operational stores reconciled from that source.
- **INV-COMP-5:** No definitive academic text is persisted from chat without an explicit
  product write/review action.
- **INV-COMP-6:** Project isolation applies to context, chapters, retrieval, memory and
  conversation state.

## Consequences

- The former Home dashboard is absorbed into the Companion resume card and module actions.
- ADR-0036 and ADR-0039 remain historical v1.0 decisions; they are not edited in place.
- Product Constitution v1.1 must reference this ADR before it can supersede v1.0.
- Writing keeps its lateral AI panel for selection-aware actions and proposal creation.

## Compliance

- Home renders the real thesis title and current focus.
- A real continuation turn receives the Companion resume and project-scoped context.
- Writing, Review, Sources and Knowledge remain reachable and pass the M7 E2E flow.
- Full repository CI and non-mutating product E2E must pass before release.
