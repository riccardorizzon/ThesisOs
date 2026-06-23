# ADR-0010: Milestone Promotion Gates

- Status: Accepted (frozen 2026-06-23)
- Context: A milestone-driven build is vulnerable to scope creep and half-built features if "done" is judged subjectively. Without explicit, verifiable exit criteria, a milestone can be declared complete while contracts are still in flux or infrastructure is unproven, undermining every slice that follows.
- Decision: Each milestone transition is gated by explicit, machine-checkable criteria (see spec §17). The M0→M1 gate requires all of: architecture approved, contracts frozen, ADRs complete, `terraform apply` success, docker-compose green, Cloud Run deployed, health green, DB migrations green, and zero feature debt.
- Consequences: Promotion becomes objective and auditable; a milestone cannot advance until its criteria are demonstrably true, which prevents scope creep and forbids starting forbidden work (chat, LangGraph runtime, RAG, ingestion, memory engine, UI feature components) before the gate passes. The cost is upfront rigor in defining and checking criteria for each transition.
- Alternatives considered: Ad-hoc "feels done" promotion was rejected because subjective judgment invites scope creep and half-built features to slip across milestone boundaries.
