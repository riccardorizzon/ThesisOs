# ADR-0028: Engineering Meta Model & Invariant Layer

- Status: Accepted (frozen 2026-06-25)
- Context: Era I delivered a **dynamics** model (`docs/platform/runtime-model.md`, the 10-phase cycle) and a **partial state** model (ADR-0025, packet-level FSM). It has no single declaration of the **objects** those models operate on, and it conflates two different things under "policy" (ADR-0026 §8 lumps invariants in with policies; `runtime-model.md` §3.2 lists "policy set (ADR + YAML + invariants)"). As Era II spawns more components (event bus, policy engine, adaptive planner) the dominant risk is **concept drift** — parts of the platform evolving slightly different notions of "task", "frozen", "promotion". Architecture review (2026-06-25) concluded a semantic layer must be frozen **before** MB2 implementation, and that the just-frozen MB2 spec (`495cdca`) is scoped one layer too low (it starts at the event bus / L4).
- Decision:

  1. **Introduce a layered platform constitution.** L0–L3 are formalization (frozen docs, no feature code); L4+ are implementation.

     ```text
     L0  Engineering Meta Model   objects + relations      docs/platform/engineering-meta-model.md   (NEW, frozen)
     L1  Invariant Model          laws, fail-closed        docs/platform/invariant-model.md          (NEW, frozen)
     L2  Global State Machine     project+packet states    extends ADR-0025                          (next)
     L3  Engineering Runtime Cycle dynamics                docs/platform/runtime-model.md            (already frozen)
     L4  Event Bus                communication            MB2 implementation
     L5  Policy Engine            tunable decisions        MB2/MB3 implementation
     L6  Adaptive Planner         planning intelligence    MB3 implementation
     ```

  2. **The Engineering Meta Model is platform-plane only.** It governs Build Control Plane + Engineering Runtime + Execution workers. The Product plane keeps its own domain model. **`Milestone` is the single shared boundary object**, defined once in L0 and owned by governance. This preserves the Product/Platform separation of ADR-0023/ADR-0026.

  3. **Invariants are first-class and distinct from policies.** An invariant is a non-negotiable law (fail-closed, changeable only by ADR); a policy is a tunable decision. This **sharpens ADR-0026 §8**, which incorrectly treated invariants as a kind of policy. Two classes: Class A transition preconditions (live in the state machine) and Class B cross-cutting invariants (live in a dedicated invariant pass run on every state write). Era I already separates them de facto: `validate.py` `errors` are invariants, `warnings` are policy hints.

  4. **Enforcement is fail-closed and executable.** Every invariant in the L1 catalog names an enforcement point. A documented-only invariant is not acceptable; `GAP` checks must ship **with** the code that could violate them, never afterward. The Policy Engine (L5) MUST NOT be able to override an invariant.

  5. **Rename `WorkflowRuntime` → `EngineeringRuntime`** to align code with the ADR-0026 concept ("Engineering Runtime"). The term "workflow" misdescribes a *cycle*. This is a mechanical migration tracked in `docs/platform/terminology-migration.md`; the code edit is deferred to the MB2 implementation branch (this commit is constitution-only, no feature code).

  6. **Supersede the MB2 spec as the constitution.** `docs/superpowers/specs/2026-06-25-thesisos-mb2-adaptive-runtime-design.md` is re-scoped from "the MB2 design" to the **L4+ implementation spec**, and its freeze is **re-opened**: before MB2 code starts it MUST be rebased so every deliverable traces to an L0 object and an L1 invariant. L0–L3 are the authority MB2 implements.

- Consequences:
  - Era II opens with **formalization, not features**: meta model + invariants + (next) global state machine, then implementation concretizes them. Each future component is a realization of L0, reducing drift.
  - The MB2 spec must be revised before implementation — short-term rework, long-term coherence.
  - Invariants become a stable spine: tunable behaviour is pushed into policies, laws stay constant, so the runtime gets safer as it grows.
  - Product Track (M5) is **unblocked and orthogonal** — the platform constitution does not gate product milestones.
  - Cost: one more layer of documents to keep consistent; mitigated by keeping L0/L1 minimal and derived from existing artifacts.

- Alternatives considered:
  - **Keep MB2 as-is and add the meta model above it later** — rejected: implementing the event bus before the object model invites the exact drift this ADR prevents.
  - **One meta model spanning both planes** — rejected: re-couples Product and Platform (violates ADR-0023/0026); only `Milestone` crosses the boundary.
  - **Invariants as a policy category (status quo, ADR-0026 §8)** — rejected: conflating laws with tunable decisions makes the runtime unsafe to evolve.
  - **Skip the meta model (it's a single-developer project)** — rejected: the project is explicitly moving to many parallel agents/components, which is precisely when a shared ontology pays off; mitigated by keeping it ~1 page.

- References: ADR-0026 (§6 state vocabulary, §8 policy — refined here), ADR-0025 (packet FSM, extended by L2), ADR-0023 (sidecar boundary), ADR-0010 (promotion gates); `docs/platform/engineering-meta-model.md`, `docs/platform/invariant-model.md`, `docs/platform/runtime-model.md`, `docs/platform/era-model.md`.
