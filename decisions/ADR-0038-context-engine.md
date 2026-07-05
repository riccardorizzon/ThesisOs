# ADR-0038: Context Engine

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product (L2 Knowledge Engine)
- **Context:** v1.0 assembles retrieval and memory per turn in graph nodes (`prompt_wire`, `memory_context`) but the operator must still craft prompts. Product v2 requires automatic context assembly so the user selects **actions**, not prompt templates.
- **Decision:**

  ### Responsibility

  **Context Engine** assembles a **ContextPacket** for every AI action and surfaces a **ContextBar** summary in Writing (and optionally other modules).

  ### Input

  ```typescript
  ContextRequest {
    project_id: string
    surface: "home" | "writing" | "sources" | "knowledge" | "research"
    entity_type?: string
    entity_id?: string
    selection?: TextRange
    user_intent?: string
  }
  ```

  ### Output — ContextPacket (required fields)

  ```typescript
  ContextPacket {
    project: { title, phase, progress_pct }
    entity?: { type, id, title, snippet }
    relevant_sources: SourceRef[]
    concepts: ConceptRef[]
    decisions: DecisionRef[]      // binding first
    definitions: DefinitionRef[]
    citations_available: CitationRef[]
    corpus_constraints: string[] // CORPUS-02/03 etc.
    writing_rules: string[]        // when surface=writing
    memory_proposals_pending: number
    recent_activity: ActivityRef[]
    token_budget: number
  }
  ```

  ### Assembly precedence (strict order)

  1. Binding decisions (OR-5 frozen)
  2. Entity scope (chapter / source / concept)
  3. Retrieval ranked, corpus-scoped (OR-3)
  4. Concept neighborhood — 1-hop (PX-4+)
  5. Terminology definitions
  6. Writing rules if `surface=writing` (OR-6, OR-4)
  7. Truncate to `token_budget`; never drop (1) or (2)

  ### API

  - `GET /projects/{id}/context` — assemble + cache
  - `POST /ai/actions/{action}` — requires `context_id` or inline packet hash

  ### Phasing

  - **PX-1 v0:** chapter + decisions + corpus_constraints + writing_rules stub
  - **PX-4+:** concepts neighborhood
  - Cache invalidation on write to entity, memory approval, source promotion

- **Invariants:**
  - **INV-CE-1:** No product AI action bypasses Context Engine in default paths.
  - **INV-CE-2:** Binding decisions always included when present — precedence (1).
  - **INV-CE-3:** Corpus exclusions enforced in packet even if retrieval returns excluded works.
  - **INV-CE-4:** ContextPacket schema versioned; breaking changes require ADR bump.
  - **INV-CE-5:** Operator never required to paste Bibliography Master or Decisions into prompts for standard actions.

- **Compliance checklist:**
  - [ ] **C1:** Integration test: packet includes frozen decision when contradictory chunk retrieved
  - [ ] **C2:** Writing AI panel calls `/context` before action
  - [ ] **C3:** p95 assembly < 500ms PX-1; < 200ms PX-4 target (engineering program)

- **Violation examples:**
  - Freeform chat panel without packet in Writing default → INV-CE-1
  - Dropping CORPUS-02 from packet when Mythologies retrieved → INV-CE-3

- **References:** ADR-0035, ADR-0037, ADR-0039, OR-3, OR-5, OR-6, `prompt_wire.py`
