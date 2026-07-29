# Stability 7-day monitor — v2.0.0-rc.2 (+ demo hardening)

> **Started (D0):** 2026-07-29  
> **Target D7:** 2026-08-05  
> **Stack:** docker compose local (`localhost:3000` / `:8000`)  
> **Baseline branch:** `feat/companion-persistence` (merge to `main` via PR)  
> **Cannot be closed by agent alone** — calendar days must elapse.

## How to run (operator, ~2 min)

```bash
make ops-check
# optional fuller:
make demo-gate
```

Log one row per check. After any hotfix, add a smoke row and note if the 7-day clock restarts.

## Log

| Day | Date | SHA (short) | Command | Result | Notes |
|-----|------|-------------|---------|--------|-------|
| D0 | 2026-07-29 | 86ad1578+ | `make demo-gate` + `make beta-validator-rc` | **PASS** | See `GA-PATH-VERIFICATION-20260729.md` |
| D1 | | | `make ops-check` | | |
| D2 | | | `make ops-check` | | |
| D3 | | | `make ops-check` | | |
| D4 | | | `make ops-check` | | |
| D5 | | | `make ops-check` | | |
| D6 | | | `make ops-check` | | |
| D7 | 2026-08-05 | | `make demo-gate` | | Close report → attach to GA bundle |

## Incidents / hotfixes

| Date | Issue | Fix SHA | Smoke | Clock restart? |
|------|-------|---------|-------|----------------|
| — | — | — | — | — |

## Exit

- [ ] D7 row PASS
- [ ] No open `v2.0-blocker`
- [ ] Summary paragraph pasted into GA bundle § Stability
