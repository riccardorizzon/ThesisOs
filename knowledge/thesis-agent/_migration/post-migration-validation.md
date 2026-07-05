# Da validare dopo la migrazione

Check post-migrazione (run: `kimi-claw-2026-06`). **Non** validazione file-per-file:
verifica che nulla di importante sia andato **perso o alterato** e che ThesisOS possa
**ragionare e lavorare** come Kimi Claw.

**Domanda guida:** *Se cancellassi Kimi oggi, ThesisOS saprebbe già tutto quello che serve?*

**Legenda esito:** ✅ OK · ⚠️ Parziale (funziona ma incompleto) · ❌ Gap · 🔒 Bloccato (serve approvazione utente)

**Audit eseguito:** 2026-06-30 (post Fase 5 migrazione, pre-promozione runtime).

---

## 1. Identità dell'agente (priorità massima)

| Elemento Kimi | Destinazione ThesisOS | Esito | Note |
|---------------|----------------------|-------|------|
| Persona "Thesis" / Cheerleader (`IDENTITY.md`, `SOUL.md`) | `01_SYSTEM/Persona.md` | ✅ | Importata con firewall D1 |
| Regole comportamento (`MEMORY.md`, `Behaviour`) | `01_SYSTEM/Behaviour.md` + `05_MEMORY/Permanent.md` | ✅ | Blueprint + merge export |
| Workflow operativo (fasi, library-first, revisione) | `02_METHOD/*`, `03_PROJECT/Decisions.md` | ✅ | |
| Filosofia progetto (STIGMATA caso applicativo, conservatorismo) | `03_PROJECT/Project-Rules.md`, `Decisions.md` | ✅ | |
| Cosa deve / non deve fare | `01_SYSTEM/Behaviour.md`, `02_METHOD/Writing-Rules.md` | ✅ | |
| Firewall chat vs scrittura accademica | `01_SYSTEM/Conversation.md`, `Identity.md` | ✅ | Persona OFF in modalità scrittura |
| Scaffolding piattaforma (`AGENTS.md`, cron, heartbeat) | resta in `_inbox` | ✅ intenzionale | Non runtime ThesisOS |

**Verdetto §1:** ✅ L'identità operativa-tesi è presente. Non è un clone 1:1 del workspace
OpenClaw (es. cron/kimi-search assenti per design).

**Da approvare tu:** conferma che `Persona.md` rispecchia la voce Kimi che vuoi in chat.

---

## 2. Memoria permanente

| Elemento | Dove | Esito | Note |
|----------|------|-------|------|
| Regole approvate (note, fonti straniere, FATTO/INFERENZA, …) | `05_MEMORY/Permanent.md` | ✅ | Da `MEMORY.md` Kimi |
| Profilo utente / metodo di lavoro | `05_MEMORY/Permanent.md` | ⚠️ | Distillato da `USER.md` LTM, non verbatim |
| Preferenze relatrice validate | `Relatrice-Rules.md` | ✅ | REL-01 congelato 2026-06-30 |
| Preferenze scrittura | `02_METHOD/Writing-Rules.md` | ✅ | |
| Stato tesi | `03_PROJECT/Thesis-State.md` | ✅ | Aggiornato post-export |
| Convenzioni | `03_PROJECT/Terminology.md` | ✅ | Seed blueprint, non da export |
| Cose da non fare (Barthes, Bourriaud, …) | `Decisions.md` CORPUS-02/03 | ✅ | |
| Protocollo MEMORY UPDATE | `01_SYSTEM/Memory-Protocol.md` | ✅ | |

**Verdetto §2:** ✅ Memoria blueprint completa; **promossa in runtime** (Fase B 2026-06-30).

---

## 3. Struttura del progetto

| Artefatto | File | Esito | Integrità |
|-----------|------|-------|-----------|
| CORE THEORY MAP v2.1 | `03_PROJECT/Core-Theory-Map.md` | ✅ | checksum origine in front-matter |
| OUTLINE_MASTER v1.0 | `03_PROJECT/Outline-Master.md` | ✅ | idem |
| BIBLIOGRAPHY_MASTER v1.0 | `03_PROJECT/Bibliography-Master.md` | ✅ | idem |
| STIGMATA FRAMEWORK v1.0 | `03_PROJECT/Stigmata-Framework.md` | ✅ | idem |
| Stress test corpus | `03_PROJECT/audit/Stress-Test-*.md` | ✅ | |
| Capitoli §1.1–2.4, §3.x | `chapters/ch01..ch03/` | ✅ | 8 file |
| Descrizione tesi | `03_PROJECT/Thesis-Description.md` | ✅ | |
| Collegamenti indice → master | `Bibliography.md`, `Thesis-State.md` | ✅ | |

