# RC Beta Validation — Operational Tracker

> **Product:** ThesisOS v2.0.0-rc.1  
> **Phase:** Release Candidate validation — **Day 0 PASS** (automated)  
> **Validator:** `bin/beta-validator-rc.sh` · `make beta-validator-rc`  
> **Onboarding:** `.asep/reports/RC-BETA-ONBOARDING.md`  
> **Started:** 2026-07-07  
> **Target duration:** 7 days  
> **Staging baseline:** `fd23ad70` @ `v2.0.0-rc.1`

## Scope

Collect **only**:

- bugs
- crashes
- regressions
- critical UX issues

**Out of scope:** new features, ASEP/SoR changes, capability expansion, MB2 refactors.

## Day 0 automated validation

| Check | Result | Report |
|-------|--------|--------|
| Beta validator script | ✓ PASS | `.asep/reports/THESISOS-v2.0.0-rc.1-BETA-VALIDATION-RUN-20260707.md` |
| Certificate | ✓ | `.asep/certificates/THESISOS-v2.0.0-rc.1-BETA-VALIDATION-DAY0-20260707.yaml` |

**Staging URL (beta):** http://34.79.238.160:3000

## Cohort

| # | User | Invited | Onboarded | Notes |
|---|------|---------|-----------|-------|
| 0 | automated-validator | ☑ | ☑ | Day 0 script PASS |
| 2 | | ☐ | ☐ | |
| 3 | | ☐ | ☐ | |
| 4 | | ☐ | ☐ | |
| 5 | | ☐ | ☐ | |
| 6 | | ☐ | ☐ | |
| 7 | | ☐ | ☐ | |
| 8 | | ☐ | ☐ | |
| 9 | | ☐ | ☐ | |
| 10 | | ☐ | ☐ | |

**Target:** 5–10 beta users (Product Lead)

## Feedback triage

| ID | Type | Severity | Surface | Status | Disposition |
|----|------|----------|---------|--------|-------------|
| — | — | — | — | — | — |

Disposition values: `v2.0-blocker` | `hotfix-wo` | `v3-backlog` | `wontfix-rc`

## Exit criteria (for GA package)

- [x] Day 0 automated validator PASS
- [ ] Staging stable 7 days
- [ ] Smoke tests green after any hotfix
- [ ] No open `v2.0-blocker` items
- [ ] Beta feedback triaged
- [ ] Hotfix WorkOrders closed (if any)

## GA gate

Tag `v2.0.0` requires **separate GA Approval Package** — not authorized by RC approval.

## WO-TRACE

```text
RC APPROVED → staging smoke PASS → THIS TRACKER → GA approval (future)
```
