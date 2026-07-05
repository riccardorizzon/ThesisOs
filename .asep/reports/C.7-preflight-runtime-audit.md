# OR-7 Pre-flight Audit — Memory Runtime Coverage

**Date:** 2026-07-01  
**WorkOrder:** C.7 (proposal **approved** — QWO **not** executed)  
**Purpose:** Measure Runtime Coverage for Memory Runtime Integrity inputs. Authorizes **C.7-R1** prerequisite when operator dispatches QWO.

---

## Authorization pipeline

```text
C.7 Proposal (approved + conditions)
        ↓
Pre-flight Runtime Audit  ← this report
        ↓
Measured Runtime Coverage (85%)
        ↓
C.7-R1 QWO (separate authorization — not implicit)
```

**Operator conditions (recorded):**

- OR-7 strictly deterministic and procedural
- No writing quality / reasoning evaluation
- No automatic permanent memory writes
- OR-3…OR-6 pre-qualified; violations → Invariant Regression only

---

## Method

Same artifact-strict pattern as C.5/C.6 pre-flight audits.

| Check | Meaning |
|-------|---------|
| **Repository** | File frozen in `knowledge/thesis-agent/` |
| **Promoted** | M2 memory and/or M3/M4 document |
| **Indexed** | M2 substantive content or document searchable |
| **Search** | `/search` returns traceable chunks for manifest/protocol queries |

Live probes: `/health`, `/memory`, `/search` against `http://localhost:8000`.

---

## Results

| Source | Wt | Repo | Promoted | Indexed / Searchable | Credit |
|--------|-----|------|----------|----------------------|--------|
| M2 `thesis` (Thesis-State snapshot) | 30% | ✅ | ✅ pinned, 4088 chars | ✅ cap. 3 / PRONTO PER REVISIONE | **30%** |
| M2 `decision` key=`decisions` (registry) | 25% | ✅ | ✅ 4502 chars | ✅ CORPUS / Congelato markers | **25%** |
| M2 `editable` (Memory-Protocol overlay) | 25% | ✅ | ✅ 40529 chars | ✅ MEMORY UPDATE / Changelog / Permanent | **25%** |
| `Bibliography-Master` M3 (manifest GT) | 15% | ✅ | ✅ indexed | ✅ search top hit | **15%** |
| `Bibliography.md` digest M3 | 5% | ✅ | ❌ separate doc | ❌ | **0%** |

### Measured Capability Coverage (OR-7)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          85%   (measured)
Qualification Coverage:    pending
Evidence Coverage:         100% (pre-flight)
Traceability Coverage:     pending (QWO)
```

---

## Scenario alignment (C.7 canonical prompt)

| Prompt element | Runtime support | Status |
|----------------|-----------------|--------|
| MEMORY UPDATE PROPOSAL format | M2 `editable` contains protocol block | ✅ |
| Thesis-State §3.2 delta | M2 `thesis` has cap. 3 stesura table (§3.x) | ✅ |
| Changelog row format | Protocol + editable reference `Changelog.md` | ✅ |
| Bibliography candidata | Bibliography-Master searchable; attivi/esclusi in GT | ✅ |
| Frozen masters read-only | M2 `decisions` + thesis master table | ✅ |
| `/health` | 200 OK | ✅ |

**Note:** `Bibliography.md` operational index not separately indexed — same pattern as C.5
(`Changelog.md` / digest docs). Manifest workflow covered via Bibliography-Master + editable
protocol. **EWO-8A** candidate only if C.7-R1 Structural FAIL.

---

## Oracle readiness (M-01…M-09)

| ID | Pre-flight |
|----|------------|
| M-01…M-08 | Inputs promoted — evaluable on live output |
| M-09 State Atomicity | Contract defined in proposal §1.1b — evaluable on bundle coherence in output |

---

## QWO authorization

| Gate | Status |
|------|--------|
| C.7 approved | ✅ 2026-07-01 |
| Pre-flight complete | ✅ this report |
| Measured Runtime Coverage | ✅ **85%** |
| **C.7-R1** | Pre-flight satisfies prerequisite; **requires explicit QWO dispatch** |

---

## WO-TRACE

```text
C.7 APPROVED → pre-flight EXECUTE → Runtime Coverage 85% → C.7-R1 prerequisite satisfied
```

Does **not** change `or-7-memory-update` lifecycle beyond **`approved`**. Qualification only on **C.7-R1 PASS**.
