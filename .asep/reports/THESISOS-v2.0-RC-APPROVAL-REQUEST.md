# Release Candidate — Approval Request

> **Product:** ThesisOS v2.0.0-rc.1  
> **Program:** `thesisos-product-v2` (PX-1…PX-6 complete)  
> **Status:** **PENDING SIGN-OFF** — tag applied locally; staging deploy not authorized until approvals below  
> **Date:** 2026-07-07  
> **Bundle:** `.asep/reports/THESISOS-v2.0-RC-BUNDLE.md`

---

## Request

Authorize **ThesisOS Product v2.0 Release Candidate 1** for staging deployment and beta onboarding.

This is **release ops** — not new product engineering. Scope is frozen at the milestone baseline below.

---

## Baseline (verified 2026-07-07)

| Artifact | Value |
|----------|-------|
| Branch | `main` |
| RC commit | `fd23ad70` — `docs(release): ThesisOS v2.0 RC bundle` |
| Product milestone commit | `bb561ea4` — `promote(px6): PX-6 Polish milestone ratified` |
| Tag `px6-complete` | → `bb561ea4` |
| Tag `v2.0.0-rc.1` | → `fd23ad70` (local) |
| Runtime dependency | `mb2-complete` @ `3957c94` (unchanged) |
| `make ci` | **PASS** @ `fd23ad70` |

---

## What is being released

All six product milestones — see bundle §3 for feature list:

```text
PX-1 Foundation → PX-2 Writing → PX-3 Sources → PX-4 Knowledge (px4-complete)
  → PX-5 Research (px5-complete) → PX-6 Polish (px6-complete)
```

**Qualification:** QWO-PX1/2, PX-3 conformance, PX-4/5/6 promotion, QWO-PX6-001 — all PASS per bundle §6.

---

## Known limitations (accepted for RC)

| ID | Summary |
|----|---------|
| L-01 | Multi-project: registry-scoped, not full DB partition |
| L-02 | Some canvas lenses use catalog stubs |
| L-03 | Citation validator = product mitigation; LLM author-date not guaranteed |
| L-04 | No multi-user collaboration |
| L-05 | No separate Reviewer/Planner agents |

Full detail: `docs/KNOWN_LIMITATIONS.md`, bundle §5.

---

## Approvals required

Reply with **`APPROVE RC v2.0.0-rc.1`** (or structured block below) in each role column.

| Role | Name | Decision | Date |
|------|------|----------|------|
| **Architect** | | ☐ APPROVE ☐ REJECT | |
| **Release Manager** | | ☐ APPROVE ☐ REJECT | |
| **Product Lead** | | ☐ APPROVE ☐ REJECT | |

### Structured approval (copy/paste)

```text
# RELEASE APPROVAL — ThesisOS v2.0.0-rc.1

Product:     ThesisOS v2.0.0-rc.1
Program:     thesisos-product-v2
Commit:      fd23ad70
Tag:         v2.0.0-rc.1
Role:        Architect | Release Manager | Product Lead
Decision:    APPROVE | REJECT
Notes:       (optional)
Timestamp:   YYYY-MM-DD
```

---

## Authorized after APPROVE (Release Manager)

1. Push tag to remote (if not already):
   ```bash
   git push origin v2.0.0-rc.1
   ```
2. Deploy backend + frontend to **staging** from `v2.0.0-rc.1`
3. Run smoke tests (Home, Writing, Sources, Knowledge, Research canvas, Settings)
4. Onboard 5–10 beta users (Product Lead) — bundle §9
5. Monitor 7 days; triage feedback → v2.0 blockers vs v3 backlog

---

## Explicitly NOT authorized by this request

- Product code changes on `main` without hotfix WorkOrder
- Tag `v2.0.0` GA (requires RC validation complete)
- Runtime / MB2 / SoR / Constitution modifications
- Scope expansion beyond PX-1…PX-6

---

## Rollback

If staging shows critical blockers: revert deployment to previous stable; hotfix on `main`; tag `v2.0.0-rc.2`. Do **not** move or delete `px6-complete`.

Bundle §8.

---

## After RC validation (separate approval)

When beta period completes with no blockers:

```bash
git tag -a v2.0.0 -m "ThesisOS v2.0.0" <hotfix-commit-or-fd23ad70>
```

Requires **GA release approval** — not covered by this RC request.

---

## WO-TRACE

```text
PX-6 promoted (px6-complete @ bb561ea4)
  → THESISOS-v2.0-RC-BUNDLE (fd23ad70)
  → v2.0.0-rc.1 tagged (local)
  → THIS REQUEST → staging + beta → v2.0.0 GA
```
