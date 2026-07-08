# ThesisOS v2.0.0-rc.2 — M7 Release Candidate Bundle

> **Status:** **APPROVED** — tag `v2.0.0-rc.2` @ `5039df77`; staging deploy authorized 2026-07-08  
> **Date:** 2026-07-08  
> **Product program:** M7 Product Hardening (ADR-0044)  
> **Scope:** M7 + M7.1 + M7.2 complete on `main`  
> **Supersedes:** `v2.0.0-rc.1` @ `fd23ad70` (PX-6 baseline — retained as milestone tag)

---

## 1. Executive summary

ThesisOS M7 program is complete. All product surfaces are DB-backed, stubs removed,
and UX polish (M7.2) passes the RC gate. This bundle authorizes `v2.0.0-rc.2` for
staging deployment and beta onboarding.

| Milestone | Status |
|-----------|--------|
| M7 Product Hardening | complete |
| M7.1 Stub Removal | complete |
| M7.2 UX Polish | complete |
| Release Candidate | **this bundle** |
| Beta | authorized |

---

## 2. Baseline

```text
Branch:     main
RC commit:  5039df77 docs(m7): dashboard merge log — M7.2 commit hash
Product:    2dda483f feat(m7.2): complete UX polish — RC gate
Tag:        v2.0.0-rc.2 → 5039df77
Prior RC:   v2.0.0-rc.1 → fd23ad70 (PX-6, unchanged)
CI:         green @ 5039df77 (make ci)
E2E:        m7-product-flow 9/9 + e2e-m7 CI job
```

---

## 3. What is in v2.0.0-rc.2 (M7 delta over rc.1)

### M7 Product Hardening
- DB-backed Sources, Knowledge, Chat, Writing, Review
- Upload → index workflow
- BibTeX + chapter `.md` export
- Playwright M7 product flow

### M7.1 Stub Removal
- Zero runtime stub fallbacks in product paths
- API-only context, corpus, canvas, knowledge

### M7.2 UX Polish
- `ApiErrorBanner` + retry
- Empty states with actionable CTAs
- Loading skeletons + lazy canvas/graph bundles
- Coach marks (5 steps)
- Playwright in CI (`e2e-m7` job)
- `docs/user/getting-started.md`

---

## 4. Qualification summary

| Qualification | Result |
|---------------|--------|
| `make ci` | PASS @ `5039df77` |
| `make gate-m7.2` | PASS (unit + Playwright) |
| `make dogfood-m7` | available (requires Vertex ADC) |
| Beta validator Day 0 | see execution report |

---

## 5. Known limitations

Unchanged from v2.0 RC bundle — see `docs/KNOWN_LIMITATIONS.md` (L-01…L-05).

Additional M7 notes:
- Single-user; no auth/multi-tenant
- Mobile writing is read-only below 768px
- Cloudflare quick tunnel (beta public URL) has no uptime SLA

---

## 6. Deployment checklist

- [x] M7.2 gate PASS
- [x] `make ci` green on `main`
- [x] Tag `v2.0.0-rc.2` on `5039df77`
- [x] Deploy staging (docker compose @ main)
- [x] Beta validator Day 0
- [ ] Human cohort onboarded (5–10)
- [ ] 7-day stability monitor
- [ ] GA package (separate approval)

---

## 7. Rollback plan

1. Revert staging to `v2.0.0-rc.1` (`fd23ad70`) if critical blockers.
2. Hotfix on `main`, tag `v2.0.0-rc.3`.
3. Do **not** delete `px6-complete` or `v2.0.0-rc.1` tags.

---

## 8. WO-TRACE

```text
M7 → M7.1 → M7.2 → THIS BUNDLE → v2.0.0-rc.2 → beta → GA (future)
```
