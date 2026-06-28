# Qualification

Gates required before any `PASS`. Run in order; STOP on first red.

```text
make ci → make unit-m4-recovery → milestone unit/behavior tests → (benchmark) → (dogfood)
```

| Gate | When |
|------|------|
| `make ci` | always |
| `make unit-m4-recovery` | always (M4 must stay unchanged — C6) |
| milestone unit/behavior tests | always |
| benchmark (B_lat / B_ground) | capability `qualification` only |
| dogfood (conversation + grounded) | capability `qualification` only |

Rules:
- Never weaken or skip a test to make a gate pass.
- If red and not trivially fixable within scope → STOP and report.
- Never claim `PASS` without having run these gates this run.
