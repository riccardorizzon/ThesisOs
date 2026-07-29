# Demo Presentability — Closure Disposition

> **Date:** 2026-07-29  
> **Product:** ThesisOS `v2.0.0-rc.2` (+ demo hardening on `feat/companion-persistence`)  
> **Decision:** **CLOSE** the demo-presentability workstream  
> **Operator:** session disposition (product-first)

---

## Closed as DONE

| Track | Evidence |
|-------|----------|
| Demo Wave 1 (data / script) | `docs/demo/DEMO-SCRIPT.md`, `bin/demo-cleanup.sh` |
| Demo Wave 2 (polish) | `bin/demo-wave2-check.sh` |
| Demo Wave 3 (ops) | `docs/demo/DEMO-OPS-RUNBOOK.md`, `bin/demo-wave3-check.sh` |
| Demo Wave 4 (growth artifacts) | `docs/demo/DEMO-GROWTH-PLAN.md`, `bin/demo-wave4-check.sh` |
| ADR-0048 shared beta gate | `decisions/ADR-0048-access-control-beta.md`, `make demo-auth-check` |
| Citations max product-side | `make demo-citations-check` (W-06 residual documented) |
| Live gates | `make demo-gate` PASS · `make beta-validator-rc` PASS |

**Product status after closure:** **demo-ready / presentable** (not GA).

---

## Explicitly DEFERRED (not open work)

| Item | Disposition | Re-open when |
|------|-------------|--------------|
| **Human cohort** (5–10 testers) | Materials ready (`BETA-COHORT-INVITE.md`); **no humans invented / onboarded** | Product Lead invites real testers |
| **GA package** (`v2.0.0`) | **Not authorized** — separate approval package required | Architect/Product GA approval |
| **M8** (multi-user + new features) | Deferred per ADR-0048 / README | After GA (or Architect exception) |

These are **not** remaining demo-wave tasks. Closing this workstream does **not** claim GA or cohort completion.

---

## Exit statement

```text
Demo Waves 1–4 + ADR-0048 = CLOSED (PASS)
Human cohort            = DEFERRED
GA package              = DEFERRED (not authorized)
M8                      = DEFERRED
```

Next authorized product work requires a new Architect act (e.g. `AUTHORIZE` GA package or M8 Work Order) — not further demo-wave churn.

---

## WO-TRACE

```text
PX-1…PX-6 promoted → M7 / v2.0.0-rc.2 → Demo Waves 1–4 + ADR-0048 CLOSED
  → (deferred) human cohort / GA / M8
```
