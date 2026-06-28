# Work Order — <PHASE> <OBJECTIVE>

## Baseline
- Project: ThesisOS · Branch: `<branch>`
- Baseline commit: `<sha>` (frozen milestones table)
- Frozen: <prior milestones>

## Objective
<one sentence: what this milestone delivers>

## Scope
<exact list of artifacts/contracts to implement>

## Out of Scope
<explicit exclusions — anything deferred to later milestones>

## Constraints
- Runtime Constitution C1–C8, ADR-0030, Runtime Contract
- <milestone-specific invariants>

## Acceptance Criteria
- <typed/documented/stable/extensible criteria>

## Tests
- <unit / behavior / regression to add>

## Regression
- `make ci` · `make unit-m4-recovery` (M4 unchanged)

## Deliverable
- Commit + report (files, contracts, tests, gates, risks, readiness for next milestone)

## Completion Criteria
- All acceptance criteria met · unit tests PASS · `make ci` PASS · `make unit-m4-recovery` PASS
- Working tree clean · repository merge-ready
