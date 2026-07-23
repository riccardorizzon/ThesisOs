# Multi-Thesis Workspace — STEP 2: Proposta architetturale

> Stato: **bozza per approvazione** · Data: 2026-07-23
> Prerequisito: `01-audit.md`. Coerente con ADR-0040 (INV-PS-5), ADR-0045
> (INV-COMP-6), ADR-0034 (INV-PV-4), ADR-0014, PX-6.3, Constitution C1–C8.

## 1. Principio

**Un solo ThesisOS, N workspace di tesi.** Non si duplica nulla: Research Engine,
Writing, Agents, Runtime, Knowledge, Event Bus, UI e API restano singoli. L'unica
variabile è il **progetto attivo** (`project_id`), che diventa la chiave di
partizione di *tutto* lo stato di prodotto — completando l'invariante INV-PS-5 già
ratificato e chiudendo il limite noto L-01 ("registry-scoped, not DB-partitioned").

```text
                 THESIS OS (unico)
                        |
                 Thesis Manager
      (projects table + resolver di scope per request)
                        |
     ┌──────────────────┼──────────────────┐
 thesis-agent        thesis-002         thesis-003
 (Default Thesis)     workspace          workspace
  docs·memoria·capitoli·bibliografia·embeddings·chat·config   (per ciascuna)
```

## 2. Identificatori (decisione da approvare)

| Richiesta originale | Proposta | Motivo |
|---|---|---|
| Default = `thesis-main` | **Mantenere l'id `thesis-agent`**, esposto in UI come "Tesi principale" (display name già oggi è il titolo reale) | `thesis-agent` è cablato in: default DB (`chapters`, `sources`), seeds Alembic 0006/0007/0009, ADR-0040/0045, file-SoR `knowledge/thesis-agent/`, programma di migrazione ASEP. Rinominarlo è un data-rename ad alto rischio e valore zero: la semantica ("tesi di default") è identica. Se il nome `thesis-main` è importante, si può aggiungere come **alias** nel registry senza toccare i dati. |
| Nuove tesi = `thesis-002`, `thesis-003`, … | **Adottata**: id sequenziali `thesis-NNN` generati dal registry (la tesi principale è concettualmente la 001) | Semplice, stabile, niente collisioni di slug. Il nome leggibile vive in `display_name` (rinominabile). |

`demo-thesis` resta invariato (sandbox demo, ADR-0045).

## 3. Componenti

### 3.1 Thesis Manager (Business layer, Product Plane)

