# Kimi Claw → ThesisOS — Migration Runbook

Processo riutilizzabile per migrare **qualsiasi** export di Kimi Claw (o
piattaforma chat analoga) dentro la knowledge base `knowledge/thesis-agent/` di
ThesisOS, senza perdere informazioni e senza rompere la struttura esistente.

Questo documento descrive **come** fare la migrazione, non solo lo specifico
export di giugno 2026. Va seguito ogni volta che arriva nuovo materiale da Kimi.

---

## 1. Principi (non negoziabili)

**P1 — Immutabilità dell'export.**
L'export di Kimi Claw non viene mai modificato. Tutte le elaborazioni avvengono
su copie. La copia grezza resta la *fonte di verità* per verifiche future e non
va cancellata dopo la migrazione.

**P2 — Tracciabilità completa.**
Ogni file migrato mantiene un riferimento alla sua origine (percorso originale,
hash, data di migrazione) e ogni trasformazione è documentata, così è sempre
possibile ricostruire come un contenuto è stato adattato a ThesisOS.

---

## 2. Cartelle coinvolte

```text
knowledge/thesis-agent/
├── _inbox/
│   └── kimi-claw/        # Fase 0: copia grezza IMMUTABILE (mai modificata)
├── _migration/           # Fase 1+: audit trail (inventario, mappa, manifest, log)
├── 01_SYSTEM/            # identità, comportamento, conversazione, memory-protocol
├── 02_METHOD/            # protocolli ricerca/revisione/scrittura, regole
├── 03_PROJECT/           # stato tesi, decisioni, bibliografia, terminologia, artefatti
├── 04_KNOWLEDGE/         # corpus binario (vedi 04_KNOWLEDGE/README.md)
│   ├── Books/ Papers/ University/ Relatrice/
│   └── References/ Images/ STIGMATA/ Bibliography/
├── 05_MEMORY/            # Permanent / Temporary / Changelog
└── chapters/             # (opzionale) testi capitolo → ThesisOS M6
```

- `_inbox/kimi-claw/` = input immutabile (P1).
- `_migration/` = solo artefatti di processo durevoli (inventario, mappa,
  manifest di tracciabilità, log). Non cancellare.

---

## 3. Il workflow (Fasi 0–6)

Ogni fase ha un output verificabile. Le Fasi 0–4 **non modificano** la struttura
ThesisOS; la migrazione vera (Fase 5) parte solo dopo approvazione esplicita.

### Fase 0 — Import grezzo (immutabile)

- Copia **tutto** l'export in `_inbox/kimi-claw/`, senza rinominare né modificare.
- File grandi (PDF, immagini): se necessario configurare **Git LFS** prima del
  commit (vedi `04_KNOWLEDGE/README.md`).
- Output: copia di riferimento intatta + checksum (vedi Fase 1).

### Fase 1 — Inventario completo

Leggere l'intero export e produrre `_migration/inventory.md` con:

- struttura delle cartelle;
- elenco di tutti i file con formato e dimensione;
- `sha256` di ogni file (base della tracciabilità P2);
- breve descrizione del contenuto;
- duplicati rilevati;
- dipendenze tra file.

