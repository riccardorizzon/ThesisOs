# ASEP Executor

Run only after intent=`develop` and the capability resolver said "proceed".
Build the Work Order from `.asep/templates/work-order-template.md` (internal — do
not ask the user to confirm unless scope conflicts with governance), then:

```text
Observe → Analyze → Strategy → Execute → Verify → Commit → Report
```

- **Observe / Analyze / Strategy** — map plan scope to files; choose the smallest
  correct diff; confirm layer membership (ADR-0030 §2) and extension points
  (runtime-contract §5).
- **Execute** (TDD where practical) — implement only in-scope artifacts. Enforce:
  - Business purity (C3): no DB / telemetry / logging / event-bus / LangGraph
    imports in Business agents.
  - Composition root wires concretes (C2); nodes take injected ports/hooks (R1–R2).
  - Runtime emits canonical events only; bus/subscribers depend on interfaces, never
    concretes; zero-subscriber runtime stays valid (C4/R6/R8).
  - M4 execution node bodies frozen unless ADR-authorized (C6).
  - Honor each node's `invariant` field in the capability graph.
- **Verify** — see `.asep/pipeline/qualification.md` (gates must be green).
- **Commit** — one milestone commit, conventional message, author override only
  (never modify `git config`).
- **Report** — see `.asep/templates/report-template.md`; write it to
  `.asep/reports/<phase>.md` and echo the status block.

STOP at any point a Constitution/ADR/layer violation is required → write the report
with `Milestone Status: STOP` and the smallest unblocking change (often an ADR).
