# QWO C.6-R2 — OR-6 Academic Artifact Production Re-Qualification Report

**Date:** 2026-07-01  
**WorkOrder:** C.6 · **Type:** QWO · **Run:** **#2** (`C.6-R2`)  
**Capability:** `or-6-write-paragraph` · **Domain:** Procedural · **Sensitivity:** reasoning-sensitive  
**Conversation id:** `8290ba23-937a-4eee-9bb8-683cfef3928a`  
**Message id:** `cf6c8bf5-9cd0-40b4-abd4-323a587f147c`  
**Verdict:** **PARTIAL**

**Precondition:** EWO-7B implemented · backend restarted (bind-mount hot-load) · oracle unchanged  
**Prior runs:** C.6-R1 PARTIAL (REJECT → EWO-7B)

---

## 1. Pre-flight

| Check | Result |
|-------|--------|
| `/health` | 200 OK |
| EWO-7B deployed | ✅ `academic_production.py` live in backend |
| Prompt path audit (local + DB memory) | ✅ author-date instruction present; numeric `[n]` instruction **absent** |
| New conversation | ✅ |
| System mutations | **None** |

### Prompt path verification (methodological gate)

Live wire composition (MemoryService + OR-6 prompt + Albers chunk) confirms:

```text
✅ author-date instruction in system prompt
✅ "Do NOT use numeric bracket citations" present
✅ "Academic writing mode (OR-4 / REL-03 / UNI-01)" block present
✅ Source header: [Source 1] Albers (1963) — Albers Interaction of Color, p. 3
❌ "bracketed numbers like [1], [2]" absent
```

**Conclusion:** production path transmits EWO-7B correctly. Any residual `[n]` in output is **not** caused by stale routing defaults.

---

## 2. Test protocol

**Prompt (OR-6 canonical — verbatim, unchanged from C.6-R1):**

```text
Scrivi un paragrafo di prova per §3.2 colore e Josef Albers in modalità scrittura
accademica. Applica REV-006, separazione A/B, livelli FONDATO/PLAUSIBILE dove
pertinente, firewall persona OFF. Etichetta lo stato del testo.
```

**Duration:** ~47.9s · **Sources (SSE):** 10 · **Output length:** ~1700 chars · **Word count:** 229

---

## 3. Agent output (full text)

```text
Certamente. Ecco una bozza di paragrafo per la sezione §3.2, redatta seguendo le direttive fornite.

***

### 3.2 Il colore come interazione: l'approccio di Josef Albers

La trattazione del colore come elemento progettuale trova un fondamento teorico imprescindibile nel lavoro di Josef Albers e nella sua teoria dell'interazione cromatica [2]. Secondo Albers, nessun colore può essere percepito in isolamento; il suo carattere è definito quasi esclusivamente dalla relazione con i colori adiacenti. Egli distingue nettamente tra il "fatto fisico" – la proprietà chimica di un pigmento o una specifica lunghezza d'onda – e il "fatto percettivo", ovvero l’effetto psichico e instabile che il colore genera nell'osservatore [2]. Questo scarto è governato da fenomeni come il contrasto simultaneo, per cui due colori a contatto si influenzano reciprocamente, alterando la percezione di entrambi. **(FONDATO)**

In questa prospettiva, la scelta di una palette cromatica nel fashion design trascende la mera selezione di tinte e si configura come una precisa posizione progettuale [2]. Il designer non si limita a "usare" i colori, ma, applicando i principi di Albers, "costruisce" un'esperienza percettiva specifica, sfruttando la natura relazionale del colore per guidare l'occhio e generare determinate atmosfere. La dimensione cromatica del capo d'abbigliamento cessa così di essere un attributo puramente decorativo per diventare un elemento strutturale nella costruzione del suo significato complessivo. **(INFERENZA / APPLICAZIONE B)**

***

**Stato:** Bozza di Prova
```

---

## 4. Oracle diff (W-01…W-12)

