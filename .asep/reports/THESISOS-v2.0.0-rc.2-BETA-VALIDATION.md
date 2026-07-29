# RC Beta Validation — Operational Tracker (M7 / rc.2)

> **Product:** ThesisOS v2.0.0-rc.2  
> **Phase:** Release Candidate validation — **CLOSED (operator disposition 2026-07-29)**  
> **Validator:** `bin/beta-validator-rc.sh` · `make beta-validator-rc`  
> **Onboarding:** `.asep/reports/RC-BETA-ONBOARDING.md`  
> **Started:** 2026-07-08  
> **Closed:** 2026-07-29 — see `.asep/reports/DEMO-PRESENTABILITY-CLOSURE-20260729.md`  
> **Staging baseline:** `5039df77` @ `v2.0.0-rc.2`  
> **Cohort / GA:** **DEFERRED** (materials ready; not claimed complete)

## Scope

Collect **only**:

- bugs
- crashes
- regressions
- critical UX issues

**Out of scope:** new features (→ M8 / v3 backlog), ASEP/SoR changes.

## Day 0 automated validation

| Check | Result | Report |
|-------|--------|--------|
| `make ci` | ✓ PASS | main @ `5039df77` |
| Beta validator script | ✓ PASS | `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION-RUN-20260708.md` |
| Certificate | ✓ | `.asep/certificates/THESISOS-v2.0.0-rc.2-BETA-VALIDATION-DAY0-20260708.yaml` |

**Staging URL (beta):** `http://localhost:3000` (docker compose) — see `RC-BETA-ONBOARDING.md`

## Cohort

| # | User | Invited | Onboarded | Notes |
|---|------|---------|-----------|-------|
| 0 | automated-validator | ☑ | ☑ | Day 0 script PASS |
| 1 | | ☐ | ☐ | Product Lead assigns |
| 2 | | ☐ | ☐ | |
| 3 | | ☐ | ☐ | |
| 4 | | ☐ | ☐ | |
| 5 | | ☐ | ☐ | |
| 6 | | ☐ | ☐ | |
| 7 | | ☐ | ☐ | |
| 8 | | ☐ | ☐ | |
| 9 | | ☐ | ☐ | |
| 10 | | ☐ | ☐ | |

**Target:** 5–10 beta users (Product Lead) · Invito: `.asep/reports/BETA-COHORT-INVITE.md`

## Feedback triage

| ID | Type | Severity | Surface | Status | Disposition |
|----|------|----------|---------|--------|-------------|
| — | — | — | — | — | — |

## Exit criteria (for GA package)

- [x] Day 0 automated validator PASS
- [x] M7.2 + `make ci` green on RC commit
- [x] Demo presentability closed (`DEMO-PRESENTABILITY-CLOSURE-20260729.md`)
- [ ] Staging stable 7 days — **deferred** (no dedicated staging SLA run claimed)
- [ ] Smoke tests green after any hotfix — **deferred**
- [x] No open `v2.0-blocker` items (operator demo path)
- [ ] Beta feedback triaged — **N/A** (no human cohort run)
- [ ] Human cohort onboarded (5–10) — **DEFERRED**

## GA gate

Tag `v2.0.0` requires **separate GA Approval Package** — **not authorized** by this closure.

## Disposition 2026-07-29

| Item | Result |
|------|--------|
| Automated / demo gates | **CLOSED PASS** |
| Human cohort | **DEFERRED** |
| GA | **DEFERRED** |
| M8 | **DEFERRED** |

## WO-TRACE

```text
M7.2 PASS → v2.0.0-rc.2 → demo Waves 1–4 + ADR-0048 CLOSED
  → GA / cohort / M8 deferred (separate authorization)
```
