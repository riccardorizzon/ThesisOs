# Piano pulizia dati — Wave 1 (thesis-agent)

> **Obiettivo:** workspace presentabile in demo — corpus leggibile, capitoli senza rumore E2E, conversazioni non confuse.  
> **Principio:** RAG legge **chunk/embeddings in Postgres**; cancellare un documento rimuove chunk collegati. I 6 core vanno **protetti**.  
> **Esecuzione:** `bash bin/demo-cleanup.sh --dry-run` poi `--apply`. Backup consigliato prima di `--apply`.

## Stato attuale (baseline 2026-07-29)

| Entità | Totale | Note |
|--------|--------|------|
| Documenti | 66 | 40 indexed, 26 parsed, 0 failed |
| Capitoli | 34 | ~22 tesi kimi-claw con contenuto, ~8 rumore |
| Conversazioni | ~156 | 56× `__companion_open__`, vari `ping`/`test` |
| Sources (catalogo) | 11 | 6 collegati ai core seeded |

---

## Documenti

### TENERE (15 dopo cleanup)

#### A. Core seeded — **non cancellare mai**

| ID | Titolo | Sources link |
|----|--------|--------------|
| `1b606520-2923-482e-9d04-c123b686dacf` | Outline-Master | sì |
| `54daa0e8-2922-4692-b750-9580daa885bd` | Stigmata-Framework | sì |
| `9b35561b-0cf5-4ca3-83db-bc96262c4118` | Core-Theory-Map | sì |
| `d9f074b6-79e5-4403-a6e6-7748d22b8556` | Sennett_The-Craftsman | sì |
| `56e7fbe5-34eb-4d2e-b0cc-e220a5f515cf` | Benjamin_Opera-Arte-Riproducibilita | sì |
| `e1114893-0a04-40c7-a15a-15d72ad8eb64` | Guida-Redazione-Tesi | sì |

#### B. Corpus secondario kimi — **tenere** (contenuto unico, non duplicato dai core)

| ID | Titolo | Chunks |
|----|--------|--------|
| `fcb97bcc-e3e4-4e34-92c7-a29f50159b77` | Csikszentmihalyi Flow | 481 |
| `9e7eec1a-1187-48d4-8544-2b5980e62d1e` | Hollander Sex-and-Suits | 275 |
| `aa23bef3-32f4-4723-acf0-7cf3cc09ee93` | Barthes Mythologies | 196 |
| `0151175a-2a61-4095-b9c5-a86152151ed0` | Albers Interaction-of-Color | 84 |
| `1834a737-bf25-4cae-a400-b6bede6c8700` | Seivewright Basics-Fashion-Research | 64 |
| `95f2e49a-1384-4457-b57f-7e9348e23161` | Bibliography-Master | 26 |
| `1b3d08ec-fa6d-494b-a034-8aef8ac0e98f` | Lobach Disegno-Industriale | 17 |
| `92bc3231-2729-4e41-8dd4-826179d8d38b` | Tesi-bibliografia-completa | 16 |
| `13788fcb-385f-409c-b2aa-d53236932a5e` | Prima revisione relatrice | 9 |

### CANCELLARE — duplicati kimi (superseded dai 6 core)

| ID | Motivo |
|----|--------|
| `0634efb5-700a-4483-b034-b3ed945efbfe` | Duplicato Outline-Master |
| `e7540d4e-b54e-4217-9d53-92cfba4b3f97` | Duplicato Stigmata-Framework |
| `8181860d-92ee-458e-b07f-d3af3743281f` | Duplicato Core-Theory-Map |
| `7f272196-516e-4060-9cf1-372444918599` | Duplicato Sennett |
| `84ce8dc7-c774-48b7-8935-e6e7d1d4b37c` | Duplicato Benjamin |
| `a67ae3a2-7e24-4b84-a1b9-9f69cb03712c` | Duplicato Guida |

### CANCELLARE — duplicati Sennett / dogfood

