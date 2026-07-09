# RC-2 Product Validation — Post-Recovery Sprint Comparison

> **Product:** ThesisOS (Recovery Sprint 1 + 2 complete)  
> **Phase:** RC-2 Product Validation — **authorized instead of Recovery Sprint 3**  
> **Date:** 2026-07-09  
> **Validator:** automated re-run of Beta V3 scenario matrix + `make beta-validator-rc`  
> **Baseline:** Beta V3 (`test thesisOs/thesis_os_beta_report_v3.md`, `thesis_os_stats_final.md`)  
> **Environment:** Docker Compose — `http://127.0.0.1:3000` / `http://127.0.0.1:8000`  
> **Prior RC:** `.asep/reports/THESISOS-v2.0.0-rc.2-BETA-VALIDATION.md` (pre-recovery)

---

## Executive verdict

**The product is objectively better on Docker after Recovery Sprint 1–2 — but mostly on connectivity and failure visibility, not UX comprehension.**

| Question | Answer |
|----------|--------|
| Did anti-pattern elimination improve the product? | **Yes** — SSR/API bridge failures (C1, C2, C3, C6) resolved on Docker |
| Did error-contract work improve the product? | **Partially** — failures are visible instead of silent; user still blocked on missing features |
| Is ThesisOS ready for human beta re-test? | **Yes on Docker** — core surfaces load; **No on Cloudflare tunnel** until AP-004 |
| Authorize Recovery Sprint 3 now? | **No** — human Beta Validation 2 recommended first |

---

## Comparison — severity counts (open issues)

Counts reflect **issues still blocking or degrading end-to-end use**, not lines of code changed.

| Metric | Beta V3 baseline | RC-2 (Docker) | Delta | Notes |
|--------|------------------|---------------|-------|-------|
| **Critical (open)** | 6 | **2** | **−4 (−67%)** | C5 + C7 remain; C1/C2/C3/C6 fixed; C4 fixed on Docker |
| **High / Gravi (open)** | 8 | **8** | **0** | UX/discoverability — untouched by Recovery Sprints |
| **Medium (open)** | 6 | **6** | **0** | Polish — untouched |
| **Total cataloged bugs (open)** | 20 | **16** | **−4** | |
| **HTTP routes returning 500** | 2 | **0** | **−2** | `/research/canvas`, `/knowledge/graph` |
| **Surfaces with "fetch failed" in SSR** | 3+ | **0** | **−3+** | `/knowledge`, `/writing`, home loaders |
| **Estimated end-to-end usability** | ~15% | **~35–40%** | **+20–25 pp** | heuristic — see module table below |

> **Environment caveat (mandatory):** Beta V3 ran on **Cloudflare tunnel**; RC-2 ran on **Docker localhost**. AP-001/AP-002 fix **A1 SSR-in-container**; tunnel/client-visible URL failures (**AP-004**) were **not in scope** and may still reproduce C4-class errors in production-like deploys.

---

## Scenario matrix — same routes as Beta V3

| Route | Beta V3 | RC-2 Docker | Delta |
|-------|---------|-------------|-------|
| `/` | 200, progress silent fail | 200, chapters load | ✅ Improved |
| `/research` | 200 | 200 | — |
| `/research/canvas` | **500** SSR exception | **200** | ✅ Fixed (AP-001) |
| `/research/guided` | 200 placeholder | 200 placeholder | — (G7 still open) |
| `/writing` | 200 + **fetch failed** | 200, workspace renders | ✅ Fixed (AP-001) |
| `/sources` | 200 OK | 200 OK | — |
| `/sources/upload` | 200 OK | 200 OK | — |
| `/knowledge` | 200 + **fetch failed** | 200, **7 concepts** (Aura, Abbigliamento, …) | ✅ Fixed (AP-001) |
| `/knowledge/graph` | **500** SSR exception | **200** | ✅ Fixed (AP-001) |
| `/settings` | 200 OK | 200 OK | — |
| `/review` | 200 OK | 200 OK | AP-002: Critical error surface if API down |
| `/ai` | 200 + **TypeError fetch** | 200, **no fetch error in SSR**; conversations API OK | ✅ Fixed on Docker |
| `/library` | 307 → `/sources` | 307 | — |
| `/workspace` | 307 → `/writing` | 307 | — |
| Backend `/health` | OK (V4) | OK | — |
| Backend `/ready` | OK (V4) | OK | — |
| Context API | — | OK (Playwright 2/2) | — |

