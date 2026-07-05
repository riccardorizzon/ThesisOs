# Capabilities

`runtime-platform.yaml` is the **Capability Graph** for the Runtime Platform track.

`thesis-agent-migration.yaml` is the graph for the **Thesis Agent Migration** program
(OR-1…E2E). See `docs/engineering-program.md` and `.asep/programs/thesis-agent-migration.yaml`.

`thesisos-product-v2.yaml` is the graph for **ThesisOS Product v2** (PX-1…PX-6).
PX-3 Wave A backlog: `.asep/reports/PX3-WAVE-A-BACKLOG.md` + `.asep/programs/px3-parallel.yaml`.
Parallel execution of remaining PX-1 EWOs: `.asep/programs/px1-parallel.yaml` and
`.asep/reports/PX1-PARALLEL-PROGRAM.md`.

The skill resolves a request to a capability node, not a milestone number, then
checks the node's prerequisites (`depends_on` done, `requires` ADRs present,
`baseline` = last commit) before executing.

The **plan** (`plans/*.md`) stays authoritative for exact scope; this graph is the
navigation layer. Keep `status` and `baseline` fields in sync after each milestone.
