# Recovery Baseline Audit — pre-commit 2026-07-10

> **Purpose:** Classify working-tree changes before tag `v2.0.0-rc.3` (Recovery baseline).  
> **Parent tag:** `v2.0.0-rc.2` @ `5039df77`  
> **New identity:** Recovery Sprint 1–2 product baseline — **not** RC-2.

---

## Summary

| Category | Files | Action for baseline tag |
|----------|------:|-------------------------|
| (1) Product | 22 | **INCLUDE** |
| (2) Infra / guard / CI | 4 | **INCLUDE** |
| (3) Documentation & validation artifacts | 18 | **INCLUDE** (PVC + engineering docs) |
| **Exclude — orthogonal / frozen** | 27+ | **DEFER** separate PX-7 commit |

---

## (1) Product modifications — INCLUDE

| File | Change |
|------|--------|
| `frontend/lib/knowledgeClient.ts` | AP-001 — `apiBaseUrl()` |
| `frontend/lib/chapterClient.ts` | AP-001 |
| `frontend/lib/api.ts` | AP-001 |
| `frontend/lib/conversationClient.ts` | AP-001 |
| `frontend/lib/aiActions.ts` | AP-001 |
| `frontend/lib/proposalClient.ts` | AP-001 |
| `frontend/lib/projectsClient.ts` | AP-001 |
| `frontend/lib/corpusClient.ts` | AP-001 |
| `frontend/lib/documentClient.ts` | AP-001 |
| `frontend/lib/memoryClient.ts` | AP-001 |
| `frontend/lib/knowledgeClient.test.ts` | AP-001 test |
| `frontend/app/page.tsx` | AP-002 — home chapters degraded |
| `frontend/app/research/page.tsx` | AP-002 — concept count status |
| `frontend/app/review/page.tsx` | AP-002 — Critical error surface |
| `frontend/components/HomeView.tsx` | AP-002 — degraded banner |
| `frontend/components/research/ResearchHubPage.tsx` | AP-002 |
| `frontend/components/writing/WritingWorkspace.tsx` | AP-002 |
| `frontend/components/chrome/CommandPalette.tsx` | AP-002 |
| `frontend/components/navigation/ProjectSwitcher.tsx` | AP-002 |
| `frontend/components/ui/ApiDegradedBanner.tsx` | AP-002 — new component |

---

## (2) Infrastructure / guard / CI — INCLUDE

| File | Change |
|------|--------|
| `bin/check-ap001-ssr-base-url.sh` | AP-001 guard |
| `bin/check-ap002-error-contract.sh` | AP-002 guard |
| `Makefile` | `ap001-guard`, `ap002-guard` wired into `check` / `ci` |
| `.gitignore` | (recovery-only commit: no research-specific entries) |

**Note:** Makefile also contained PX-7 `research_engine` targets — **removed from this baseline commit** (see Exclude).

---

## (3) Documentation & validation artifacts — INCLUDE

| File | Role |
|------|------|
| `docs/engineering/anti-pattern-registry.md` | AP registry |
| `docs/engineering/error-contract-v1.md` | Error contract |
| `docs/recovery-sprint-1-report.md` | Recovery log |
| `.asep/reports/THESISOS-RC-2-RECOVERY-VALIDATION.md` | Automated validation (rename conceptually to recovery baseline) |
| `.asep/reports/THESISOS-RC-2-RECOVERY-VALIDATION-RUN-20260709.md` | Run log |
| `test thesisOs/beta-validation-kit/*` | PVC-1 kit |
| `test thesisOs/scorecard-PVC1-*.md` | PVC session data (tunnel — reference only) |
| `test thesisOs/results-template.md` | PVC aggregate |
| `test thesisOs/thesis_os_*.md` | Beta baseline reports (pre-existing inputs) |

---

## EXCLUDE — not Recovery baseline (defer)

| Path | Reason |
|------|--------|
| `research_engine/**` | PX-7 Learning Plane — frozen (ADR-0050), orthogonal to Recovery product |
| `.asep/research/**` | Metric Language catalog — Research Engine |
| `decisions/ADR-0050-research-language-freeze.md` | Governance for PX-7, not Recovery |
| `docs/superpowers/specs/2026-07-09-*.md` (8 files) | PX-7 / Metric Language design specs |
| Makefile `unit-research-engine`, `observe-px7.1`, `validate-metrics` | Depends on excluded package |

**No temporary/debug files detected** in the 40-file set.

---

## Tag identity

```
v2.0.0-rc.2 @ 5039df77
        ↓
Recovery Sprint 1 (AP-001)
        ↓
Recovery Sprint 2 (AP-002)
        ↓
v2.0.0-rc.3  ← this baseline (PVC Docker target)
```