1. **Tabella `projects`** (nuova, SoR dell'identità):
   `id VARCHAR(64) PK`, `display_name TEXT`, `kind VARCHAR(16)` (`owned|demo`),
   `status VARCHAR(16)` (`active|archived`), `settings JSONB DEFAULT '{}'`,
   `created_at`, `updated_at`. Seed idempotente: `thesis-agent` (owned, titolo
   reale) + `demo-thesis` (demo).
2. **`ProjectRegistryService` → DB-backed** (stessa interfaccia pubblica:
   `list/get/has/create`; si aggiunge `rename` e la sequenza `thesis-NNN`).
   API: `GET/POST /projects` invariati + `PATCH /projects/{id}` (rename).
3. **Resolver di scope unico** (`resolve_project_id(explicit) -> str`):
   `esplicito > default (thesis-agent)`, con validazione sul registry. Tutti i
   servizi lo usano; si eliminano i default string duplicati.

### 3.2 Partizione dati (schema)

Colonna `project_id VARCHAR(64) NOT NULL` (dopo backfill) + indice su:

| Tabella | Backfill | Nota |
|---|---|---|
| `documents` | `thesis-agent` | chunks/embeddings/versions ereditano via FK/owner |
| `memories` | `thesis-agent` | memory_versions eredita |
| `conversations` | dal JSON `agent_runs.input.project_id` se presente, altrimenti `thesis-agent` | sostituisce l'hack "scope AgentRun" |
| `notes` | `thesis-agent` | oggi 0 righe |
| `tasks` | `thesis-agent` | |
| `agent_runs` | da `input.project_id` se presente, altrimenti `thesis-agent` | colonna reale, il JSON resta per compat |
| `events` | `thesis-agent` | vedi §3.6 |

Niente FK rigida verso `projects` nella prima iterazione (i literal storici come
`cur-11-review-isolation` verrebbero rifiutati); la validazione avviene nel
resolver. FK opzionale in un secondo momento, dopo la pulizia dei dati.

Allineamenti contract: `contracts/db/schema.sql` (aggiunge anche il project_id di
`sources` oggi mancante), ORM `db/models.py` (idem `Source`), `contracts/openapi/openapi.yaml`.

### 3.3 Domini applicativi

| Dominio | Cambiamento |
|---|---|
| **Documents/Upload** | `POST /documents/upload`, list, get: param `project_id` opzionale (default thesis-agent). L'upload registra la source nel progetto attivo, non più sempre in thesis-agent |
| **Retrieval/RAG** | `retrieval/service.py`: filtro `documents.project_id = :pid` (join su chunks/embeddings). Vale per `/search`, RAG chat (`graph/retriever.py`), writing panel |
| **Memory** | `MemoryService` accetta `project_id`; `/memory` API con param opzionale; chiavi companion scoped per progetto |
| **Conversations/Chat** | colonna `conversations.project_id`; il binding LangGraph resta via `configurable` (ADR-0014: GraphState pulito) |
| **Chapters** | già scoped su list/create; si aggiunge ownership check su get/patch/delete/export; `copy_demo_structure(project_id)` esplicito |
| **Export/Citations** | filtro per progetto via chapters/sources già scoped |
| **Companion** | Invariato per `thesis-agent` (file-SoR `knowledge/thesis-agent/`, INV-COMP-6). Per le altre tesi: companion **DB-only** — resume packet generico (già esiste), memoria/workspace context letti dalle tabelle scoped. Niente file-SoR per le nuove tesi in v1 (estensione futura: `knowledge/<project-id>/`) |
| **Knowledge** | fix del fallback al catalogo globale: un progetto vuoto non deve "vedere" i concetti STIGMATA di thesis-agent |
| **Events** | campo `project_id` **additivo** nel payload/envelope (C5-compatibile); colonna su `events` per query |
| **Conformance API** | usare davvero il path param invece di `del project_id` |

### 3.4 Frontend

1. **Un solo punto di iniezione dello scope**: wrapper fetch in `lib/api.ts` (o
   helper `withProject(url)`) che aggiunge il progetto attivo a ogni client; si
   eliminano i default `"thesis-agent"` sparsi nei client. `knowledgeClient` e le
   pagine SSR (`knowledge`, `research`, `research/canvas`) leggono cookie/active id.
2. **Storage namespaced**: chiavi `thesisos:{projectId}:…` per session-state,
   prefs, proposals, recent/linked sources, canvas views/basket, outline order.
   Migrazione una-tantum: le chiavi legacy diventano il namespace di `thesis-agent`.
3. **Switch**: si mantiene il full reload (semplice e affidabile); gli store
   zustand restano quindi sicuri. `ShellRouter`: rimuovere il pinning forzato di
   chat su `thesis-agent` — la chat segue il progetto attivo; il solo caso demo
   mantiene il comportamento attuale (demo non è la tesi dell'utente).
4. **UX**: ProjectSwitcher mostra tutte le tesi (owned) + demo; "Nuova tesi" chiede
   il nome (PATCH display_name); Settings salva il rename sul registry (non più solo
   in localStorage).

### 3.5 Regole di compatibilità (invarianti del progetto)

1. Nessuna richiesta esistente cambia comportamento: param assente ⇒
   `thesis-agent`.
2. Nessuna route rimossa o rinominata; nessun campo obbligatorio nuovo nelle API.
3. `knowledge/thesis-agent/` e il flusso companion della tesi principale intatti.
4. Eventi: solo campi additivi.
5. Ogni migrazione DB è reversibile (downgrade implementato e testato).
6. Test di isolamento: per ogni dominio, "il progetto B non vede i dati del
   progetto A" diventa un test automatico permanente.

### 3.6 Governance

- **Nuovo ADR** (n. successivo disponibile, es. ADR-0047 "Multi-Thesis Workspace —
  Thesis Manager e partizione per project_id"): registra tabella `projects`,
  colonne di scope, campo evento additivo, id sequenziali. Nessun articolo C1–C8
  cambia ⇒ niente bump della Runtime Constitution. Non è multi-tenant/collab ⇒
  niente bump della Product Constitution.
- Esecuzione come **completamento PX-6.3** dentro il programma
  `thesisos-product-v2.yaml` (oggi `blocked` → da sbloccare con questo piano).
- Ogni PR dichiara `Layer: Business` (salvo il commit eventi: Runtime) e segue la
  review order C7.
