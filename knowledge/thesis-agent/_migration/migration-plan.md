# Piano di migrazione — export Kimi Claw → ThesisOS (run: kimi-claw-2026-06)

Fasi 3–4 del runbook. **Nessuna operazione eseguita finché l'utente non approva.**
Origine immutabile: `_inbox/kimi-claw/kimi claw/` (mai modificata).

Azioni: **copia** (materializza/sposta una copia) · **merge** (unisce a file esistente) ·
**estrai** (deriva contenuto nuovo) · **lascia** (resta solo in `_inbox`, archivio).

---

## 1. Mappatura (Fase 3)

### Intelligenza dell'agente → memoria / metodo / progetto

| Origine | Destinazione ThesisOS | Azione |
|---------|-----------------------|--------|
| `MEMORY.md` | `05_MEMORY/Permanent.md` (+ cross-check `02_METHOD/*`) | merge |
| `USER.md` (profilo + LTM) | `05_MEMORY/Permanent.md` (sez. profilo utente) | estrai + merge |
| `USER.md` (STM: sequenza fasi CORPUS→…→STESURA) | `03_PROJECT/Decisions.md` (cronologia decisioni) | estrai + merge |
| `CORE_THEORY_MAP_v2.1.md` | `03_PROJECT/Core-Theory-Map.md` | copia (materializza) |
| `OUTLINE_MASTER_v1.0.md` | `03_PROJECT/Outline-Master.md` | copia |
| `STIGMATA_DOCUMENTATION_FRAMEWORK_v1.0.md` | `03_PROJECT/Stigmata-Framework.md` | copia |
| `BIBLIOGRAPHY_MASTER_v1.0.md` | `03_PROJECT/Bibliography.md` | merge |
| `STRESS_TEST_REPORT_v2.0.md` | `03_PROJECT/audit/Stress-Test-1.md` | copia |
| `STRESS_TEST_2_REPORT_v2.0.md` | `03_PROJECT/audit/Stress-Test-2.md` | copia |

### Testi tesi (capitoli)

| Origine | Destinazione | Azione |
|---------|--------------|--------|
| `chapters/ch01/*` (§1.1–1.3) | `chapters/ch01/` | copia |
| `chapters/ch02/*` (§2.1–2.4) | `chapters/ch02/` | copia |
| `chapters/ch03/CAP03_*` (§3.x) | `chapters/ch03/` | copia |

### Corpus documentale → `04_KNOWLEDGE/`

| Origine | Destinazione | Azione |
|---------|--------------|--------|
| `descrizione_tesi_md_.md` | `03_PROJECT/Thesis-Description.md` | copia |
| `GUIDA_REDAZIONE_TESI.md` | `04_KNOWLEDGE/University/` | copia |
| `Tesi_bibliografia_completa.md` | `04_KNOWLEDGE/Bibliography/` + merge in `03_PROJECT/Bibliography.md` | copia + merge |
| `user_pasted_..._Il_processo_creativo...txt` | `04_KNOWLEDGE/References/` | copia |
| `job_001` Hollander | `04_KNOWLEDGE/Books/Hollander_Sex-and-Suits.md` | copia + rinomina |
| `job_002` Sennett | `04_KNOWLEDGE/Books/Sennett_The-Craftsman.md` | copia + rinomina |
| `job_003` Löbach | `04_KNOWLEDGE/Books/Lobach_Disegno-Industriale.md` | copia + rinomina |
| `job_004` Albers | `04_KNOWLEDGE/Books/Albers_Interaction-of-Color.md` | copia + rinomina |
| `job_006` Benjamin | `04_KNOWLEDGE/Books/Benjamin_Opera-Arte-Riproducibilita.md` | copia + rinomina |
| `job_007` Seivewright | `04_KNOWLEDGE/Books/Seivewright_Basics-Fashion-Research.md` | copia + rinomina |
| `job_008` Csikszentmihalyi | `04_KNOWLEDGE/Books/Csikszentmihalyi_Flow.md` | copia + rinomina |
| `job_009` Barthes | `04_KNOWLEDGE/Books/Barthes_Mythologies.md` | copia + rinomina |
| `prima_revisione_..._tesi_.pdf` | `04_KNOWLEDGE/Relatrice/prima-revisione-2026-05-27.pdf` | copia + rinomina |
| `pdf_pages/page_1..4.png` | `04_KNOWLEDGE/Relatrice/pages/` | copia (vedi D3) |

### Persona conversazionale (D1 risolta: importare con firewall)

| Origine | Destinazione | Azione |
|---------|--------------|--------|
| `IDENTITY.md` + `SOUL.md` (Cheerleader / Spark Engine) | `01_SYSTEM/Persona.md` (nuovo) | estrai + materializza |
| firewall persona↔lavoro | rafforza `01_SYSTEM/Conversation.md` + `01_SYSTEM/Identity.md` | merge |

