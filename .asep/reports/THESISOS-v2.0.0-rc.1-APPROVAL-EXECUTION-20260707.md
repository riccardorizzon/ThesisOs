# Release Candidate Approval — Execution Report

> **Product:** ThesisOS v2.0.0-rc.1  
> **Program:** `thesisos-product-v2`  
> **Status:** **APPROVED** — staging deploy authorized  
> **Date:** 2026-07-07

## Approval receipt

Structured approval received (Architect | Release Manager | Product Lead):

```text
# RELEASE APPROVAL — ThesisOS v2.0.0-rc.1

Product:     ThesisOS v2.0.0-rc.1
Program:     thesisos-product-v2
Commit:      fd23ad70 (RC) / bb561ea4 (product baseline)
Tag:         v2.0.0-rc.1 → px6-complete
Role:        Architect | Release Manager | Product Lead
Decision:    APPROVE
Notes:       PX-1…PX-6 complete; make ci green; known limitations accepted per bundle §5
Timestamp:   2026-07-07
```

Certificate: `.asep/certificates/THESISOS-v2.0.0-rc.1-APPROVAL-20260707.yaml`

## Baseline (verified)

| Artifact | Value |
|----------|-------|
| RC commit | `fd23ad70` — `docs(release): ThesisOS v2.0 RC bundle` |
| Product milestone | `bb561ea4` — `promote(px6): PX-6 Polish milestone ratified` |
| Tag `px6-complete` | → `bb561ea4` |
| Tag `v2.0.0-rc.1` | → `fd23ad70` |
| Runtime | `mb2-complete` @ `3957c94` |

## Actions executed

| Step | Status | Notes |
|------|--------|-------|
| Record approval certificate | ✓ | `.asep/certificates/THESISOS-v2.0.0-rc.1-APPROVAL-20260707.yaml` |
| Update approval request status | ✓ | `.asep/reports/THESISOS-v2.0-RC-APPROVAL-REQUEST.md` |
| Update RC bundle status | ✓ | `.asep/reports/THESISOS-v2.0-RC-BUNDLE.md` |
| Verify `make ci` | ✓ PASS | 391 backend + 286 frontend + 191 builder-engine @ HEAD |
| Push `v2.0.0-rc.1` to remote | blocked | no `origin` remote configured |
| Deploy staging | pending | requires infra (Release Manager) |
| Beta onboarding | pending | Product Lead — bundle §9 |

## Authorized next steps (Release Manager)

1. Configure remote and push tag:
   ```bash
   git push origin v2.0.0-rc.1
   ```
2. Deploy backend + frontend to **staging** from `v2.0.0-rc.1`
3. Run smoke tests (Home, Writing, Sources, Knowledge, Research canvas, Settings)
4. Onboard 5–10 beta users; monitor 7 days

## Explicitly NOT authorized

- Product code changes on `main` without hotfix WorkOrder
- Tag `v2.0.0` GA (requires RC validation complete)
- Runtime / MB2 / SoR / Constitution modifications

## WO-TRACE

```text
PX-6 promoted (px6-complete @ bb561ea4)
  → THESISOS-v2.0-RC-BUNDLE (fd23ad70)
  → v2.0.0-rc.1 tagged
  → APPROVED (2026-07-07) — make ci PASS
  → staging + beta → v2.0.0 GA
```
