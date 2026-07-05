# QWO C.3-R3 — OR-3 Re-Qualification Report

**Date:** 2026-06-30  
**WorkOrder:** C.3 · **Type:** QWO · **Run:** **#3** (`C.3-R3`)  
**Capability:** `or-3-corpus`  
**Conversation id:** `6867c597-5e1d-4ad0-bd17-d90a4b12607b`  
**Message id:** `34110fcb-fb62-44a8-b20d-81bdd8c9d17e`  
**Verdict:** **PARTIAL**  
**Disposition:** **REJECTED** (operator 2026-06-30 — see `.asep/reports/C.3-R3-disposition.md`)  
**Next:** C.3-R4 re-QWO

**Authorization:** Level 2 auto — QC Certificate `.asep/certificates/C.3-R3-20260630.yaml`  
**Precondition:** EWO-3 + **EWO-4 Grounding** implemented; backend **rebuilt/restarted**  
**Prior runs:** C.3-R1 PARTIAL (accepted) · C.3-R2 FAIL · investigation ACCEPTED

---

## Supervisor session

| Step | Result |
|------|--------|
| OBSERVE | Next WO: C.3-R3 · `/health` OK · EWO-4 code live in container |
| QC Certificate | PASS — no pending EWO / open STOP |
| Policy | Level 2 auto-authorize QWO |
| Termination | Session iter 1 — no halt pre-execute |
| EXECUTE | QWO ~67s |
| VERIFY | vs Qualification Contract → **PARTIAL** |
| DISPOSITION | **REJECTED** — operator; OR-3 not qualified → **C.3-R4** |

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| EWO-3 implemented | ✅ masters indexed (26 + 99 chunks) |
| EWO-4 implemented | ✅ `[BINDING DECISIONS]` + exclusion-aware retrieval |
| Backend restart | ✅ `docker compose up -d --build backend` |
| Runtime Coverage | ~100% |
| Proposal C.3 approved | ✅ |
| New conversation | ✅ |
| System mutations | **None** |

---

## 2. Test protocol

**Prompt (OR-3 canonical):** unchanged from C.3-R1/R2.

**Runtime boundary:** single POST `/chat`, new session, no attachments.

---

## 3. Agent output (summary)

- **Autori elencati (10):** Löbach, Csikszentmihalyi, Albers, Benjamin, Barthes (*Sistema moda*), Hollander, Sennett, Dorfles, Warburg, Seivewright  
- **Autori mancanti (2):** **Eco**, **Flügel** ❌  
- **Esclusioni:** Barthes *Mythologies* (**CORPUS-02**) + Bourriaud / estetica relazionale (**CORPUS-03**) — **explicit**, cites `[BINDING DECISIONS]` ✅  
- **Ruoli:** frequent **Fondamentale** mis-label (Albers, Benjamin, Barthes, Hollander, Seivewright) vs GT (4 fondamentali only) ⚠️  
- **Opere/capitoli:** many rows «Non specificata nelle fonti fornite» despite Bibliography-Master / Core-Theory-Map in retrieval ⚠️  
- **Sources (10):** Core-Theory-Map, Bibliography-Master, Outline, Stigmata-Framework, Benjamin book, Mythologies (retrieved but correctly excluded in output)

Full text: 3870 chars (execution log `/tmp/c3-r3-parsed.json`).

---

## 4. Ground Truth vs output

| Contract element | C.3-R2 | C.3-R3 | Result |
|------------------|--------|--------|--------|
| ~12 autori + ruolo | ~8/12 | **10/12** | ❌ (Eco, Flügel missing) |
| Fondamentali (4) | 1/4 | 4 named but +6 mis-labelled fond. | ❌ |
| Capitoli mapping | partial | partial; many «non specificata» | ⚠️ |
| CORPUS-02 Mythologies | ❌ absent | ✅ excluded + CORPUS-02 | ✅ **Fixed** |
| CORPUS-03 Bourriaud | ❌ absent | ✅ excluded + CORPUS-03 | ✅ **Fixed** |
| Barthes = *Sistema moda* | ✅ | ✅ | ✅ |
| FOND vs SUPPORTO | partial | confused | ❌ |
| Ricostruzione da sole sorgenti promosse | exclusions fail | exclusions OK; author list incomplete | ⚠️ |

### Availability / Applicability / Completeness

| Dimension | C.3-R1 | C.3-R2 | C.3-R3 |
|-----------|--------|--------|--------|
| **Availability** | partial (40%) | ~100% | ~100% |
| **Applicability** | ✅ exclusions | ❌ regression | ✅ **restored** |
| **Completeness** | insufficient | insufficient | **insufficient** (10/12; roles/opere) |

---

## 5. Failure / partial classification

| Cause | Assessment |
|-------|------------|
| **Primary (resolved vs R2)** | **Grounding Gap** — EWO-4 fixed binding-decision application and exclusion synthesis |
| **Remaining (this run)** | **Completeness Gap** — 2/12 autori missing; FOND/SUPPORTO taxonomy imprecise; opera titles not synthesized from promoted masters |
| **Secondary** | **Reasoning Gap** — model labels several support authors as «Fondamentale» despite GT |
| **Not promotion gap** | Masters + decisions indexed; runtime ~100% |

**Valid PARTIAL** per Qualification Contract §PARTIAL — esclusioni OK; mappa corpus incompleta.

**Not auto-accepted** — requires operator disposition (Level 2 STOP).

---

## 6. Cognitive pipeline attribution

```text
Ground Truth   ✅  (masters + decisions present)
Retrieval      ✅  (Bibliography-Master, Core-Theory-Map in top-10)
Grounding      ✅  (post-EWO-4: CORPUS-02/03 applied via [BINDING DECISIONS])
Reasoning      ⚠️  (author count, role taxonomy, opera synthesis)
```

This run validates the **Grounding** category: problem was not Alignment/Promotion.

---

## 7. Capability Coverage (post C.3-R3)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          ~100%
Qualification Coverage:    PARTIAL (~75% — exclusions + 10/12 autori)
Evidence Coverage:         100%
```

---

## 8. Lifecycle

| Field | Value |
|-------|-------|
| `or-3-corpus` lifecycle | **`approved`** (unchanged — not `qualified`) |
| OR-3 log | **PARTIAL** (C.3-R3) |
| Unblocks OR-4 | **No** (C.3-R3 PARTIAL rejected; C.3-R4 pending) |

---

## 9. WO-TRACE

```text
C.3-R1 PARTIAL (accepted) → EWO-3 Alignment
  → C.3-R2 FAIL → Investigation ACCEPTED (Grounding Gap)
  → EWO-4 Grounding → C.3-R3 PARTIAL (exclusions fixed; completeness gap)
```

Next run id if re-QWO: **C.3-R4** (only if operator rejects PARTIAL or mandates re-run).

---

## QC Certificate reference

`.asep/certificates/C.3-R3-20260630.yaml` — pre-execute PASS; post-run **PARTIAL** triggers STOP (T2).
