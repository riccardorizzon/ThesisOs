# ThesisOS v2.0.0 — GA Approval Bundle (**DRAFT**)

> **Status:** **DRAFT — NOT AUTHORIZED**  
> **Date:** 2026-07-29  
> **Do not tag `v2.0.0` from this draft.**  
> **Execution:** `.asep/reports/GA-PATH-EXECUTION-20260729.md`

---

## 1. Intent

Request future authorization to tag `v2.0.0` when blockers below are cleared.
This draft freezes **what we know today** so GA is mechanical later.

## 2. Baseline (candidate)

| Field | Value |
|-------|-------|
| Product | ThesisOS |
| Prior RC | `v2.0.0-rc.2` @ `5039df77` |
| Candidate branch | `feat/companion-persistence` |
| Candidate tip | `86ad1578` (+ execution commit on same branch) |
| Demo closure | `.asep/reports/DEMO-PRESENTABILITY-CLOSURE-20260729.md` |

## 3. Gate evidence (automated — agent can refresh)

| Gate | Required for GA | Status in draft |
|------|-----------------|-----------------|
| PX-1…PX-6 promoted | yes | PASS (certificates) |
| M7 / rc.2 | yes | PASS |
| `make demo-gate` | yes | **PASS** 2026-07-29 |
| `make beta-validator-rc` | yes | **PASS** 2026-07-29 |
| Human cohort 5–10 | yes (path A) | **BLOCKED — requires humans** |
| Feedback triage / no blocker | yes | **BLOCKED — no cohort** |
| 7-day stability | yes | **INCOMPLETE — D0 only** |
| Architect AUTHORIZE | yes | **NOT ISSUED** |

## 4. Known accepted limitations (carry into GA)

- Single-user + optional `BETA_ACCESS_TOKEN` (ADR-0048); multi-user = M8
- Citations author-date preferred; **W-06** not 100% guaranteed
- Docling / heavy PDF deferred
- Tunnel pubblico fragile — prefer localhost for demos

## 5. Blockers to authorization

1. **P1** — Human cohort onboarded **or** signed waiver for path B (operator-only GA).
2. **P3** — D7 stability row PASS (or explicit waiver).
3. **P0** — Candidate merged to `main` (PR merged).
4. **Architect/Product act** — replace DRAFT with APPROVED certificate.

## 6. Rollback (when GA ships)

1. Keep `v2.0.0-rc.2` tag.
2. If critical post-GA: hotfix + `v2.0.1`; do not delete `v2.0.0`.
3. Staging revert to previous tag if deploy fails.

## 7. Out of scope

- M8 multi-user / new features
- ASEP Core / PX-EXEC expansion
- Claiming cohort completion without real testers

## 8. Approval block (empty until you act)

```text
Product:     ThesisOS v2.0.0
Status:      NOT APPROVED (draft)
Baseline:    <sha after merge>
Approver:    —
Date:        —
```

## WO-TRACE

```text
demo CLOSED → GA draft 2026-07-29 → (you) cohort/7d/AUTHORIZE → tag v2.0.0
```
