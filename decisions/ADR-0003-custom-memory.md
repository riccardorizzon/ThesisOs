# ADR-0003: Custom Memory Layer

- Status: Accepted (frozen 2026-06-23)
- Context: ThesisOS needs long-term memory that the single user can read, edit, and trust — preferences, thesis scope, concepts, citations, decisions, and a Notion-like editable page injected into the system prompt. This memory must be structured, manually editable, versioned, and able to reference documents, which is a poor fit for automatic-extraction memory systems.
- Decision: We build a custom memory layer on Postgres + pgvector with six editable, versioned kinds (user, thesis, concept, citation, decision, editable), all stored in a `memories` table with a `kind` discriminator. No Mem0 is used in the core.
- Consequences: We get full control over memory shape, manual editing, explicit versioning, and document references — exactly what a research/thesis workflow needs. The cost is that we own the memory engine ourselves rather than delegating to an off-the-shelf library, and automatic memory extraction is not provided at this stage.
- Alternatives considered: Mem0 was deferred to M15–M16 because its automatic-extraction model is not a fit for structured, manually-editable, versioned memory; it may be revisited later for opportunistic extraction on top of the custom layer.
