# Reports

The executor writes one report per WorkOrder phase or **qualification run** here.

## Qualification run naming (`C.{n}-R{k}`)

Each QWO execution is a distinct qualification instance. Re-runs after an EWO get a
new run id — prior reports are **never overwritten**. History is part of the capability.

| Run id | WorkOrder | Verdict | Report | Notes |
|--------|-----------|---------|--------|-------|
| `C.1-R1` | C.1 OR-1 | FAIL | `C.1-or-1.md` (legacy) | pre-EWO-1 |
| `C.1-R2` | C.1 OR-1 re-QWO | **PASS** (accepted) | `C.1-R2.md` | post-EWO-1 |
| `C.2-R1` | C.2 OR-2 | PARTIAL (accepted) | `C.2-R1.md` | → EWO-2 |
| `C.2-R2` | C.2 OR-2 re-QWO | **PASS** | `C.2-R2.md` | or-2 qualified |
| *(pre-flight)* | C.3 OR-3 | — | `C.3-preflight-runtime-audit.md` | measured 40% runtime |
| `C.3-R3` | C.3 OR-3 re-QWO | **PARTIAL** | `C.3-R3.md` | post-EWO-4 Grounding; disposition pending |
| `C.3-R2-investigation.md` | C.3 investigation | — | Grounding Gap; not Promotion |
| `C.3-R2` | C.3 OR-3 re-QWO | **FAIL** | `.asep/reports/C.3-R2.md` |
| `C.3-R1` | C.3 OR-3 | **PARTIAL** (accepted) | `C.3-R1.md` | → EWO-3 |

**Qualification Contract:** mandatory from C.2 onward — see `.asep/proposals/C.3-or-3-corpus.md`.

**Capability Coverage:** four dimensions on each OR capability — see `docs/engineering-program.md`.

## Engineering reports

| Report | WorkOrder | Category |
|--------|-----------|----------|
| `META-0-engineering-program-binding.md` | META-0 | Infrastructure |
| `EWO-1-runtime-knowledge-alignment.md` | EWO-1 | Alignment |
| `EWO-2-runtime-methodology-alignment.md` | EWO-2 | Alignment |
| `EWO-3-runtime-corpus-alignment.md` | EWO-3 | Alignment |
| `EWO-4A-corpus-list-grounding.md` | EWO-4A | Grounding |
| `C.3-R4` | C.3 OR-3 re-QWO | **PASS** | `C.3-R4.md` | post-EWO-4A; or-3 qualified |
| `C.4-or-4-constraint-compliance.md` | C.4 proposal | ⏳ pending | Constraint Compliance / Normative |

The newest report tells the skill where the last run left off when the user says
`ASEP: continua`.
