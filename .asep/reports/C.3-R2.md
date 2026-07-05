# QWO C.3-R2 — OR-3 Re-Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.3 · **Type:** QWO · **Run:** **#2** (`C.3-R2`)  
**Capability:** `or-3-corpus`  
**Conversation id:** `fcc5b450-a33d-4130-8696-e3befedb1ca7`  
**Message id:** `f4c3ecaa-b292-42c9-aa29-bb86eb482627`  
**Verdict:** **FAIL**

**Authorization:** Level 2 auto — QC Certificate `.asep/certificates/C.3-R2-20260630.yaml`  
**Precondition:** EWO-3 implemented; C.3-R1 PARTIAL **accepted**  
**Prior run:** C.3-R1 PARTIAL (accepted) — preserved

---

## Supervisor session

| Step | Result |
|------|--------|
| OBSERVE | Next WO: C.3-R2 · `/health` OK |
| QC Certificate | PASS — no pending EWO / open STOP |
| Policy | Level 2 auto-authorize QWO |
| Termination | Session iter 1 — no halt pre-execute |
| EXECUTE | QWO ~58s |
| VERIFY | vs Qualification Contract → **FAIL** |

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| EWO-3 implemented | ✅ masters indexed (26 + 99 chunks) |
| Runtime Coverage | ~100% |
| Proposal C.3 approved | ✅ |
| New conversation | ✅ |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-3 canonical):** unchanged from C.3-R1.

---

## 3. Agent output (summary)

- **Supporto (7):** Albers, Hollander, Barthes (*Sistema della moda*), Dorfles, Eco, Benjamin, Seivewright — opere + capiti largely from Core-Theory-Map ✅  
- **Fondamentali:** only Sennett explicit; states sources lack full fondamentali list ❌  
- **Missing autori:** Löbach, Csikszentmihalyi, Warburg, Flügel ❌  
- **Esclusioni:** agent states *«non è possibile indicare quali autori esclusi»* ❌ **CORPUS-02/03 not applied**

Full text: 2838 chars (execution log).

---

## 4. Ground Truth vs output

| Contract element | C.3-R1 | C.3-R2 | Result |
|------------------|--------|--------|--------|
| ~12 autori + ruolo | 6/12 | ~8/12 | ❌ |
| Fondamentali (4) | 1/4 | 1/4 | ❌ |
| Capitoli mapping | partial | improved (support) | ⚠️ |
| CORPUS-02 Mythologies | ✅ | ❌ absent | **Regression** |
| CORPUS-03 Bourriaud | ✅ | ❌ absent | **Regression** |
| Barthes = *Sistema moda* | ⚠️ | ✅ | ✅ |
| FOND vs SUPPORTO | ❌ | partial | ⚠️ |
| Ricostruzione da sole sorgenti promosse | ❌ | partial authors; exclusions fail | ❌ |

### Availability / Applicability / Completeness

| Dimension | C.3-R1 | C.3-R2 |
|-----------|--------|--------|
| **Availability** | partial (40% runtime) | high (~100% masters) |
| **Applicability** | ✅ exclusions | ❌ **regression** |
| **Completeness** | insufficient | insufficient (8/12; no exclusions) |

---

## 5. Failure classification

| Cause | Assessment |
|-------|------------|
| **Primary** | Agent failed to retrieve/apply M2 **decisions** (CORPUS-02/03) despite masters promoted — **Applicability regression** vs C.3-R1 |
| **Secondary** | Fondamentali list (Bibliography-Master § A.1) not synthesized in output — **Completeness** gap |
| **Not promotion gap** | Masters + books indexed; runtime coverage ~100% |
| **Agent limitation** | Run-to-run retrieval variance on exclusions |

**Valid FAIL** per Qualification Contract §FAIL — esclusioni assenti.

---

## 6. Capability Coverage (post C.3-R2)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          ~100%
Qualification Coverage:    FAIL (0% this run)
Evidence Coverage:         100%
```

---

## 7. Lifecycle

| Field | Value |
|-------|-------|
| `or-3-corpus` lifecycle | **`approved`** (unchanged — not `qualified`) |
| OR-3 log | **FAIL** (C.3-R2) |
| Unblocks OR-4 | **No** |

**Outer Loop:** FAIL disposition requires operator — no auto-spawn EWO.

---

## 8. WO-TRACE

```text
C.3-R1 PARTIAL (accepted) → EWO-3 → C.3-R2 FAIL (exclusions regression)
```

Next run id if re-QWO: **C.3-R3** (after remediation).

---

## QC Certificate reference

`.asep/certificates/C.3-R2-20260630.yaml` — pre-execute PASS; post-run failure is **qualification**, not certificate invalidation.
