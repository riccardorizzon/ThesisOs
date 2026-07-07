# ADR-0044: Product Phase — ThesisOS Primary, ASEP Maintenance

**Status:** Accepted  
**Date:** 2026-07-07  
**Supersedes:** implicit "platform-first" delivery mode  
**Related:** ADR-0043 (ASEP Core 1.0 maintenance freeze), `plans/m7-product-hardening-plan.md`

## Context

Repository audits (2026-07-07) show:

- ASEP Engineering Runtime and governance: ~67% mature, sufficient for maintenance.
- ThesisOS product: ~62% mature; core backend exists but UI relies on stubs, broken import route, non-persistent review/chat.

Continuing platform expansion yields low user value. The highest leverage work is wiring existing capabilities into a continuous user experience.

## Decision

1. **ThesisOS is the primary delivery track** (Track A, ~90% effort).
2. **ASEP evolves only when ThesisOS is blocked** (Track C, ~2% effort).
3. **Runtime maintenance only** for shared infra bugs (Track B, ~8% effort).
4. **M7 gate blocks new features** until the UI workflow passes without silent stubs:

   ```text
   Import → Index → Knowledge → Search → Chat → Writing → Review → Export
   ```

5. **No new ASEP capabilities** (PX-EXEC Phase 3–4, plugins, governance expansion) until M7 gate PASS, except break/fix.

6. **ASEP evolution rule (binding):**

   > **ASEP evolves only when ThesisOS requires it.**

   No framework work triggered by future possibility. Every ASEP change must cite a concrete ThesisOS blocker in the PR description.

7. **Stub policy:** no silent fallback to demo data in happy path; errors must be explicit or gated behind `DEMO_MODE` with visible badge.

8. **Post-M7 sequence:** M7 → M7.1 (stub removal) → M7.2 (UX polish) → Release Candidate → Beta → M8 (new features). No M8 work before M7.2 complete.

## Consequences

### Positive

- Focused delivery on user-visible outcomes.
- Reduced dual-path orchestration confusion (Era I vs Era II).
- Clear gate for M8+ planning.

### Negative

- OpenAPI / README drift addressed in Wave 4, not Wave 1.
- Some PX-1 stub modules remain until M7 Wave 2–3.

## Compliance

- M7 work orders reference this ADR.
- PRs during M7 declare `Layer: Business` unless bugfix-only.
- ASEP changes require justification: "Which M7 gate criterion is blocked?"
