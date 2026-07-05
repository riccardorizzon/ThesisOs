# ADR-0040: Product State Model

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product
- **Context:** v1.0 state lives split across blueprint markdown, M2 memories, chapters table, and chat history. Product v2 needs explicit state model for Home progress, session closure, and module coherence without exposing engine internals.
- **Decision:**

  ### State domains

  | Domain | Authority (UX runtime) | Governance mirror | UX surface |
  |--------|------------------------|-------------------|------------|
  | Project | `projects` | template config | Settings |
  | Outline / chapters | `chapters` tree | blueprint `chapters/` | Writing left panel |
  | Progress | **derived** | — | Home ring |
  | Sources | `sources` + `documents` | Bibliography-Master | Sources |
  | Concepts | `concepts` graph | Terminology, Theory Map | Knowledge |
  | Decisions | `memories` decision + Decisions.md | Frozen markers | Proposals, Knowledge |
  | Activity | `activities` | Changelog (on approve) | Home feed |
  | Session proposals | ephemeral → OR-7 | Memory-Protocol | Modals |

  ### Progress (deterministic)

  ```text
  progress_pct = Σ (chapter_weight × status_factor) / Σ chapter_weight
  ```

  - Weights from outline metadata
  - `status_factor`: draft=0.4, review=0.7, approved=1.0
  - **Not LLM-estimated**

  ### Session closure (OR-7 product UX)

  Closing a session proposes atomically (operator approves):

  - Memory update
  - Thesis-State delta
  - Changelog row
  - Bibliography candidata

  **State Atomicity:** partial acceptance forbidden (OR-7 M-09).

  ### Home "Continua"

  Deep link to last `writing/[chapterId]` + section anchor from activity log.

- **Invariants:**
  - **INV-PS-1:** Progress displayed on Home MUST use deterministic formula — not model guess.
  - **INV-PS-2:** Permanent writes require operator approval — no silent DB/memory mutation from AI panel.
  - **INV-PS-3:** Frozen decisions cannot be reopened from UI without explicit trigger (OR-5).
  - **INV-PS-4:** Activity feed reads from `activities` table — not raw chat log.
  - **INV-PS-5:** `project_id` scopes all product state from PX-1 onward.

- **Compliance checklist:**
  - [ ] **C1:** Progress unit test with fixed chapters → fixed pct
  - [ ] **C2:** Session close UI offers bundled proposal
  - [ ] **C3:** Attempt to edit frozen decision shows blocked state

- **Violation examples:**
  - Home progress from LLM → INV-PS-1
  - Auto-write to Permanent without modal → INV-PS-2

- **References:** ADR-0037, ADR-0041, OR-7, Memory-Protocol, `Thesis-State.md`
