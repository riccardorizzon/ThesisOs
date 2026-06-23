# ADR-0006: Event-Driven Architecture

- Status: Accepted (frozen 2026-06-23)
- Context: As ThesisOS grows, actions like uploading a document, creating chunks, updating memory, creating chapters, and completing critiques will need to trigger downstream work and leave an audit trail. Hardwiring these as direct function calls would make the system rigid, untraceable, and impossible to scale or reroute later.
- Decision: We define a typed event catalog plus an in-process dispatcher, with all events persisted to an `events` outbox table. The initial catalog is DocumentUploaded, ChunkCreated, MemoryUpdated, ChapterCreated, and CritiqueCompleted. The dispatcher is designed to be Pub/Sub-pluggable later without changing producers or consumers.
- Consequences: This gives a durable audit trail (the outbox) and a clear future scaling path to Cloud Pub/Sub, while staying simple in M0 where only the interface, catalog, and table ship — no producers or consumers are wired. The cost is a small amount of indirection over plain function calls.
- Alternatives considered: Direct function calls only were rejected because they offer no future scaling path and no audit trail, coupling producers tightly to consumers and blocking later distribution of work.
