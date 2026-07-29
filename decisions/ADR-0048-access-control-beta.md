# ADR-0048: Access control — single-user beta + optional shared token (M8 multi-user deferred)

**Status:** Accepted  
**Date:** 2026-07-29  
**Plane:** Product  
**Related:** ADR-0047 (multi-thesis workspace), ADR-0044 (product phase), `docs/demo/DEMO-GROWTH-PLAN.md`

## Context

ThesisOS beta is **single-operator**. Public Cloudflare tunnels expose the stack
without login. Full multi-user auth (accounts, sessions, per-user isolation)
is an M8 / GA concern and must not be stubbed with fake login UI.

## Decision

1. **Default (local / trusted VM):** no authentication. Operator trust model.
2. **Optional shared beta gate:** when `BETA_ACCESS_TOKEN` is set on the backend,
   all routes except `/health` and `/ready` require header `X-Beta-Token: <token>`.
   Same value may be injected by the Next.js middleware / FE env for browser `/api/*`.
   This is **not** multi-user — one shared secret for a closed cohort.
3. **Multi-thesis ≠ multi-user:** ADR-0047 `project_id` isolation remains the
   workspace boundary for one operator with N theses.
4. **M8 (not authorized here):** real identity (session/JWT/OIDC), per-user data
   plane, invite flows. Requires GA package + dedicated Work Order.

## Consequences

- Ops scripts and `make ops-check` keep working when the token is **unset**.
- Public demo may enable the token without building an auth product.
- Product UI must declare single-user honestly (Settings / handout).

## Anti-goals

- No fake login page.
- No JWT stub that pretends multi-tenant security.
- No silent change of default local DX.