| ID | Motivo |
|----|--------|
| `dea2ebee-edcd-4ab6-9324-7c1e9a453c4e` | Dogfood M4 excerpt |
| `1d2c6829-5077-4e8d-8a51-6601e92ef94e` | Dogfood M4 excerpt |
| `8246a26d-f148-4594-9f13-8e2edb968e19` | Dogfood M4 excerpt |
| `51f8adac-5798-489d-97a3-7fedab053532` | Craftsman small |
| `c31abf2c-a069-4919-b7fb-5eeb6cbebc19` | The Craftsman full markdown (dup) |
| `6013bd6f-9985-4be4-b0d4-28d969f78c43` | PDF Prologue+Ch1 (dup; tenere seeded MD) |

### CANCELLARE — rumore test (37 righe)

Pattern: titoli `a`, `f`, `emb`, `round`, `persist`, `secret`, `docling_*`, `Dogfood M*`, `P3/P4`, `phase2_test`, upload E2E.

Elenco completo in `bin/demo-cleanup.sh` (`NOISE_DOC_IDS`).

### CANCELLARE — kimi pagine vuote / bozze micro

| ID | Titolo |
|----|--------|
| `b85b16cc-2845-4598-99e0-83b95e662e8a` | bozza-1.1-processo-creativo (3 chunks) |
| `07280808-82ee-49e6-b504-af8ad151fdc8` | page 1 |
| `e3b0b795-413d-4278-a044-31cb0ae8f4ca` | page 2 |
| `996b331f-77da-4f0a-bd7e-eefbaae41179` | page 3 |
| `de9df660-3e80-4216-b9ec-4e6aedd2a155` | page 4 |

**Totale delete documenti:** ~51 → **~15 restanti**

---

## Capitoli

### TENERE (~25)

- Tutti i capitoli `[kimi-claw-2026-06]` con **word_count > 100** (Cap. 1–3, §1.x, §2.x).
- **Vetrina demo:** `503c33f5-a3d8-40ee-adc0-3ff067747a17` (Cap. 3, ~3662 parole, `review`).

### CANCELLARE (9) — rumore E2E/G5

| ID | Titolo | word_count |
|----|--------|------------|
| `c97085ac-5f2f-469f-9daf-4ec97879e4d6` | Craftsmanship (stub vuoto) | 0 |
| `def76b59-bd21-4ad5-9df8-469f34c1d76d` | E2E export | 4 |
| `2ad647f2-0c97-4dee-88f0-aff1b6271b34` | E2E export | 4 |
| `3824aa41-1390-474d-8481-3a6d443398cb` | E2E export | 4 |
| `fe64f0f6-7a26-4cad-b025-e25577a48940` | G5 test | 3 |
| `c5c2639b-2ab7-4dc7-8941-ffe521f82aca` | G5 walkthrough | 4 |
| `a696a545-4f6b-4b75-b955-e87d230a9e15` | G5 walkthrough | 4 |
| `30c6bc7f-bf9e-41b3-9faa-711d519d0c9c` | G5 walkthrough | 4 |
| `0f11b036-a74e-409a-b143-909c317d0acf` | G5 walkthrough | 4 |

### CANCELLARE (10) — stub vuoti duplicati (stesso titolo delle righe `review`)

| ID | Titolo |
|----|--------|
| `e8793790-88ef-4841-9495-369b9450f280` | Cap. 3 stub (aprire `503c33f5…` per demo) |
| `bfb9c3e4…` … `e2772c4e…` | §1.1–§2.4 stub vuoti |
| `fe01b674…` | Introduzione reti neurali sparse |
| `273017a7…` | prova |

**Nota:** capitoli `demo-thesis` (seed demo) non sono cancellabili via API — non toccare quel project.

### NASCONDERE (Wave 2 — completato)

- Prefisso `[kimi-claw-…]` rimosso dai titoli via `bin/demo-wave2.sh --apply`.
- README allineato con route `/manuscript` (Manoscritto).
- Limitazioni beta in **Settings → Beta — limitazioni note**.

---

## Conversazioni

### NASCONDERE in demo (non aprire)