Comando di riferimento per i checksum (sola lettura, non modifica l'export):

```bash
cd knowledge/thesis-agent
find _inbox/kimi-claw -type f -exec sha256sum {} \; > _migration/checksums.sha256
```

### Fase 2 — Analisi semantica

Per ogni elemento, classificare (senza spostare nulla):
memoria permanente · prompt di sistema · istruzioni operative · conversazioni ·
documenti di ricerca · bibliografia · file di progetto · knowledge base ·
configurazioni · allegati.

### Fase 3 — Mappatura verso ThesisOS

Produrre `_migration/mapping.md` con la tabella origine→destinazione usando la
**tassonomia reale** della sezione 4. Indicare per ogni riga l'azione
(copia / merge / estrazione / conversione / indicizzazione) e le trasformazioni.

### Fase 4 — Piano di migrazione (gate di approvazione)

Prima di toccare qualunque cosa, elencare esplicitamente:

- file che verranno **copiati**;
- file che verranno **convertiti**;
- file che verranno **unificati** (merge);
- file che verranno **lasciati invariati**;
- eventuali **conflitti** e come risolverli.

→ **STOP. Si procede solo dopo approvazione dell'utente.**

### Fase 5 — Migrazione

Applicare il piano approvato. Ogni file derivato riceve la sua intestazione di
provenienza (sezione 5) e una riga nel manifest. L'export grezzo resta intatto.

### Fase 6 — Ricostruzione della memoria e validazione finale

L'obiettivo non è copiare file, ma **ricostruire l'intelligenza dell'agente** così
che riprenda esattamente dal punto in cui Kimi Claw si è fermato, usando però
l'architettura ThesisOS:

- memoria permanente, regole di scrittura, workflow, stile, convenzioni;
- stato del progetto e cronologia delle decisioni.

Concretamente: promuovere `01_SYSTEM` + `02_METHOD` + `05_MEMORY/Permanent.md` +
`03_PROJECT/Decisions.md` verso ThesisOS `memories`
(`editable` / `thesis` / `decision`) e il corpus `04_KNOWLEDGE/*` verso
`documents` (M3) + retrieval (M4); i capitoli verso M6.

Validazione finale: ogni artefatto master del `Thesis-State.md` risulta
materializzato/promosso, e ogni file derivato è risalibile alla sua origine via
manifest.

---

## 4. Tassonomia di mappatura (categoria → destinazione reale)

> Non creare cartelle generiche tipo `system/`, `sources/`, `config/`,
> `archive/`: romperebbero la struttura ThesisOS. Usare **sempre** le cartelle
> reali qui sotto.

| Categoria semantica | Destinazione ThesisOS | Azione tipica |
|---|---|---|
| Memoria permanente | `05_MEMORY/Permanent.md` | merge (con approvazione) |
| Identità / comportamento | `01_SYSTEM/` | cross-check / merge |
| Istruzioni operative / workflow | `02_METHOD/` | cross-check / merge |
| Prompt di sistema / config piattaforma Kimi | restano solo in `_inbox` | **non importare** ¹ |
| Conversazioni (transcript) | restano in `_inbox`; estrarre artefatti → `03_PROJECT/`, capitoli → `chapters/` | estrazione + indicizzazione |
| Artefatti congelati (THEORY MAP, OUTLINE, BIBLIOGRAPHY_MASTER) | `03_PROJECT/` | materializza |
| Documenti di ricerca (paper, libri) | `04_KNOWLEDGE/{Papers,Books,References}` | copia |
| Bibliografia | `04_KNOWLEDGE/Bibliography/` + `03_PROJECT/Bibliography.md` | copia + indicizza |
| Allegati / immagini / foto progetto | `04_KNOWLEDGE/{Images,STIGMATA}` | copia |

¹ Vedi `04_KNOWLEDGE/README.md` → "Cosa NON importare da Kimi". Prompt, system
prompt e config della piattaforma restano nella copia grezza (P1) ma non
diventano runtime: il comportamento è già descritto in `01_SYSTEM`–`02_METHOD`.

---

## 5. Tracciabilità (attuazione di P2)

**File markdown derivati** — front-matter di provenienza in testa al file:

```yaml
---
source: _inbox/kimi-claw/<percorso/originale>
source_sha256: <hash>
migrated_at: 2026-06-30
transform: extract        # copy | extract | merge | convert
migration_run: kimi-claw-2026-06
notes: <come è stato adattato>
---
```

**File binari** (PDF, immagini) — non possono avere front-matter: la riga nel
manifest è la fonte di verità, più (per la bibliografia) l'entry in
`03_PROJECT/Bibliography.md` con il path.

**Manifest centrale** — `_migration/MANIFEST.tsv`, una riga per artefatto:

```text
origin_path	sha256	bytes	type	destination	action	transform	date	notes
```

**Log** — `_migration/migration-log.md`: cronologia leggibile delle operazioni
per ogni `migration_run`.

---

## 6. Cosa NON fare

- Non modificare o rinominare nulla dentro `_inbox/kimi-claw/` (P1).
- Non creare cartelle fuori dalla tassonomia della sezione 4.
- Non reimportare prompt/system/config Kimi come runtime.
- Non saltare il gate di Fase 4: nessuna migrazione senza approvazione.
- Non committare file enormi senza valutare Git LFS.

---

## 7. Checklist rapida

- [ ] Fase 0: export copiato in `_inbox/kimi-claw/`, intatto
- [ ] Fase 1: `inventory.md` + `checksums.sha256` generati
- [ ] Fase 2: ogni file classificato semanticamente
- [ ] Fase 3: `mapping.md` con tassonomia reale
- [ ] Fase 4: piano di migrazione → **approvazione utente**
- [ ] Fase 5: migrazione applicata, manifest + provenienza compilati
- [ ] Fase 6: memoria ricostruita e validazione finale superata
