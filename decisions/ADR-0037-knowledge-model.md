# ADR-0037: Knowledge Model — Concept-Centric

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product (domain model)
- **Context:** Most research tools are document-centric (PDF → notes → chapter). ThesisOS differentiator is **knowledge-centric** flow: concepts link sources, chapters, decisions, and citations. v1.0 has `memory.kind=concept` but no graph or singleton enforcement.
- **Decision:**

  ### Center of gravity

  The canonical entity is **`Concept`**, not Document or ChatMessage.

  ```text
  Knowledge  →  Sources  →  Writing  →  Output
  ```

  ### Concept singleton

  Each concept exists **once** per project (`slug` unique). Aliases merge to canonical node; no duplicate "Perception" notes across files.

  ### Graph

  Typed relations between concepts: `supports`, `contradicts`, `extends`, `used_in`, `related`.

  ### Bridges

  | Entity | Links to concept |
  |--------|------------------|
  | Source | M:N `concept_sources` |
  | Chapter | M:N `concept_chapters` |
  | Decision | M:N `concept_decisions` |
  | Citation | via source + locator |

  ### Module lenses (same graph)

  - **Knowledge:** ontological — definitions, Explain this thesis
  - **Research:** exploratory — map, discovery (PX-5 after PX-4)

  ### Implementation phasing

  - PX-3: sources feed concept extraction (proposed → approved)
  - PX-4: concept entity + Explain panel
  - PX-5: graph visualization

- **Invariants:**
  - **INV-KM-1:** No product feature treats PDF/upload as the primary identity for research navigation.
  - **INV-KM-2:** Concept slug unique per `project_id`.
  - **INV-KM-3:** Explain this thesis reads from concept graph + linked entities — not ad-hoc RAG-only.
  - **INV-KM-4:** FONDATO/PLAUSIBILE / corpus exclusions (OR-2, OR-3) apply to concept-source links.
  - **INV-KM-5:** Research graph UX (PX-5) MUST NOT ship before concept model (PX-4).

- **Compliance checklist:**
  - [ ] **C1:** Concept CRUD API exists before Research graph EWO
  - [ ] **C2:** Source detail shows linked concepts
  - [ ] **C3:** Writing Context Packet includes concept refs when PX-4+ live

- **Violation examples:**
  - File-browser as primary Research view → INV-KM-1
  - PX-5 graph EWO before PX-4 concept store → INV-KM-5

- **References:** ADR-0034, ADR-0038, ADR-0040, `docs/product/specs/thesisos-product-ux-v1.md` §5.5, §11
