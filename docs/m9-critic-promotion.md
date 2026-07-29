# M9 — Critic — Promotion

**Status:** **Proposed template** — fill gates after implementation + qualify.  
**Spec:** `docs/superpowers/specs/2026-07-29-thesisos-m9-critic-design.md` (**Proposed**).  
**ADR:** 0056 (Critic Loop & Approval Gate) — Proposed until M9.0.

## Summary

M9 activates the **Critic** capability and route, emits `CritiqueCompleted`, bounds writer→critic revise to at most one automatic rewrite, and gates `review → approved` on a passing critique — without GraphState schema changes and without implementing M10 QA.

## Capability map (fill at ship)

| Capability | Milestone | Commit |
|------------|-----------|--------|
| Spec + ADR-0056 Accepted | M9.0 | _TBD_ |
| Critic capability + node | M9.1 | _TBD_ |
| Critic route + events | M9.2 | _TBD_ |
| Bounded revise loop | M9.3 | _TBD_ |
| Approval gate | M9.4 | _TBD_ |
| Qualification + promotion | M9.5 | _TBD_ |

## Promotion gates

```yaml
adrs: proposed_pending_accept
critic_capability: pending
critic_isolation: pending
critic_node: pending
critic_route: pending
revise_loop_bound: pending        # MAX_AUTO_REVISE == 1
non_writer_routes_unchanged: pending
hallucination_fixture: pending
redundancy_fixture: pending
critique_completed_event: pending
approval_requires_pass: pending
graphstate: unchanged             # critique field pre-existed
qa_phase_not_implemented: true
m0_through_m8_tests: pending
scope_creep: false
documentation: pending
knowledge_updated: pending
```

Live:

```yaml
dogfood_critic_fail_then_pass: pending
dogfood_approve_blocked_without_pass: pending
benchmark_b_critique: pending
m9_tag: pending                   # tag m9-complete
```

## Tags

| Tag | SHA | Meaning |
|-----|-----|---------|
| `m9-complete` | _TBD_ | Qualified Critic baseline |

## Explicit non-goals at promotion

- M10 QA phase / `phase='qa'` product gate
- Unlimited revise / supervisor re-entry (M12)
- Outline ops (M8) / citation styles (M7) unless already promoted separately
- Auto-`published`
