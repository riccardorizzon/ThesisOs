# ADR-0029: Behavioral Semantics Layer

- Status: Accepted (frozen 2026-06-25)
- Context: DR-001 and Architect sign-off (2026-06-25) identified that L2 GSM defines **what transitions are valid** but not **why objects collaborate**. Without an explicit semantics layer, implementers infer intent from transition tables — causing drift as MB2+ adds modules. Architect approved inserting Behavioral Semantics between L1 (laws) and L2 (states) as a constitutional clarification, not a redesign.
- Decision:

  1. **Introduce `docs/platform/behavioral-semantics.md`** as the canonical semantics layer between L1 and L2.

  2. **Updated constitution stack:**

     ```text
     L0  Engineering Meta Model      who exists
     L1  Invariant Model               laws
     BS  Behavioral Semantics          why objects collaborate
     L2  Global State Machine          valid transitions
     L3  Engineering Runtime Cycle     when transitions run
     L4+ Implementation
     ```

  3. **Behaviors are not states or objects.** They are named collaboration patterns (Scheduling, Claiming, Delegation, Promotion, Retry, Recovery, Escalation, Observing, Freezing, Validating, Merging, Replanning) mapping to existing L2 transition IDs.

  4. **Engineering Traceability Matrix extended** with **Behavior**, **Event**, and **Observability** columns — Event = semantic fact emitted; Observability = evidence the behavior occurred (distinct from event).

  5. **L2 micro-patch (L2.1)** approved as constitutional clarification only: Goal guards, Task birth (T-00), C-07 owner split — no new features.

  6. **MB2 rebase authorized** only after L2.1 + ETM extension + Behavioral Semantics freeze (this ADR).

- Consequences: Implementers trace code to Behavior → Transition → Invariant → L0 → Vision. LLM workers remain interchangeable executors. Cost: one additional document to maintain; mitigated by behavior table stability.

- Alternatives considered:
  - Fold semantics into L2 — rejected; mixes *why* with *what*, bloats transition table.
  - Skip semantics until MB3 — rejected by Architect as natural bridge; low cost now.
  - Add behaviors as L0 objects — rejected; behaviors are patterns, not entities.

- References: ADR-0028, DR-001, `behavioral-semantics.md`, `engineering-traceability-matrix.md`, `global-state-machine.md`.