### Da archiviare e NON promuovere (restano solo in `_inbox`)

`AGENTS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `TOOLS.md`, `skills/*`,
`memory_consolidation/*`, `memorized_diary/*`, `memory/2026-06-25.md`. → azione **lascia**.

---

## 2. Piano operativo (Fase 4) — riepilogo per azione

**Copia/materializza (nuovi file):** 3 artefatti master + 2 stress test + 8 capitoli +
8 libri + guida università + descrizione tesi + bozza §1.1 + PDF relatrice + scansioni.
**Merge (in file esistenti del blueprint):** `MEMORY.md`+`USER.md` → `05_MEMORY/Permanent.md`;
STM → `03_PROJECT/Decisions.md`; bibliografie → `03_PROJECT/Bibliography.md`.
**Lascia invariato (archivio `_inbox`):** scaffolding piattaforma, persona, skills, motore memoria, diari.
**Tracciabilità (P2):** ogni file derivato riceve front-matter di provenienza; ogni riga in `_migration/MANIFEST.tsv`; log in `_migration/migration-log.md`.

### Nuove cartelle da creare
`03_PROJECT/audit/`, `chapters/ch01..ch03/`, `04_KNOWLEDGE/Relatrice/pages/`.

---

## 3. Decisioni (risolte con l'utente)

**D1 — Persona "Cheerleader" → IMPORTARE con firewall netto.**
La personalità (`IDENTITY.md`/`SOUL.md`) viene mantenuta, ma separata rigorosamente dal lavoro:
- `01_SYSTEM/Persona.md` (nuovo) = voce companion (hype, emoji, slancio), **attiva solo in modalità conversazione**.
- `01_SYSTEM/Conversation.md` = firewall esplicito: Modalità 1 (conversazione) persona ON; Modalità 2 (scrittura accademica) persona **OFF totale** (sobrio, neutrale, niente emoji/esclamazioni).
- `01_SYSTEM/Identity.md` + `02_METHOD/Writing-Rules.md` restano garanti del rigore nel testo tesi.

**D2 — Capitoli → mirror markdown in `chapters/` ora.** ✓

**D3 — Scansioni relatrice → vedi metodo "scrittura a penna" qui sotto.**
Risolta: preservare PDF originale + PNG full-res (no varianti lossy) come evidenza immutabile;
creare companion di trascrizione per pagina (proposta con livelli di confidenza + `DA VERIFICARE`,
mai come fatto confermato). Conferma sub-scelta in chat.

**D4 — Binari/Git → `.gitignore` su `_inbox/kimi-claw/` + Git LFS per i binari tenuti.** ✓

**D5 — Libri OCR → importare come sono in `Books/` con nota OCR nel front-matter.** ✓

**D6 — Blueprint → posso arricchire i file `03_PROJECT/*` e `05_MEMORY/Permanent.md` esistenti.** ✓

---

## 4. Metodo per la revisione manoscritta della relatrice (D3)

Le annotazioni sono scrittura a penna scansionata: massima cura, niente automatismi ciechi.

1. **Fedeltà massima, nessun downscale.** Tenere `prima-revisione-2026-05-27.pdf` (sorgente migliore)
   + `page_1..4.png` full-res in `04_KNOWLEDGE/Relatrice/`. Scartare `_compressed.jpg`/`_small.png`
   (perdono dettaglio della grafia) → restano solo in `_inbox`.
2. **Niente OCR/auto-trascrizione come verità.** La grafia corsiva è inaffidabile in OCR e le regole
   di progetto marcano queste note come "alto rischio interpretativo".
3. **Companion di trascrizione strutturato** in `04_KNOWLEDGE/Relatrice/transcription/page_N.md`,
   una voce per annotazione con: pagina · ancora (§/riga di riferimento) · lettura proposta verbatim ·
   confidenza (`leggibile` / `incerto` / `illeggibile`) · flag `DA VERIFICARE`.
4. **Tutto come proposta, validazione in batch** (workflow relatrice esistente): l'agente può produrre
   una prima lettura dalle scansioni full-res, ma ogni voce resta proposta finché l'utente non conferma.
5. **Provenienza:** immagini/PDF nel `MANIFEST.tsv`; il companion ha front-matter verso le immagini sorgente.

Sub-scelta da confermare: **(a)** produco subito la prima lettura-proposta delle 4 pagine, oppure
**(b)** creo solo i template vuoti da compilare insieme.

---

## 5. Gate

**STOP.** Decisioni D1–D6 acquisite. Eseguo la Fase 5 (migrazione) solo dopo il tuo **GO finale**
+ la sub-scelta D3 (a/b). L'export grezzo in `_inbox/` resta intatto in ogni caso.
