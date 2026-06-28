# ASEP Review — <PHASE>

Review order (Constitution C7): Constitution → Layer → Contracts → Events → Feature → Performance → Code.

## Architecture Decision Checklist (`docs/architecture-decision-checklist.md`)
- [ ] Respects Runtime Constitution C1–C8
- [ ] No new cross-layer dependency (Business/Runtime/Infrastructure)
- [ ] No public contract changed without ADR (agent JSON, GraphState, /chat, event vocab)
- [ ] New/changed runtime events documented (event model + runtime-contract §3)
- [ ] Runtime API changes documented (runtime-contract §4–§5)
- [ ] ADR needed? written/extended if so
- [ ] Runtime Contract updated if onboarding changed
- [ ] M4 compatibility preserved (or ADR-authorized)
- [ ] Qualification needed? (eval/benchmark/dogfood)
- [ ] Promotion needed? (freeze/tag)

## Verdict
- PASS / STOP — <reason if STOP>
