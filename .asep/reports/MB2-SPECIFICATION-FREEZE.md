# MB2 — Specification Freeze

- **Date:** 2026-07-05
- **Type:** Governance state transition (not implementation)
- **Capability:** `mb2-engineering-runtime`
- **Certificate:** `.asep/certificates/MB2-SOR-20260705.yaml`

---

## Decision

MB2 Engineering Runtime transitions to:

| Dimension | State |
|-----------|-------|
| Platform capability lifecycle | **SPECIFIED** |
| Specification | **Frozen** |
| Implementation | **Not authorized** |

Sign-off:

> The Engineering Runtime contract is now considered normative. Future implementations
> SHALL conform unless superseded by a newer Specification of Record.

---

## Document chain (complete — no further Runtime documentation planned)

```text
Vision          docs/platform/era-model.md (Era II)
    ↓
ADR             decisions/ADR-0042-engineering-runtime.md
    ↓
SoR             docs/superpowers/specs/mb2-engineering-runtime-spec.md
    ↓
Reference Impl  builder_engine/ (partial — not authorized to extend until MB2-Q)
    ↓
Qualification   MB2-Q1…Q6 (future)
```

---

## Freeze distinction

| Artifact | Specification | Implementation |
|----------|---------------|----------------|
| PX-2 | Frozen (product spec) | **Frozen** (qualified baseline) |
| MB2 | **Frozen** (SoR) | **Open** (not started) |

---

## Next authorized action

1. **PX-3** — first **Runtime Conformance Program** (delivers Sources + stress-tests SoR)
2. **No MB2 code** until Conformance Assessment confirms SoR stability
3. **Future (PX-3 end only):** `.asep/reports/MB2-CONFORMANCE-ASSESSMENT.md`

---

## Phase model (constitutional → conformance → implementation)

```text
Era I / PX-2     Build → Document          (governance demonstrated)
MB2              Specify → Authorize         (SoR frozen — constitutional phase complete)
PX-3             Build → Qualify             (conformance program — validates SoR)
Post-PX-3        Conformance Assessment → Implementation Authorized
```

Implementation authorization chain:

```text
MB2 SoR frozen
  → PX-3 completed
  → MB2-CONFORMANCE-ASSESSMENT (no normative changes required)
  → Implementation Authorized
  → MB2-Q gates / Reference Implementation
```

---

## WO-TRACE

```text
PX-2 COMPLETE/FROZEN → ADR-0042 → runtime-model-v2 → MB2 SoR → SPECIFICATION FREEZE → PX-3 gate
```
