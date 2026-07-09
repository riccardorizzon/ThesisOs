# Error Contract v1

> **Document class:** Product architecture contract (ASEP engineering)  
> **Status:** ACTIVE — Recovery Sprint 2 Theme B (B1)  
> **Date:** 2026-07-09  
> **Related:** `docs/engineering/anti-pattern-registry.md` (AP-002), `frontend/lib/apiBase.ts` (AP-001)

---

## Purpose

Define **what happens when an API call fails** — not whether to use `try/catch`.

**AP-002 is not “silent catch”.** It is **absence of policy**: the same failure produces empty UI, error banners, or HTTP 500 depending on the file.

This contract is the policy.

---

## Core rule

> **Never represent an API error as a valid “no data” state** unless the surface is classified **Optional** and documented as such.

`return []` after a failed fetch is **forbidden** when the user would interpret it as “nothing exists”.

`return []` is **allowed** for: empty successful response, local cache miss, optional enrichment, corrupt localStorage parse.

---

## Failure modes by context

| Context | Required behavior | UI pattern |
|---------|-------------------|------------|
| **SSR — Critical** | Error Surface — block or dedicated error view | `ApiErrorBanner`, `*ErrorState`, `*LoadError` |
| **SSR — Important** | Degraded State — page usable + visible warning | `ApiDegradedBanner` + partial content |
| **SSR — Optional** | Degraded or omit — must not block route | Omit metric / hide widget |
| **Client — Critical** | Banner + Retry | `ApiErrorBanner` inline |
| **Client — Important** | Degraded banner or inline warning | `ApiDegradedBanner` |
| **Client — Optional** | Silent OK — previous state preserved | No user-facing error |
| **Background refresh** | Keep previous state; optional dev log | No false empty |

---

## API classification (v1)

### Level 1 — Critical (never simulate empty)

| Surface | Loader | Contract |
|---------|--------|----------|
| Knowledge list / explain | SSR + client | Error Surface (already compliant) |
| Writing context | SSR | Error Surface (`ApiErrorBanner`) |
| Writing chapter editor load | Client | Error in editor shell |
| Sources list / detail | SSR | Error Surface (`SourcesErrorState`) |
| Review context | SSR | Error Surface (required — B2) |

### Level 2 — Important (degrade with visible warning)

| Surface | Loader | Contract |
|---------|--------|----------|
| Home — chapter progress | SSR | Degraded — banner; do not show 0% as success |
| Research hub — concept count | SSR | Degraded — distinguish error vs true empty |
| Outline / chapter list | Client | Degraded — banner; not “Nessun capitolo” on API fail |
| Command palette — chapters | Client | Degraded — message in palette |
| Projects list | Client | Degraded — do not inject fake default project |
| Conversation list | Client | Error Surface (user-facing chat) |

### Level 3 — Optional (may fail silently)

| Surface | Loader | Contract |
|---------|--------|----------|
| Canvas serendipity strip | Client | Optional — empty strip OK |
| Inspector rail enrichment | Client | Optional |
| Linked sources footer prefetch | Client | Optional |
| Corpus search remote boost | Client | Fallback to local search OK |
| Nav badge refresh (`AppShell`) | Background | Previous state OK |

---

## Reference implementations (Pattern B)

```text
frontend/app/knowledge/page.tsx     → KnowledgeExplorerLoadError
frontend/app/writing/page.tsx       → ApiErrorBanner
frontend/app/sources/page.tsx       → SourcesErrorState
```

New code must match the **classification table**, not copy the nearest file blindly.

---

## Out of scope (Theme B) — AP-006

**Unhandled SSR throw** (`research/canvas`, `knowledge/graph`, `review` without try/catch) is **Fault Isolation**, not Error Contract.

Track separately as AP-006 candidate.

---

## CI guard (B2+)

| Guard | Scope |
|-------|--------|
| `make ap002-guard` | SSR `page.tsx`: forbid bare `catch { return []` / `return 0` after API await |

Critical SSR routes must use Pattern B components (enforced by review + guard on known violations).

---

## Theme B micro-sprints

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **B1** | This document + API classification | ✅ |
| **B2** | SSR Important → Degraded; Review → Error Surface | ✅ |
| **B3** | Client Important → Degraded/Banner | ✅ |
| **Guard** | `ap002-guard` in CI | ✅ |

---

**Authority:** Recovery Sprint 2 — Error Contract Standardization  
**Next review:** After Theme B gate PASS
