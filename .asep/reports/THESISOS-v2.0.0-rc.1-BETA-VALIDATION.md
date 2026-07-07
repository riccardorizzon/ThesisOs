# RC Beta Validation — Operational Tracker

> **Product:** ThesisOS v2.0.0-rc.1  
> **Phase:** Release Candidate validation (not feature development)  
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

## Cohort

| # | User | Invited | Onboarded | Notes |
|---|------|---------|-----------|-------|
| 1 | | ☐ | ☐ | |
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
