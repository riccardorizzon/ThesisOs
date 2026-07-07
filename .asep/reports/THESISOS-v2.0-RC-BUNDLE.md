# ThesisOS v2.0 — Release Candidate Bundle

> **Status:** **APPROVED** — tag `v2.0.0-rc.1` @ `fd23ad70`; staging deploy authorized 2026-07-07 — see `.asep/reports/THESISOS-v2.0.0-rc.1-APPROVAL-EXECUTION-20260707.md`  
> **Date:** 2026-07-07  
> **Product program:** `thesisos-product-v2`  
> **Scope:** PX-1 through PX-6 complete and promoted  
> **Baseline:** product `bb561ea4` (`px6-complete`); RC bundle `fd23ad70` (`v2.0.0-rc.1`)

---

## 1. Executive summary

ThesisOS Product v2.0 is ready for release candidate evaluation. All six milestones of `thesisos-product-v2` are complete and promoted:

| Milestone | Tag | Status |
|-----------|-----|--------|
| PX-1 Foundation | — | complete |
| PX-2 Research Workspace | — | complete |
| PX-3 Sources | — | complete |
| PX-4 Knowledge | `px4-complete` | promoted |
| PX-5 Research | `px5-complete` | promoted |
| PX-6 Polish | `px6-complete` | promoted |

This bundle requests authorization to tag and deploy `v2.0.0-rc.1`.

---

## 2. Baseline

```text
Branch:     main
RC commit:  fd23ad70 docs(release): ThesisOS v2.0 RC bundle
Product:    bb561ea4 promote(px6): PX-6 Polish milestone ratified
Tag:        px6-complete → bb561ea4
Tag:        v2.0.0-rc.1 → fd23ad70 (local)
Runtime:    mb2-complete → 3957c94
CI:         green @ fd23ad70
```

---

## 3. What is in v2.0

### PX-1 Foundation
- AppShell + navigation
- Design system v1
- Home page
- Product routing

### PX-2 Research Workspace
- Writing flow
- Source interaction
- Decision visibility
- Session continuity

### PX-3 Sources
- Knowledge sources management
- Source linking
- Source exploration

### PX-4 Knowledge
- Knowledge objects
- Knowledge graph
- Knowledge Explorer
- Sources → Knowledge linking

### PX-5 Research
- Research hub (`/research`)
- Canvas viewport with pan/zoom/select
- Inspector rail
- Discovery lenses
- Serendipity strip

### PX-6 Polish
- Citation validator (numeric `[n]` detection, author-date suggestions, Applica gating)
- Bibliography export (BibTeX) + print stylesheet
- Multi-project switch + registry isolation
- Outline drag reorder
- Settings depth page
- Typography polish (Crimson Pro + Atkinson)
- Cross-surface performance pass

---

## 4. Runtime dependency

Product v2.0 runs on the MB2 Engineering Runtime:

- Runtime tag: `mb2-complete` @ `3957c94`
- SoR revision: 2026-07-05
- MB2-Q1…Q6: PASS
- §13.3 golden path: PASS

No runtime changes are required for v2.0 RC.

---

## 5. Known limitations

| ID | Limitation | Mitigation in v2.0 | Future work |
|----|------------|--------------------|-------------|
| L-01 | Multi-project isolation is registry-scoped, not DB-partitioned | Project registry + active project context | Full DB partition per project |
| L-02 | L-author / L-unread lenses use catalog stubs | Documented partial; core lenses fully functional | Satellite data integration |
| L-03 | Citation validator is product-layer mitigation; does not claim deterministic LLM author-date | Applica gating + override | LLM model or post-processing improvement |
| L-04 | Collaboration / multi-user editing not included | Single-user scoped | Product v3 |
| L-05 | Separate Reviewer/Planner agents not included | Manual review flow | Product v3 |

Full limitations: `docs/KNOWN_LIMITATIONS.md`

---

## 6. Qualification summary

| Qualification | Result |
|---------------|--------|
| `make ci` | green @ `bb561ea4` |
| `make unit-builder-engine` | green |
| `make unit-m4-recovery` | 45/45 PASS |
| QWO-PX1-001 | PASS |
| QWO-PX2-001 | PASS |
| PX-3 conformance assessment | PASS |
| MB2-Q1…Q6 | PASS |
| PX-4 promotion | PASS |
| PX-5 promotion | PASS |
| PX-6 QWO-PX6-001 | PASS |

---

## 7. Deployment checklist

- [x] Tag `v2.0.0-rc.1` on `fd23ad70` (approved 2026-07-07)
- [ ] Deploy backend to staging
- [ ] Deploy frontend to staging
- [ ] Run smoke tests on staging
- [ ] Invite beta users
- [ ] Monitor error tracking and performance for 7 days
- [ ] Collect beta feedback
- [ ] Fix blocking issues
- [ ] Tag `v2.0.0` and deploy to production

---

## 8. Rollback plan

If critical issues are found during RC:

1. Revert deployment to previous stable tag.
2. Apply hotfix on `main`.
3. Tag `v2.0.0-rc.2` and redeploy.
4. Do **not** roll back `px6-complete`; it remains the product milestone baseline.

---

## 9. Beta onboarding plan

| Step | Action |
|------|--------|
| 1 | Identify 5–10 beta users |
| 2 | Send onboarding guide (link TBD) |
| 3 | Collect structured feedback via form |
| 4 | Weekly sync during RC period |
| 5 | Triage feedback into v2.0 blockers vs v3 backlog |

---

## 10. Required approvals

| Role | Approval needed |
|------|-----------------|
| Architect | Release candidate sign-off |
| Release Manager | Deployment authorization |
| Product Lead | Beta user selection |

---

## 11. Proposed commands

```text
# Tag RC (DONE locally @ fd23ad70)
git tag -a v2.0.0-rc.1 -m "ThesisOS v2.0.0 release candidate 1" fd23ad70

# After approval — push tag
git push origin v2.0.0-rc.1

# Deploy staging
# (deployment commands depend on infra setup)

# After RC validation
git tag -a v2.0.0 -m "ThesisOS v2.0.0" <hotfix-or-rc-commit>
```

---

## 12. WO-TRACE

```text
PX-1 → PX-2 → PX-3 → PX-4 (px4-complete) → PX-5 (px5-complete) → PX-6 (px6-complete)
  → THESISOS-v2.0-RC-BUNDLE (this document)
  → v2.0.0-rc.1 tag
  → staging deploy + beta
  → v2.0.0 GA
```
