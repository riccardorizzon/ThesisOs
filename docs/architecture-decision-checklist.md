# Architecture Decision Checklist

> **Not an ADR.** A short, uniform gate every reviewer runs **before approving a PR**
> that touches the Runtime Platform (`backend/app/`). It operationalizes the
> Runtime Constitution (C7 review order) and ADR-0030. If any box is checked, follow
> the linked action before merge.

Run top to bottom; stop and resolve before approval.

- [ ] **Constitution** — does the change respect every invariant C1–C8? (`docs/runtime-constitution.md`)
- [ ] **Layer** — does it introduce any new dependency **across** layers (Business / Runtime / Infrastructure)? → must go through composition root + ports (C1, C2, C8)
- [ ] **Public contract** — does it modify a public agent contract, `GraphState`, or the `/chat` shape? → incompatible change requires an **ADR** (C5)
- [ ] **Event** — does it introduce or change a runtime event? → update event model + `docs/runtime-contract.md` §3 (C4)
- [ ] **Runtime API** — does it change `build_graph`, lifecycle, Event Bus, or extension points? → update `docs/runtime-contract.md` §4–§5
- [ ] **ADR needed?** — is this an architectural decision (new boundary, new pattern, incompatible change)? → write/extend an ADR
- [ ] **Runtime Contract update?** — does onboarding guidance need to change? → update `docs/runtime-contract.md`
- [ ] **M4 compatibility** — does it preserve validated M4 behavior, or is deviation ADR-authorized? (C6) → `make unit-m4-recovery` green
- [ ] **Qualification?** — does it need eval / benchmark / dogfood before it can ship? (M5.5)
- [ ] **Promotion?** — does it require a freeze/tag step? (M5.6)

## Review order (Constitution C7)

```text
1. Constitution → 2. Layer → 3. Contracts → 4. Events →
5. Feature → 6. Performance → 7. Code
```

## References

- `docs/runtime-constitution.md` — invariants C1–C8
- `decisions/ADR-0030-agent-runtime-layer-boundaries.md` — layer rules R1–R8
- `docs/runtime-contract.md` — extension points
