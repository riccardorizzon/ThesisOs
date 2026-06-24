# Citation Agent (Runtime)

> Type: Runtime LangGraph node. Milestone: **M7**. Status: designed (contract frozen), not implemented. Sources: `contracts/agents/citation.json`, M0 spec §7, `contracts/openapi/openapi.yaml` (`/citations`, `/bibliography`), ADR-0007.

## Mission
Turn the draft's citation markers into resolved, correctly formatted references and
a bibliography (APA7 / MLA / Chicago) from canonical CSL-JSON sources.

## Responsibilities
- Resolve each `CitationRef` to a `sources` row (CSL-JSON) with locators.
- Format in-text citations and the bibliography per the requested style.
- Back `POST /citations` and `GET /bibliography?style=apa7`.

## Inputs (contract)
- `reads_state`: `draft`, `citations`.

## Outputs (contract)
- `writes_state`: `citations` (`state_mutations: citations = set`) — enriched/resolved.

## Allowed actions
- Read/write `sources`/`citations`; render styles from CSL-JSON; attach locators
  (`locator`/`prefix`/`suffix`).

## Forbidden actions
- Writing prose (Writer's job) or judging quality (Critic's job).
- Mutating `GraphState` fields other than `citations`; adding fields (frozen).

## Dependencies
- **M6 Writer** (`draft` + raw `citations`), **`sources`/`citations` tables** (since
  M0), CSL-JSON pipeline.

## Promotion criteria (M7 gate, to be frozen in the M7 spec)
- CSL-JSON → APA7/MLA/Chicago rendering; bibliography endpoint; locators preserved;
  all `citations` resolve to real sources.

## Failure modes (contract)
- `unresolved_source` — a citation marker has no backing `sources` row.
- (Design risk) style-format edge cases — covered by per-style tests.