| Pattern | Count | Azione demo |
|---------|-------|-------------|
| `__companion_open__` | ~56 | Ignorare; creare thread «Demo — …» |
| `ping`, `ops ping`, `test` | ~15 | Non mostrare |
| `G5/G6 walkthrough`, `M7 dogfood` | ~6 | Non mostrare |

### CANCELLARE (opzionale — flag `--conversations`)

Criteri SQL (script):

```sql
title IN ('ping', 'ops ping', 'test', 'ciao')
OR title ILIKE '%walkthrough%'
OR title ILIKE '%dogfood%'
OR title ILIKE 'rispondi soltanto%'
```

**Non cancellare** conversazioni con domande sostanziali (STIGMATA, Sennett, Cap. 4, autori corpus).

**Totale delete conversazioni stimato:** ~20–30 (non le 56 companion — quelle restano finché non c’è filtro UI).

---

## Sources (bibliografia)

### TENERE tutte e 11

- 6 voci linkate ai core seeded — **protette** indirettamente (non cancellare doc collegati).
- 5 voci catalogo collegate ai doc kimi via `bin/demo-cleanup.sh --apply` (link automatico):

| Source | Document |
|--------|----------|
| Flow | Csikszentmihalyi Flow |
| Sex and Suits | Hollander |
| Mythologies | Barthes |
| Interaction of Color | Albers |
| L'opera d'arte… (Benjamin IT) | Benjamin_Opera-Arte-Riproducibilita |

### Nessuna delete sources in Wave 1

---

## Ordine di esecuzione

```bash
# 1. Backup
docker compose exec -T db pg_dump -U thesisos thesisos > /tmp/thesisos-pre-wave1.sql

# 2. Preview
bash bin/demo-cleanup.sh --dry-run

# 3. Apply (documenti + capitoli)
bash bin/demo-cleanup.sh --apply

# 4. Opzionale: conversazioni rumore
bash bin/demo-cleanup.sh --apply --conversations

# 5. Verifica
make ops-check
bash bin/audit-document-storage.sh
docker compose exec -T db psql -U thesisos -d thesisos -c \
  "SELECT status, COUNT(*) FROM documents GROUP BY 1;"
```

## Rischi e mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| Perdita chunk RAG utili | Dry-run + lista KEEP esplicita; backup pg_dump |
| Source orphan | Non cancellare i 6 core; script verifica `sources.document_id` |
| Capitolo non cancellabile | Solo `thesis-agent`; `demo-thesis` protetto da backend |
| Demo senza Sennett | Tenere `d9f074b6…` seeded, mai i duplicati |

## Esito atteso post-Wave 1

| Entità | Prima | Dopo |
|--------|-------|------|
| Documenti | 66 | ~15 |
| Capitoli | 34 | ~15 (25 − 9 E2E/G5 − 10 stub vuoti) |
| Conversazioni | ~160 | ~130 (con `--conversations`) |
| Sources linkati | 6/11 | 11/11 |
| Failed docs | 0 | 0 |
| Titoli capitolo duplicati | 8 coppie | 0 |

Wave 2 (completata): rename capitoli vetrina, README Manoscritto, bullet limitazioni in Settings UI.

```bash
bash bin/demo-wave2.sh --dry-run
bash bin/demo-wave2.sh --apply
make demo-wave2-check    # gate: titoli puliti, export, sources 11/11
make demo-gate           # gate completo pre-demo
```

## Checklist chiusura Wave 2

| Item | Gate | Stato |
|------|------|-------|
| Capitoli senza prefisso `[kimi-claw-…]` | `make demo-wave2-check` | 14 capitoli, 0 duplicati |
| Cap. 3 vetrina (≥3000 parole) | `make demo-wave2-check` | `503c33f5…` in `review` |
| Export markdown Cap. 3 | `make demo-wave2-check` | HTTP 200 + 422 senza `project_id` |
| Limitazioni beta in UI | Settings → *Beta — limitazioni note* | 4 bullet umani |
| Menu / docs allineati | README + getting-started + RC onboarding | `/manuscript` elencato |
| Coach marks / empty state | Vitest `CoachMark`, `HomeView`, `EmptyStatePanel` | codice + test verdi |
