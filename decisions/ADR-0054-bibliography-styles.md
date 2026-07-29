# ADR-0054: Bibliography Styles — APA7 / MLA / Chicago (M7 Grounding Engine — Wave 1)

- Status: **Proposed** (2026-07-29) — not Accepted; freeze with M7.0 before style implementation.
- Governance: Consistent with ADR-0001 (contract-first), ADR-0053 (citation capability), ADR-0044 (CSL-JSON on `sources`, BibTeX export).
- Context: OpenAPI reserves `GET /bibliography?style=` and writers/academia need human-readable citations. Full CSL processor suites are heavy; ThesisOS needs a **frozen, testable subset** of three styles with golden fixtures, not an unbounded CSL engine.

- Decision:

  ### 1. Supported styles (closed set for Wave 1)

  | `style` query value | Output |
  |---------------------|--------|
  | `apa7` | APA 7th edition reference list entries (+ in-text form helper) |
  | `mla` | MLA 9th edition (practical subset) |
  | `chicago` | Chicago Notes-Bibliography **bibliography** entries (notes numbering UI deferred) |

  Unknown `style` → `400` with stable error code `unsupported_style`.

  ### 2. Input record

  - Primary: `sources.csl_json` (JSONB).
  - Fallback fields on `sources` (`title`, `authors`, `year`, `doi`, `url`, `type`) when CSL keys missing.
  - Locators from `citations.locator` / `CitationRef.locator` for in-text forms only.

  ### 3. Supported CSL subset (Wave 1)

  Renderers MUST handle at least: `type`, `title`, `author` (family/given or literal), `issued`/`year`, `publisher`, `container-title`, `volume`, `issue`, `page`, `DOI`, `URL`.  
  Unsupported CSL keys are ignored (no crash). Missing title → emit placeholder `[untitled]` and flag in metadata for tests — do not skip silently without test coverage.

  ### 4. API surface

  - **LOCKED:** un-deprecate and realize `GET /bibliography?project_id=&style=apa7|mla|chicago` → ordered list of styled strings (and structured fields for UI).
  - **LOCKED:** un-deprecate and realize `POST /citations` alongside resolve route (see ADR-0053).
  - Scope: sources in bibliography set = same inclusion policy as ADR-0044 BibTeX export.
  - BibTeX export path **remains**; this ADR adds human styles, not a replacement.

  ### 5. Implementation constraint

  - Style logic lives in a pure module (e.g. `backend/app/services/citation/styles/`) with **golden fixture tests** per style (≥3 fixture sources each).
  - No network calls to external CSL processors required in Wave 1 (optional later).

- Consequences: Predictable academic output for Italian thesis primary use case; bounded QA via fixtures. Cost: not full CSL; edge-case publications may need manual edit until M7.x.

- Alternatives considered:
  - **Embed citeproc-js / full CSL** — deferred (ops weight, versioning); may revisit in M7.x.
  - **APA only** — rejected; roadmap and OpenAPI imply multi-style.
  - **HTML-only rich export** — rejected for Wave 1; plain/structured text first.

- References: ADR-0053; `contracts/openapi/openapi.yaml` (`/bibliography`); `sources.csl_json`; M7 Grounding Engine design spec.
