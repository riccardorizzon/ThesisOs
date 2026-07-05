# OR-4 Pre-flight Audit — Normative Runtime Coverage

**Date:** 2026-06-30  
**WorkOrder:** C.4 (proposal **approved** — QWO **not** executed)  
**Purpose:** Measure **Runtime Coverage** from observed data. This value **authorizes** C.4-R1; it is not a contract presupposition.

---

## Authorization pipeline

```text
C.4 Proposal (approved)
        ↓
Pre-flight Runtime Audit  ← this report
        ↓
Measured Runtime Coverage
        ↓
C.4-R1 QWO Authorization
```

Proposal-time estimates are **informative only** — see `.asep/proposals/C.4-or-4-constraint-compliance.md` §7.1.

---

## Method

For each Normative Ground Truth source required by OR-4 (ThesisOS instance):

| Check | Meaning |
|-------|---------|
| **Repository** | File frozen in `knowledge/thesis-agent/` |
| **Promoted** | Present in runtime M2 and/or M3/M4 |
| **Indexed** | M2 row present with substantive content, or document `status=indexed` |
| **Search** | `/search` returns chunks traceable to that artifact (not homonyms) |

**Critical distinction:** repo existence → **Ground Truth Coverage** only.  
Promoted + retrievable without workspace → **Runtime Coverage**.

---

## Results

| Source | Wt | Repo | Promoted | Indexed | Search (artifact) | Runtime credit |
|--------|-----|------|----------|---------|-------------------|----------------|
| `university-rules` memory (UNI-01) | 35% | ✅ | ✅ M2 | ✅ (8398 chars) | ✅ | **35%** |
| `relatrice-rules` memory (REL-01) | 35% | ✅ | ✅ M2 | ✅ (3804 chars) | ✅ | **35%** |
| `decisions` (UNI/REL/REV/RED-02) | 15% | ✅ | ✅ M2 | ✅ (4502 chars) | ✅ markers | **15%** |
| `University-Rules.md` digest doc | 10% | ✅ | ❌ M3 | ❌ | ❌ | **0%** |
| `Relatrice-Rules.md` digest doc | 5% | ✅ | ❌ M3 | ❌ | ❌ | **0%** |
| `Guida-Redazione-Tesi.md` OCR | 5% | ✅ | ✅ M3 | ✅ 131 chunks | ✅ | **5%** |

### Measured Capability Coverage (OR-4)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          90%   (measured — not proposal estimate)
Qualification Coverage:    pending
Evidence Coverage:         pending (pre-flight complete)
Traceability Coverage:     pending (assessed at QWO)
```

---

## Notes

1. **M2 memories contain full digest text** — Fase B promoted UNI-01 and REL-01 into `university-rules` and `relatrice-rules` keys. Digest markdown files were **not** separately uploaded to M3/M4 (same pattern as pre-EWO-3 corpus masters).
2. **90% Runtime Coverage** — sufficient to authorize **C.4-R1** per contract (C.4.1 Acquisition testable on live agent). Missing 10% = digest docs not indexed as separate M3 artifacts; **EWO-5A** candidate only if QWO shows Structural FAIL despite M2 content.
3. **Guida OCR** is auxiliary — subordinate to `University-Rules.md` digest in GT hierarchy.
4. `/health` → **200 OK** at audit time.

---

## QWO authorization

| Gate | Status |
|------|--------|
| C.4 proposal approved | ✅ 2026-06-30 |
| Pre-flight complete | ✅ this report |
| Measured Runtime Coverage recorded | ✅ **90%** |
| **C.4-R1 authorized** | ✅ (subject to QC + Level 2 policy at execute) |

---

## WO-TRACE

This audit does **not** change capability lifecycle (`or-4-rules` remains `approved`).  
Coverage update only — lifecycle advances on **C.4-R1 PASS** only.