**Verdetto §3:** ✅ Struttura intellettuale del progetto materializzata e collegata.

---

## 4. Corpus documentale

| Categoria | Atteso (export Kimi) | Presente | Esito |
|-----------|---------------------|----------|-------|
| Libri (8 estrazioni OCR) | job_001–009 (no 005) | `04_KNOWLEDGE/Books/` × 8 | ⚠️ **md OCR**, non PDF originali |
| Guida università | GUIDA_REDAZIONE | `University/Guida-Redazione-Tesi.md` | ✅ |
| Bibliografia progetto | Tesi_bibliografia_completa | `Bibliography/Tesi-bibliografia-completa.md` | ✅ |
| Revisione relatrice | PDF + scansioni | `Relatrice/prima-revisione…pdf` + 4 PNG | ✅ |
| Bozza §1.1 | clipboard txt | `References/bozza-1.1-processo-creativo.md` | ✅ |
| Materiale STIGMATA (foto, sketch) | non in export | cartella vuota (`.gitkeep`) | ❌ **assente** — atteso |
| Papers / References extra | — | solo bozza §1.1 | ⚠️ |

**Verdetto §4:** ⚠️ Tutto ciò che **c'era** nell'export è migrato; mancano PDF libri
(non erano nell'export) e **tutto il materiale STIGMATA binario** (framework sì, foto no).

---

## 5. Regole della tesi

| Tipo | File | Esito | Note |
|------|------|-------|------|
| Regole università (oggettive) | `03_PROJECT/University-Rules.md` | ✅ | UNI-01; §8 no footnote |
| Regole relatrice | `03_PROJECT/Relatrice-Rules.md` | ✅ | REL-01 R1–R5 |
| Convenzioni bibliografiche | `Bibliography-Master.md` + `Tesi-bibliografia-completa.md` | ✅ | Autore-data; note vietate (UNI-01) |
| Formato citazioni / impaginazione | `University-Rules.md` §7–10 | ✅ | Checklist §13 corso ancora aperta |

**Verdetto §5:** ✅ Regole istituzionali e relatrice chiuse; promosse in runtime (Fase B).

---

## 6. Decisioni storiche

| Elemento | Dove | Esito |
|----------|------|-------|
| REV-001 – REV-006 | `Decisions.md` | ✅ |
| CORPUS congelato, esclusioni Barthes/Bourriaud | `Decisions.md` | ✅ |
| METH, RED, MEM | `Decisions.md` | ✅ |
| Cronologia fasi CORPUS→STESURA | `Decisions.md` | ✅ |
| Motivazioni stress test / audit | `audit/Stress-Test-*.md`, `Core-Theory-Map.md` | ✅ |
| Alternative già valutate (v2.0→v2.1 corpus) | Stress test reports | ✅ |
| Pipeline LIBRARY-FIRST (identificazione, citation bank) | `USER.md` LTM → Permanent parziale | ⚠️ | Non documentata come procedura standalone in `02_METHOD/` |

**Verdetto §6:** ✅ Le decisioni **non si ripeterebbero**; ⚠️ la pipeline operativa
library-first è implicita, non un runbook dedicato.

---

## 7. Stato reale del lavoro

| Elemento | Dove | Esito |
|----------|------|-------|
| Fasi congelate (CORPUS, BIBLIO, ARCHITETTURA, META) | `Thesis-State.md`, `Decisions.md` | ✅ |
| Cap. 1–2 congelati | `Thesis-State.md`, `chapters/` | ✅ |
| §3.1 pronto per revisione | `chapters/ch03/CAP03_*` (stato interno) | ✅ |
| §3.2+ non iniziato | `Thesis-State.md` | ✅ |
| Materiale STIGMATA da popolare | `Stigmata-Framework.md` | ⚠️ framework sì, evidenza no |
| Prossimi passi | `TODO.md` | ⚠️ **obsoleto** — non aggiornato post-migrazione |

**Verdetto §7:** ⚠️ Stato intellettuale corretto; backlog `TODO.md` da allineare.

---

## 8. Capacità operative

| Capacità Kimi | Documentata in markdown | Runtime ThesisOS | Esito |
|---------------|-------------------------|------------------|-------|
| Leggere nuovi libri (library-first) | `02_METHOD/Research-Protocol.md` | M3 ingest non configurato | ⚠️ |
| Aggiornare bibliografia | `Bibliography.md` workflow | M7 non promosso | ⚠️ |
| Modificare capitoli | `chapters/` mirror | M6 ChapterService non collegato | ⚠️ |
| Mantenere memoria (MEMORY UPDATE) | `Memory-Protocol.md` | DB `memories` non promosso | ⚠️ |
| Proporre fonti (candidate/scartate) | `Source-Classification.md` | — | ✅ doc |
| FATTO / INFERENZA / VALUTAZIONE | `Behaviour.md` | — | ✅ doc |

**Verdetto §8:** ⚠️ Capacità **descritte** nel blueprint; **non ancora eseguibili**
via ThesisOS finché non si fa promozione memoria + ingest (step 4 del tuo ordine).

---

## 9. Tracciabilità

| Elemento | File | Esito |
|----------|------|-------|
| Manifest migrazione | `_migration/MANIFEST.tsv` (42 voci) | ✅ |
| Checksum export grezzo | `_migration/checksums.sha256` (20 file, verificati OK) | ✅ |
| Checksum derivati | `_migration/derived-checksums.sha256` | ✅ |
| Front-matter su file derivati | `source`, `source_sha256`, `migration_run` | ✅ |
| Export immutabile | `_inbox/kimi-claw/` intatto | ✅ |
| Log operazioni | `_migration/migration-log.md` | ✅ |

**Nota:** il `sha256` nel manifest è quello del **file origine**; i derivati hanno hash
diverso per il front-matter aggiunto — comportamento atteso (P2).

**Verdetto §9:** ✅ Tracciabilità auditabile.

---

## 10. Stress test (capacità del sistema)

Simulazione: *ThesisOS deve rispondere usando solo `knowledge/thesis-agent/`*
(senza re-imparare da Kimi).

| # | Domanda / compito | Esito simulato | Gap se ⚠️/❌ |
|---|-------------------|----------------|-------------|
| T1 | Spiegare struttura completa tesi | ✅ | `Outline-Master.md` |
| T2 | Elencare regole relatrice | 🔒 | `Relatrice-Rules.md` vuoto; solo proposte in `transcription/` |
| T3 | Libri del corpus attivo | ✅ | `Bibliography-Master.md` (~12 autori) |
| T4 | Stato ogni capitolo | ✅ | `Thesis-State.md` + metadata in `chapters/` |
| T5 | Spiegare framework STIGMATA | ✅ | `Stigmata-Framework.md` |
| T6 | Aggiornare voce bibliografia | ⚠️ | Procedura in doc; nessun DB/runtime |
| T7 | Proporre stesura paragrafo rispettando regole | ⚠️ | Regole in doc; relatrice non validate; runtime assente |

**Verdetto §10:** ⚠️ **4/7 pieni**, 1 bloccato (relatrice), 2 parziali (runtime).
La migrazione **file** è riuscita; la migrazione **operativa** no finché non chiudi §5 + step 4.

---

## 11. Operational Readiness (gate finale — aggiunto 2026-06-30)

Verifica che ThesisOS **lavori** come Kimi Claw, non solo che i file esistano.
Sette test pratici OR-1 … OR-7; eseguiti sull'**agente vivo** dopo promozione runtime.

| Test | Contenuto | Baseline pre-runtime |
|------|-----------|---------------------|
| OR-1 | Ricostruire struttura completa tesi | ✅ PASS |
| OR-2 | Spiegare framework STIGMATA | ✅ PASS |
| OR-3 | Corpus + quando usare ciascuna fonte | ✅ PASS |
| OR-4 | Regole università + relatrice | 🔒 bloccato (tua revisione) |
| OR-5 | Decisioni prese vs aperte | ✅ PASS |
| OR-6 | Scrivere paragrafo rispettando regole | ⚠️ PARTIAL |
| OR-7 | Aggiornare memoria/bib/stato tracciato | ⚠️ PARTIAL |

**Migrazione conclusa** ⇔ tutti OR **PASS** (zero FAIL) **e** E2E **PASS**.

→ Specifica OR + E2E: `_migration/operational-readiness.md`
→ Log esecuzioni: `_migration/operational-readiness-log.md`

---

## 12. End-to-End Project Test — E2E (gate integrazione)

Simula una **sessione continua** di lavoro reale sulla tesi. Eseguito **dopo** OR PASS.

| Step | Azione |
|------|--------|
| E2E-1 | Leggere fonte corpus (library-first, A/B) |
| E2E-2 | Aggiornare bibliografia |
| E2E-3 | MEMORY UPDATE se necessario (con approvazione) |
| E2E-4 | Proporre integrazione nell'outline |
| E2E-5 | Scrivere paragrafo (uni + relatrice + progetto) |
| E2E-6 | Aggiornare Thesis-State + Changelog |

**Criteri globali:** contesto continuo · decisioni chiuse non riaperte · tracciabilità ·
zero violazioni regole.

**Baseline:** 🔒 non eseguibile (richiede OR PASS + runtime + regole approvate).

Scenario default: Albers → §3.2 outline. Dettaglio in `operational-readiness.md` § E2E.

**ThesisOS operativo** ⇔ OR + E2E PASS.

---

## Riepilogo esecutivo

| Area | Esito |
|------|-------|
| 1 Identità agente | ✅ |
| 2 Memoria permanente | ✅ |
| 3 Struttura progetto | ✅ |
| 4 Corpus documentale | ⚠️ |
| 5 Regole tesi | ✅ |
| 6 Decisioni storiche | ✅ |
| 7 Stato lavoro | ⚠️ |
| 8 Capacità operative | ⚠️ |
| 9 Tracciabilità | ✅ |
| 10 Stress test | ⚠️ |
| 11 Operational Readiness | ⏳ Fase C |
| 12 E2E Project Test | ⏳ dopo OR PASS |

### Cosa NON è andato perso (confermato)

- 4 artefatti master + 2 stress test + 8 capitoli
- Regole operative `MEMORY.md` + profilo LTM
- Decisioni REV/CORPUS/METH e cronologia fasi
- 8 libri (estrazioni), guida, bibliografia, revisione relatrice
- Persona + firewall conversazione/scrittura
- Export grezzo intatto + manifest

### Cosa manca o è incompleto (onesto)

1. **Materiale STIGMATA binario** → non era nell'export Kimi
2. **PDF libri originali** → export aveva solo estrazioni OCR md
3. **Checklist §13 University-Rules** (template Word, frontespizio) → da confermare con corso
4. **Fase C–D** → OR-1…OR-5 PASS live; OR-6 PARTIAL (C.6-R1); OR-7 + E2E pending
5. **Commit git** → knowledge/thesis-agent ancora largely uncommitted

---

## Ordine di chiusura (allineato al tuo piano)

```
META-0 — Engineering Program binding     ✅
Fase A — Validazione regole              ✅
Fase B — Promozione runtime              ✅

Fase C — Operational Readiness (WorkOrders C.1…C.7)
  [x] OR-1 … OR-5 su agente vivo → PASS
  [ ] OR-6 → PARTIAL (C.6-R1) — disposition EWO-7B o C.6-R2
  [ ] OR-7 su agente vivo → PASS
  → program: .asep/programs/thesis-agent-migration.yaml

Fase D — E2E (WorkOrder D.1)
  [ ] E2E-1 … E2E-6 sessione continua → PASS

Fase E — Release baseline (WorkOrder E.1)
  [x] KNOWN_LIMITATIONS.md + manifest + release notes + operational runbook
  [x] E.1 report + capability registry freeze
  [ ] Commit + git tag (operator — at baseline commit)
```

Dettaglio test OR-1 … OR-7: **`operational-readiness.md`**

### Validazione relatrice (solo ciò che compromette il futuro)

Non 42 voci una per una: conferma **pattern ad alto impatto** se la lettura ti convince
(dopo aver visto scansioni + `transcription/page_*.md`):

| ID | Pattern | Impatto se sbagliato |
|----|---------|---------------------|
| R1 | Nome completo autore alla 1ª citazione | citazioni errate in tutta la tesi |
| R2 | "È tuo? Se no, cita!" / distinguere intuizione vs fonte | plagio / attribuzioni fantasma |
| R3 | Separare paragrafi + `(Autore, anno)` | struttura e bibliografia |
| R4 | Affermazioni categoriche → cautela / prova | metodo relatrice |
| R5 | Nomi completi stilisti (Balenciaga, …) | REV-004 |

Rispondi quando hai visto: **"post-migrazione: R1–R5 ok"** (o correzioni) +
**"university-rules: ok"** → procediamo a `Relatrice-Rules.md` e promozione.

---

*Questo documento sostituisce l'approccio "validare ogni file" con validazione per
capacità. Le trascrizioni granulari restano in `Relatrice/transcription/VALIDATION.md`
come supporto per R1–R5, non come gate principale.*
