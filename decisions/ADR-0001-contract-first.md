# ADR-0001: Contract First

- Status: Accepted (frozen 2026-06-23)
- Context: ThesisOS is built milestone by milestone by Cursor agents, where each later milestone (M1–M18) adds one vertical slice. If product features were written before the architecture, API contracts, and data schemas were stable, every slice would build on shifting foundations, accumulating integration debt and forcing painful rewrites as interfaces changed underneath working code.
- Decision: We produce the architecture, the API/agent/event contracts, and the database schemas before writing any product code. No feature code is written until the M0 gate passes; M0 delivers only docs, contracts, scaffolding, and a deployable health shell.
- Consequences: This forbids chat, RAG, ingestion, memory engine, and agent implementations in M0 — anything that produces a user-visible feature is out of scope until the gate passes. In exchange it enables stable, frozen contracts so that M1+ slices integrate cleanly against known interfaces instead of moving targets.
- Alternatives considered: Walking-skeleton-first (build a thin end-to-end feature path immediately, then harden) was rejected because it front-loads product code against unstable interfaces and produces contract debt that compounds across every subsequent milestone.
