# ADR-0041: Blueprint ↔ Runtime Sync

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product (cross-plane with blueprint)
- **Context:** ThesisOS carries dual state: governance blueprint (`knowledge/thesis-agent/`) and runtime DB (memories, chapters, documents). v1.0 promotion script (`promote_runtime.py`) is one-directional batch ingest. Product v2 requires explicit sync policy to avoid silent drift.
- **Decision:**

  ### Source of truth by artifact class

  | Artifact class | Governance SoT | Runtime UX SoT | Sync direction |
  |----------------|----------------|----------------|----------------|
  | Frozen decisions | `Decisions.md` + decision memories | DB memories | blueprint → runtime on promote; runtime → blueprint **only on approved proposal** |
  | Terminology / Theory Map | blueprint markdown | `concepts` (PX-4) | promote + approved edits |
  | Outline master | `Outline-Master.md` | `chapters` tree | bidirectional with approval |
  | Chapter prose (promoted) | blueprint `chapters/` | `chapters.content_md` | bidirectional with approval |
  | Bibliography master | `Bibliography-Master.md` | `sources` | candidata → approved promotion |
  | Corpus binaries | `04_KNOWLEDGE/` | `documents` + chunks | import/index; immutable inbox |
  | Session / temp | `05_MEMORY/Temporary.md` | session state | runtime only; optional promote |

  ### Conflict resolution

  **Operator approval always wins.** No silent overwrite of Frozen artifacts. Conflicts surface as **Proposal** with diff.

  ### Promotion vs live edit

  - **Batch promotion:** `promote_runtime.py` (or successor) for milestone ingest — idempotent, tagged `migration_run` / `project_id`
  - **Live edit:** UI/API → proposal → approve → write both sides or explicit single-side with audit row

  ### Traceability

  Every derived runtime row retains provenance in metadata: `source_path`, `source_sha256`, `project_id` (existing P2 migration pattern).

  ### PA-0 boundary

  PA-0 defines policy only — full bidirectional sync implementation is PX-3+ EWO, not PA-0.

- **Invariants:**
  - **INV-SY-1:** Frozen blueprint artifacts MUST NOT be overwritten by runtime without approved proposal.
  - **INV-SY-2:** Operator approval required for Permanent memory and master artifact changes (OR-7).
  - **INV-SY-3:** Sync conflicts MUST be visible — no last-write-wins on Frozen class.
  - **INV-SY-4:** `_inbox/` exports remain immutable (migration P1).
  - **INV-SY-5:** Cross-plane sync features require compliance with Runtime Constitution (no graph node writes to blueprint files).

- **Compliance checklist:**
  - [ ] **C1:** Write path to Decisions.md goes through proposal flow
  - [ ] **C2:** Promoted chapter metadata includes source provenance
  - [ ] **C3:** No background job syncs Frozen → runtime without audit log

- **Violation examples:**
  - Nightly script overwriting Outline-Master from DB → INV-SY-1
  - Graph node writing Permanent.md directly → INV-SY-5 + Runtime C3

- **References:** `docs/kimi-to-thesisos-migration-runbook.md`, `promote_runtime.py`, ADR-0040, OR-7, P6 Constitution Governance
