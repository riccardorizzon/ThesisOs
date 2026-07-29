# ADR-0053: Citation Capability & Topology (M7 Grounding Engine — Wave 1)

- Status: **Proposed** (2026-07-29) — not Accepted; does not authorize implementation until Architect freeze + Critic sign-off on the M7 Grounding Engine design spec.
- Governance: Consistent with Runtime Constitution (C1–C8, esp. C6/C8), ADR-0030 (R1/R2 ports), ADR-0027 (reserved `citation` route), ADR-0007 (frozen GraphState), ADR-0031 (capability/port pattern).
- Context: M6 writer emits `CitationRef` markers in GraphState but does not persist `citations` or resolve against `sources`. ADR-0044 Product Hardening already DB-backed `sources` and shipped validate/BibTeX surfaces. Product Track M7 Wave 1 must activate the reserved `citation` route without colliding with Hardening naming or inventing a second source catalog. A frozen topology + ownership decision is required before implementation.

- Decision:

  ### 1. Activate the reserved `citation` route (separate, not chained)

  ```text
  START → supervisor → planner → router → memory_context → [route_after_router]
        ├─ … conversation / grounded_chat / writer … (unchanged)
        └─ route=citation ──► citation_node ──► END
  ```

  - **No** automatic `writer → citation` edge in Wave 1.
  - Router may select `citation` when the user asks to resolve/format bibliography or when a prior draft's citations need resolution.
  - Existing routes remain byte-stable (C6).

  ### 2. Citation is a CAPABILITY port

  ```text
  CitationCapability:  async resolve(brief: CitationBrief) -> ResolvedCitations
  ```

  - `make_citation_node(capability)` is a thin Business adapter: maps result → `{citations, errors}` per `contracts/agents/citation.json`.
  - Capability MUST NOT import `app.db`, concrete `CitationService`, or Event Bus (R1/R3/R8).
  - Optional style strings ride stream metadata / Event Bus — not new GraphState fields.

  ### 3. Resolution discipline

  - Each `CitationRef.source_id` MUST resolve to a `sources` row in the active `project_id`.
  - Resolution order: UUID match on `sources.id`, then slug match on `sources.slug` if `source_id` is non-UUID (writer/retrieval may emit either — normalize to UUID in resolved refs).
  - Failures append `AgentError(agent="citation", message=…)` with contract error **`unresolved_source`**; do not invent sources.
  - Alignment: rules must not contradict `POST /citations/validate` (ADR-0044).

  ### 4. Persistence ownership — `CitationService`

  - `CitationService` is the **sole writer** for the `citations` table.
  - Graph node never INSERTs citations; REST (or an explicit composition-root persist hook outside the node) calls `CitationService`.
  - `sources` remain owned by the existing source/document inventory path (ADR-0044); this ADR does not create a parallel catalog.

  ### 5. Naming & tags

  - Milestone label: **M7 Grounding Engine**.
  - Promotion tag: `m7-grounding-complete` (not bare `m7-complete`, to avoid collision with Product Hardening RC language).

- Consequences: Clear extension of ADR-0027; Writer purity preserved; Hardening inventory reused; M7.x evidence/confidence can add ports later without reopening GraphState. Cost: users must trigger citation route (or future autochain decision) explicitly in Wave 1.

- Alternatives considered:
  - **Always chain writer→citation** — rejected for Wave 1 (scope; latency; blurs route vocabulary).
  - **Resolve inside writer_node** — rejected; violates `writer.json` / citation contract split.
  - **New GraphState fields for resolved CSL** — rejected (ADR-0007).
  - **Replace ADR-0044 bibliography export** — rejected; complementary surfaces.

- References: M7 Grounding Engine design spec `docs/superpowers/specs/2026-07-29-thesisos-m7-grounding-engine-design.md`; ADR-0027, ADR-0031, ADR-0044, ADR-0054; `contracts/agents/citation.json`.