**Automated gate:** `make beta-validator-rc` → **PASS** (health, 6 HTTP surfaces, context API, Playwright 2/2).

**Guards:** `make ap001-guard` PASS · `make ap002-guard` PASS · `make unit-frontend` 306/306 PASS (prior session).

---

## Per-issue disposition (Beta catalog → RC-2)

### Critical

| ID | Beta V3 symptom | RC-2 status | Recovery link | RC-2 evidence |
|----|-----------------|-------------|---------------|---------------|
| **C1** | Knowledge fetch failed | **FIXED** | AP-001 Theme A | Concepts render; no "fetch failed" in HTML |
| **C2** | Canvas SSR 500 | **FIXED** | AP-001 | HTTP 200; `research-canvas-shell` route reachable |
| **C3** | Graph SSR 500 | **FIXED** | AP-001 | HTTP 200 (was Digest 4130059368) |
| **C4** | AI Chat TypeError | **FIXED (Docker)** | AP-001 client paths | `/conversations` API returns items; no SSR fetch error |
| **C5** | No chapter creation UI | **OPEN** | — (UX backlog) | Empty state still says *"Crea il primo capitolo dalla API"* |
| **C6** | Writing fetch failed | **FIXED** | AP-001 | `writing-workspace` in SSR; chapters exist in API |
| **C7** | New project crash | **PARTIAL** | AP-002 Theme B | `ProjectSwitcher` shows degraded banner on error; crash not re-tested in browser |

### High (Gravi) — all **OPEN**

| ID | Issue | RC-2 |
|----|-------|------|
| G1 | Memoria hidden in Contesto tab | OPEN — needs human UX test |
| G2 | Metric badges inert | OPEN |
| G3 | ⓘ button no-op | OPEN |
| G4 | No revision mode config | OPEN |
| G5 | Auto-save no feedback | OPEN |
| G6 | Source detail sparse | OPEN |
| G7 | Guided research placeholder | OPEN |
| G8 | Revisione → Writing loop | OPEN (depends on C5) |

### Medium — all **OPEN**

M1–M5 unchanged (tab fonte, badge sviluppo, export RIS, session timer, concept chips).

---

## Module usability estimate (Beta V3 → RC-2)

Heuristic comparison using Beta V2 module table methodology — **not** a substitute for human Beta Validation 2.

| Modulo | Beta V3 usable | RC-2 Docker usable | Change |
|--------|----------------|--------------------|--------|
| Home | 90% | 90% | — |
| Sources | 60% | 60% | — |
| Knowledge | **0%** | **~70%** | **+70 pp** |
| Writing | **10%** | **~35%** | **+25 pp** (loads if chapters exist; C5 blocks new users) |
| Research | **5%** | **~45%** | **+40 pp** (hub + canvas/graph HTTP OK) |
| AI Chat | **0%** | **~50%** | **+50 pp** on Docker (API alive; UI not browser-walked) |
| Revisione | 20% | 20% | — |
| Settings | 40% | 40% | — |
| Nuovo Progetto | **0%** | **~20%** | PARTIAL (graceful degrade vs crash) |
| **Overall E2E** | **~15%** | **~35–40%** | **+20–25 pp** |

---

## What Recovery Sprint 1–2 actually changed

### Not this

- Did **not** add chapter creation UI (C5)
- Did **not** fix badge/ⓘ/settings UX (G2–G5)
- Did **not** fix Cloudflare tunnel deploy (AP-004)
- Did **not** prove a human beta tester understands the product better

### This

- **Eliminated a class of SSR misconfiguration** (AP-001) → Knowledge, Canvas, Graph, Writing loaders work in Docker
- **Standardized failure visibility** (AP-002) → degraded banners instead of silent empty states on Important surfaces
- **Installed permanent guards** → `ap001-guard`, `ap002-guard` in `make check` / `make ci`
- **Shifted diagnosis** from "backend down" (V3) to "specific bridges broken / UX gaps" (RC-2)

---

## Recovery Sprint ROI (maintenance measurement)

