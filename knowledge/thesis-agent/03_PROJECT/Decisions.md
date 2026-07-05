# Decisions

Decisioni esplicite del progetto. Modifiche solo via MEMORY UPDATE approvato.

## Corpus bibliografico

| ID | Decisione | Stato |
|----|-----------|-------|
| CORPUS-01 | ~12 autori attivi nel master; non espandere senza approvazione | Congelato |
| CORPUS-02 | Barthes *Mythologies* — **escluso** | Congelato |
| CORPUS-03 | Bourriaud / estetica relazionale come pilastro — **escluso** | Congelato |
| CORPUS-04 | Library-first obbligatorio prima di paragrafi teorici | Congelato |

## Revisione e qualità

| ID | Decisione | Stato |
|----|-----------|-------|
| REV-001 | Rispettare indicazioni strutturali relatrice | Congelato |
| REV-002 | Coerenza terminologica tra capitoli | Congelato |
| REV-003 | Evitare ripetizioni cross-capito | Congelato |
| REV-004 | Citazioni verificabili; no attribuzioni fantasma | Congelato |
| REV-005 | Tono allineato a prima correzione PDF relatrice | Congelato |
| REV-006 | Controllo attribuzioni; A/B; FONDATO/PLAUSIBILE/SPECULATIVO | Congelato |

## Metodo e oggetto

| ID | Decisione | Stato |
|----|-----------|-------|
| METH-01 | Ricerca qualitativa, non quantitativa | Congelato |
| METH-02 | STIGMATA = caso applicativo, non oggetto teorico principale | Congelato |
| METH-03 | Interpretazione conservativa; dubbio → domanda, non ipotesi | Congelato |
| METH-04 | Evidence-first per narrativa processo STIGMATA | Congelato |

## Requisiti istituzionali

| ID | Decisione | Stato |
|----|-----------|-------|
| UNI-01 | `University-Rules.md` approvato (guida Accademia del Lusso + regola progetto §8: **nessuna nota a piè di pagina**, autore-data nel corpo) | **Congelato** 2026-06-30 |
| REL-01 | Regole relatrice R1–R5 validate → `Relatrice-Rules.md` | **Congelato** 2026-06-30 |

## Redazione

| ID | Decisione | Stato |
|----|-----------|-------|
| RED-01 | Italiano accademico per tutta la tesi | Congelato |
| RED-02 | Footnote: **vietate** (vedi UNI-01 §8); sostituisce "minimizzate" | Congelato 2026-06-30 |
| RED-03 | Fonti straniere: studio in traduzione; no quote dirette tradotte non verificate | Congelato |
| RED-04 | Classificazione fonti: approvata / candidata / scartata | Congelato |

## Memoria e workflow

| ID | Decisione | Stato |
|----|-----------|-------|
| MEM-01 | Nessuna memoria permanente senza approvazione utente | Congelato |
| MEM-02 | Note relatrice: analisi → batch domande → attesa → modifiche | Congelato |
| MEM-03 | Due modalità: conversazione vs scrittura accademica | Congelato |

## Piattaforma (migrazione ThesisOS)

| ID | Decisione | Stato |
|----|-----------|-------|
| PLAT-01 | Non migrare system prompt Kimi; ricostruire da chat | Approvato 2026-06 |
| PLAT-02 | Knowledge binaria solo da export Kimi in `04_KNOWLEDGE/` | Approvato 2026-06 |
| PLAT-03 | Comportamento agente in `knowledge/thesis-agent/` | Approvato 2026-06 |
| PLAT-04 | Persona "Cheerleader" importata (`01_SYSTEM/Persona.md`), firewall conv/scrittura | Approvato 2026-06-30 |
| PLAT-06 | Engineering Program binding (META-0): ASEP ↔ thesis-agent migration track | Approvato 2026-06-30 |

## Cronologia fasi (da chat Kimi — run kimi-claw-2026-06)

Ricostruita da `USER.md` (STM). Documenta come si è arrivati agli artefatti congelati.

| Data | Fase / evento | Esito |
|------|---------------|-------|
| 2026-06-17 | Set-up regole operative (FATTO/INFERENZA/VALUTAZIONE; due modalità; note; fonti straniere) | Approvate |
| 2026-06-17 | Analisi guida università + descrizione tesi + prima revisione relatrice (no modifiche) | Report |
| 2026-06-17→19 | FASE CORPUS: CORE THEORY MAP v2.0 → 2 stress test → v2.1 | **Congelato** 2026-06-19 |
| 2026-06-19 | FASE BIBLIOGRAFIA: BIBLIOGRAPHY_MASTER v1.0 | **Congelata** |
| 2026-06-19 | FASE ARCHITETTURA: OUTLINE_MASTER v1.0 | **Congelata** |
| 2026-06-20 | FASE META-DOCUMENTI: STIGMATA_DOCUMENTATION_FRAMEWORK v1.0 | **Congelata** |
| 2026-06-22 | Modalità EVIDENCE-FIRST attivata | — |
| 2026-06-23 | Modalità LIBRARY-FIRST: analisi 4 libri (pipeline identificazione/citation bank) | — |
| 2026-06-24 | Avvio FASE STESURA: §1.1 (Löbach, Csikszentmihalyi) | Bozza |
| 2026-06-24→26 | Revisione puntuale §1.1 (attribuzioni Löbach: distinguere teoria vs interpretazione) | In revisione |

## Da decidere

- Checklist §13 `University-Rules.md` (template Word, frontespizio) — da confermare con segreteria/corso.
- Policy auto-persist draft M6 → chapter (ThesisOS enhancement).
- Quando reimportare testi congelati cap. 1–2 in `ChapterService`.
