# OR-3 Pre-flight Audit — Repository vs Runtime

**Date:** 2026-06-30  
**WorkOrder:** C.3 (proposal approved — QWO **not** executed)  
**Purpose:** Measure Capability Coverage from **observed data**, not estimates.

---

## Method

For each Ground Truth source required by OR-3:

| Check | Meaning |
|-------|---------|
| **Repository** | File frozen in `knowledge/thesis-agent/` |
| **Promoted** | Present in runtime M2/M3/M4 |
| **Indexed** | Document status `indexed` (or M2 row present) |
| **Search** | `/search` returns chunks **from that artifact** (not homonyms) |
| **Chat probe** | Short `/chat` retrieval test (not QWO verdict) |

**Critical distinction (Engineering Program):**

- ✅ Markdown in repo → **Ground Truth Coverage**
- ✅ Promoted + retrievable in conversation **without workspace** → **Runtime Coverage**

Search hits from *other* documents that mention similar keywords **do not** count as GT artifact coverage.

---

## Results

| Source | Wt | Repo | Promoted | Indexed | Search (artifact) | Runtime credit |
|--------|-----|------|----------|---------|-------------------|----------------|
| `Bibliography-Master.md` | 35% | ✅ | ❌ | ❌ | ❌ (hits → Stigmata-Framework, Tesi-bib) | **0%** |
| `Core-Theory-Map.md` | 25% | ✅ | ❌ | ❌ | ❌ (hits → Stigmata-Framework refs only) | **0%** |
| `Decisions.md` CORPUS | 25% | ✅ | ✅ M2 | ✅ | ✅ memory | **25%** |
| Books OCR (`04_KNOWLEDGE/Books/`) | 10% | ✅ 8 files | ✅ 8/8 | ✅ 8/8 | ✅ per-book | **10%** |
| `Tesi-bibliografia-completa.md` | 5% | ✅ | ✅ | ✅ | ✅ | **5%** |

### Measured Capability Coverage (OR-3)

```text
Ground Truth Coverage:     100%
Runtime Coverage:          40%   (was ~58% estimate — revised down)
Qualification Coverage:    pending
Evidence Coverage:         pending
```

---

## Books promoted (Fase B)

| File | Runtime status |
|------|----------------|
| Albers_Interaction-of-Color.md | indexed |
| Barthes_Mythologies.md | indexed ⚠️ **CORPUS-02 excluded** |
| Benjamin_Opera-Arte-Riproducibilita.md | indexed |
| Csikszentmihalyi_Flow.md | indexed |
| Hollander_Sex-and-Suits.md | indexed |
| Lobach_Disegno-Industriale.md | indexed |
| Seivewright_Basics-Fashion-Research.md | indexed |
| Sennett_The-Craftsman.md | indexed |

**Not in repo Books folder / not promoted:** Warburg, Barthes *Sistema della moda*, Dorfles, Eco, Flügel (GT authors without dedicated OCR doc in Fase B).

---

## Search false-positive note

Query `BIBLIOGRAPHY_MASTER Löbach` returns 5 hits — **none** from `Bibliography-Master.md` (document absent). Top hits: Stigmata-Framework, Guida, Tesi-bibliografia-completa.

Query `CORPUS-02 Mythologies escluso` returns **Barthes_Mythologies.md** OCR — contradictory runtime signal vs CORPUS-02.

---

## Chat probe (retrieval only — conv `92083ca4-f73d-47d4-b827-e220f0559fbb`)

Prompt (OR-3-like, abbreviated):

```text
Elenca gli autori del corpus attivo con opera e ruolo. Indica cosa è escluso.
```

| Probe check | Result |
|-------------|--------|
| Multiple authors named (≥6/8 sampled) | ✅ |
| Mythologies excluded | ✅ |
| Bourriaud excluded | ✅ |
| Fondamentale / supporto distinction | ❌ |
| Chapter mapping (Löbach cap.1, Albers cap.3, …) | ❌ (not verified in excerpt) |

Agent can **partially** answer from books + decisions; **cannot** fully reconstruct master corpus map without promoted masters.

---

## Conclusion

1. **Proposal C.3 remains valid** — measured Runtime Coverage **40%**, not 58%.
2. **C.3-R1 QWO** likely → **PARTIAL** or **FAIL** (promotion gap on masters) → **EWO-3 Alignment** candidate.
3. **No EWO required** for books already promoted — gap is **masters**, not OCR existence in repo.
4. Proceed to **C.3-R1** when operator authorized — pre-flight complete.

---

## WO-TRACE

This audit does **not** change capability lifecycle. Coverage update only.