| Sprint | Theme | AP | Issues directly affected | Engineering artifacts | Product health delta (Docker) | Time | ROI assessment |
|--------|-------|----|--------------------------|-----------------------|-------------------------------|------|----------------|
| **RS-1** | Anti-Pattern Elimination | AP-001 **ELIMINATED** | C1, C2, C3, C6 (SSR) | 10 client files, `ap001-guard`, tests | 500→200 on 2 routes; fetch-failed eliminated on 3+ surfaces | ~1 day | **High** — one pattern → 4 critical fixes |
| **RS-2** | Error Contract | AP-002 **MITIGATED** | Silent home progress, Research hub, ⌘K, Review, ProjectSwitcher | `error-contract-v1.md`, `ApiDegradedBanner`, `ap002-guard` | Failures visible; no new features; C7 crash → degrade | ~1 day | **Medium** — process/observability; limited user-value alone |
| **RS-3** | — | AP-006, UX, AP-004 | — | — | — | — | **Not authorized** pending RC-2 + human beta |

**Hypothesis under test:**

```
Anti-pattern elimination → product improvement
```

**RC-2 result:** **Confirmed for AP-001 (connectivity class).** **Not confirmed for UX class** — High/Medium counts unchanged.

**Alternate hypothesis (still open):**

```
AP elimination ≠ User Value (for UX/discoverability issues)
```

**RC-2 result:** **Supported** — beta tester would still say *"non capisco come creare un capitolo"* (C5) and *"i badge non fanno niente"* (G2).

---

## Research Engine lens (Recovery Sprint observation)

Research Engine remains **frozen** (ADR-0050). This section defines **future observe targets** — not implemented in RE this session.

| Observable | RS-1 | RS-2 | RC-2 |
|------------|------|------|------|
| APs mitigated/eliminated | 1 (AP-001) | 1 (AP-002) | — |
| Critical issues closed | 4 | 0 | 4 net vs baseline |
| Guards added | 1 | 1 | 2 cumulative |
| unit-frontend | 306 PASS | 306 PASS | 306 PASS |
| HTTP 500 routes | −2 | 0 | −2 vs beta |
| Human usability score | — | — | **TBD** (Beta Validation 2) |

---

## Decision record (Product Architect)

| Decision | Status |
|----------|--------|
| Recovery Sprint 3 | **NOT AUTHORIZED** |
| RC-2 Product Validation | **COMPLETE** (this report) |
| Human Beta Validation 2 (same scenarios as V3) | **RECOMMENDED NEXT** |
| Recovery Sprint 3 (AP-006 / UX theme) | **Only after** human beta confirms delta or identifies next blocker class |
| Deployment Sprint (AP-004 tunnel) | **Separate track** — required to validate C4 on public URL |

---

## Recommended next steps

1. **Human Beta Validation 2** — same checklist as V3, on Docker first, then tunnel if deploy sprint runs.
2. **Scorecard sign-off** — Product Lead fills "understands how to create chapter?" (C5) and "can complete writing flow?" manually.
3. **If human beta confirms ~35%+ usability** → authorize **UX Recovery Theme** (C5, G1–G3) *or* **AP-004 Deployment Sprint** for tunnel parity — pick based on cohort environment.
4. **If human beta shows no perceived improvement** → treat as discovery: pivot from AP elimination to UX research / onboarding design.

---

## Artifacts

| Artifact | Path |
|----------|------|
| This report | `.asep/reports/THESISOS-RC-2-RECOVERY-VALIDATION.md` |
| Beta baseline V3 | `test thesisOs/thesis_os_beta_report_v3.md` |
| Beta stats | `test thesisOs/thesis_os_stats_final.md` |
| Recovery log | `docs/recovery-sprint-1-report.md` |
| Anti-pattern registry | `docs/engineering/anti-pattern-registry.md` |
| Error contract | `docs/engineering/error-contract-v1.md` |
| Validator script | `bin/beta-validator-rc.sh` |
| Validator log | `/tmp/beta-validator-rc.log` |

---

## WO-TRACE

```text
Beta V3 (tunnel) → Recovery Sprint 1 (AP-001) → Recovery Sprint 2 (AP-002) → RC-2 (THIS) → Beta Validation 2 (human) → RS-3? / UX theme? / AP-004?
```