| ID | Criterion | Result | Notes |
|----|-----------|--------|-------|
| W-01 | Paragraph exists | ✅ | 229 words; Albers + colore present |
| W-02 | Persona OFF | ✅ | No emoji, `!`, blocklist |
| W-03 | A/B separation | ✅ | `Secondo Albers` + fashion design application block |
| W-04 | Attribution marker | ✅ | `(FONDATO)`, `Secondo Albers` |
| W-05 | Evidence level tag | ✅ | FONDATO present |
| W-06 | Autore-date | ❌ | Uses `[2]` ×3; **no** `(Albers, 1963)` or `Albers (1963)` |
| W-07 | No footnotes | ✅ | Absent |
| W-08 | Status label | ✅ | `Bozza di Prova` |
| W-09 | No unilateral freeze | ✅ | Absent |
| W-10 | Excluded authors | ✅ | Mythologies/Bourriaud absent |
| W-11 | Source anchor | ✅ | `[2]` markers (numeric — satisfies W-11 but conflicts W-06) |
| W-12 | Academic language | ✅ | Italian function tokens ≥3 |

**Oracle score:** 11/12 PASS · **1 FAIL** (W-06 — same class as C.6-R1)

---

## 5. Sub-capability matrix

| Sub-cap | Verdict | Signal |
|---------|---------|--------|
| **C.6.1 Production Mode** | **PASS** | W-02, W-12 (chatty intro is Artifact Issue — non-blocking) |
| **C.6.2 Source-Constrained Synthesis** | **PASS** | W-01, W-03, W-04, W-11; W-10 clean |
| **C.6.3 Normative Conformance in Prose** | **FAIL** | W-06 — autore-date absent despite prompt |
| **C.6.4 Probative Labeling** | **PASS** | W-05, W-08, W-09 |

**Composite:** C.6.3 FAIL → parent **cannot PASS**.

---

## 6. Failure classification (post-EWO-7B)

| Class | Applies? | Rationale |
|-------|----------|-----------|
| Production path defect (stale prompt) | **No** | Wire audit confirms EWO-7B instructions live |
| **Model non-compliance** | **Yes** | Model emitted `[2]` despite explicit prohibition + `(Albers, 1963)` example in prompt |
| Invariant Regression | No | IR-* clean |
| Structural | No | Paragraph + retrieval OK |

**Disposition tree (operator methodology):**

```text
Prompt contains ACADEMIC_CITATION_INSTRUCTION?  YES (verified)
Model output uses [n]?                           YES
→ Model variance / instruction-following gap — NOT a re-open of EWO-7B root cause
```

---

## 7. Comparison C.6-R1 vs C.6-R2

| Signal | C.6-R1 | C.6-R2 |
|--------|--------|--------|
| W-06 | FAIL `[2]` | FAIL `[2]` |
| Prompt author-date rule | ❌ absent (systemic) | ✅ present (EWO-7B) |
| A/B explicit labels | Explicit Blocco A/B | Implicit A/B |
| Word count | 335 | 229 |
| Traceability | 100% | ≥80% (estimated) |

**Regression:** none on C.6.1/C.6.2/C.6.4 sub-capabilities. **No improvement** on W-06 despite corrected production path.

---

## 8. Recommended next action

**Do not** ACCEPT PARTIAL (operator disposition stands).

**Do not** re-run C.6-R3 without additional production-path enforcement.

Proposed **EWO-7C** (Production Path — Citation Enforcement):

1. Remove "numbered sources" priming language in academic grounding header.
2. Add inline few-shot example of correct `(Albers, 1963)` usage in `ACADEMIC_PRODUCTION_BLOCK`.
3. Optional: single-turn **retry guard** in `conversation_node` when academic mode detects `\[\d+\]` without author-date in draft (rewrite instruction — no oracle change).

Then **C.6-R3** re-QWO.

---

## 9. Verdict

**PARTIAL** — EWO-7B production path **verified** but W-06 **not resolved** on live model output. C.6.3 FAIL persists. No Invariant Regression.

**Lifecycle:** `or-6-write-paragraph` remains **`approved`** — not `qualified`.

**Supervisor:** STOP (T2 — QWO PARTIAL disposition pending operator on EWO-7C vs retry policy).

---

## WO-TRACE

```text
EWO-7B PASS → backend restart → C.6-R2 EXECUTE → prompt path verified → W-06 FAIL (model) → PARTIAL → STOP
```
