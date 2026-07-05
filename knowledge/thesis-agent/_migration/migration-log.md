# Migration log — run kimi-claw-2026-06

**Data esecuzione:** 2026-06-30
**Origine:** `_inbox/kimi-claw/kimi claw/` (immutabile, intatta)
**Runbook:** `docs/kimi-to-thesisos-migration-runbook.md`
**Manifest:** `_migration/MANIFEST.tsv` (42 voci)
**Checksum origine:** `_migration/checksums.sha256` · **derivati:** `_migration/derived-checksums.sha256`

## Fasi eseguite

- **Fase 0** — import grezzo (utente). 14 md + 6 zip in `_inbox/kimi-claw/`.
- **Fase 1** — inventario + checksum. → `inventory.md`, `checksums.sha256`.
- **Fase 2** — analisi semantica. → `inventory.md`.
- **Fase 3** — mappatura. → `migration-plan.md` §1.
- **Fase 4** — piano + decisioni D1–D6 approvate (GO 2026-06-30).
- **Fase 5** — migrazione (vedi sotto).
- **Fase 6** — ricostruzione memoria (merge sotto) + validazione checksum.

## Operazioni Fase 5/6

### Copie materializzate (con front-matter di provenienza)
- `03_PROJECT/`: Core-Theory-Map, Outline-Master, Stigmata-Framework, Bibliography-Master, Thesis-Description, audit/Stress-Test-1, audit/Stress-Test-2.
- `chapters/`: ch01 (§1.1–1.3), ch02 (§2.1–2.4), ch03 (CAP03).
- `04_KNOWLEDGE/Books/`: 8 estrazioni libro (Hollander, Sennett, Löbach, Albers, Benjamin, Seivewright, Csikszentmihalyi, Barthes*).
- `04_KNOWLEDGE/University/Guida-Redazione-Tesi.md`, `Bibliography/Tesi-bibliografia-completa.md`, `References/bozza-1.1-processo-creativo.md`.
- `04_KNOWLEDGE/Relatrice/`: `prima-revisione-2026-05-27.pdf` + `pages/page_1..4.png` (full-res).

\* Barthes *Mythologies* importato ma **ESCLUSO** dal corpus (Decisions CORPUS-02).

### Merge / estrazioni (ricostruzione intelligenza agente)
- **D1 Persona:** nuovo `01_SYSTEM/Persona.md`; firewall in `Conversation.md` + `Identity.md`.
- **Memoria:** `05_MEMORY/Permanent.md` ← regole operative (`MEMORY.md`) + profilo utente (`USER.md` LTM).
- **Decisioni:** `03_PROJECT/Decisions.md` ← cronologia fasi (`USER.md` STM) + PLAT-04/05.
- **Stato:** `03_PROJECT/Thesis-State.md` ← identità progetto (Ilaria Marelli, Accademia del Lusso) + stato "materializzato".
- **Bibliografia:** `03_PROJECT/Bibliography.md` → punta a master + file libri reali.
- **Relatrice:** `transcription/page_1..4.md` (lettura PROPOSTA, `DA VERIFICARE`).

### Non promosso (resta solo in `_inbox`, archivio)
`AGENTS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `TOOLS.md`, `skills/*`,
`memory_consolidation/*`, `memorized_diary/*`, `memory/2026-06-25.md`.

## Note operative
- Git LFS **non installato**: `.gitattributes` pronto, ma i binari non sono ancora
  committabili via LFS. Installare `git-lfs` prima del commit dei file in `Relatrice/`.
- Export grezzo e `_migration/extracted/` esclusi da git (`.gitignore`); integrità
  verificabile via `checksums.sha256`.

## Follow-up aperti
- Validare le trascrizioni relatrice → poi compilare `03_PROJECT/Relatrice-Rules.md`.
- Compilare `03_PROJECT/University-Rules.md` dalla guida importata.
- Pulizia OCR libri (rinviata, D5).
- Fase 2 runtime: promozione `memories` + ingest `documents` (M3/M4) + capitoli M6.
