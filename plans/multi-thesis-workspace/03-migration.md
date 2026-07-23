# Multi-Thesis Workspace — STEP 3: Piano di migrazione della tesi attuale

> Stato: **bozza per approvazione** · Data: 2026-07-23
> Obiettivo: la tesi attuale (`thesis-agent`, 34 capitoli, 61 documenti, 13 memorie,
> 131 conversazioni, 2 208 embeddings) diventa la **Default Thesis** del nuovo
> sistema **senza alcuna interruzione o perdita**, e senza che l'utente percepisca
> differenze.

## 1. Principi

1. **Additivo, mai distruttivo**: ogni migrazione aggiunge colonne/tabelle; nessun
   dato viene spostato tra tabelle, nessun file toccato in `knowledge/thesis-agent/`.
2. **Backfill = attribuzione, non copia**: i dati esistenti vengono *etichettati*
   come `thesis-agent` (sono già i suoi).
3. **Tre fasi per colonna**: (a) add nullable → (b) backfill → (c) `NOT NULL` +
   indice. Ogni fase con `downgrade()` implementato.
4. **Gate di verifica dopo ogni migrazione** (query di conteggio, `make ci`,
   smoke test UI).
5. **Rollback**: `alembic downgrade -1` + redeploy immagine precedente; nessuna
   migrazione cancella dati, quindi il rollback è sempre sicuro.

## 2. Sequenza delle migrazioni Alembic

> Numerazione indicativa (successiva all'attuale head).

### M-A `projects` table + seed

```sql
CREATE TABLE projects (
  id VARCHAR(64) PRIMARY KEY,
  display_name TEXT NOT NULL,
  kind VARCHAR(16) NOT NULL DEFAULT 'owned',
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO projects (id, display_name, kind) VALUES
  ('thesis-agent', 'Prima dei dieci minuti. Il processo creativo nel fashion design', 'owned'),
  ('demo-thesis',  'Progetto dimostrativo', 'demo')
ON CONFLICT (id) DO NOTHING;
```

Verifica: `SELECT count(*) FROM projects;` = 2. Downgrade: `DROP TABLE projects`.
Da qui il registry legge/scrive su DB (fallback in-memory eliminato nello stesso
commit — il comportamento API resta identico).

### M-B `documents.project_id`

```sql
ALTER TABLE documents ADD COLUMN project_id VARCHAR(64);
UPDATE documents SET project_id = 'thesis-agent' WHERE project_id IS NULL;
ALTER TABLE documents ALTER COLUMN project_id SET NOT NULL,
                      ALTER COLUMN project_id SET DEFAULT 'thesis-agent';
CREATE INDEX idx_documents_project ON documents (project_id);
```

Verifica: `count(*) FROM documents WHERE project_id='thesis-agent'` = 61 (valore
attuale; ricontrollare al momento dell'esecuzione). Chunks/embeddings non si
toccano: ereditano via `document_id` / `owner_id`.

### M-C `memories.project_id`

Stesso pattern (13 righe → `thesis-agent`). `memory_versions` eredita via FK.

### M-D `conversations.project_id`

```sql
ALTER TABLE conversations ADD COLUMN project_id VARCHAR(64);
UPDATE conversations c SET project_id = COALESCE(
  (SELECT ar.input->>'project_id' FROM agent_runs ar
    WHERE ar.conversation_id = c.id AND ar.trigger = 'scope'
      AND ar.input ? 'project_id'
    ORDER BY ar.created_at DESC LIMIT 1),
  'thesis-agent');
-- poi NOT NULL + default + indice
```

Le conversazioni già "demo" mantengono così il loro scope reale. Il vecchio
meccanismo scope-AgentRun resta leggibile ma non più necessario.

### M-E `tasks`, `notes`, `agent_runs`, `events` + colonna evento

Stesso pattern additivo (backfill `thesis-agent`; per `agent_runs` si usa
`input->>'project_id'` quando presente). Campo `project_id` additivo nel payload
degli eventi *nuovi*; gli eventi storici restano com'erano (sono log).

### M-F Allineamento contract/ORM (nessun cambiamento dati)

- `db/models.py`: aggiungere `project_id` a `Source` (già nel DB), `Document`,
  `Memory`, `Conversation`, ecc. — l'ORM raggiunge lo schema reale.
- `contracts/db/schema.sql`: rigenerare con `pg_dump --schema-only` (procedura M0
  già documentata) così il drift di `sources` si chiude.
- `contracts/openapi/openapi.yaml`: aggiungere i nuovi param opzionali e
  `PATCH /projects/{id}`.

### M-G Pulizia dati anomali (richiede conferma esplicita)

Un capitolo ha `project_id='cur-11-review-isolation'` (residuo di test di
isolamento). Opzioni: (a) riassegnarlo a `demo-thesis`, (b) eliminarlo.
**Proposta: (b) eliminarlo**, previa conferma dell'owner al momento
dell'esecuzione. Fino ad allora resta dov'è (non è visibile in nessuna tesi).

## 3. Migrazione del comportamento (senza dati)

| Passo | Cosa cambia | Compat |
|---|---|---|
| B-1 | Resolver unico `resolve_project_id` sostituisce i default sparsi | Output identico per richieste senza param |
| B-2 | Upload → progetto attivo | Se il param manca ⇒ thesis-agent (identico a oggi) |
| B-3 | Retrieval con filtro project | Default thesis-agent ⇒ stesso corpus di oggi; test di parità RAG (stesse query, stessi top-k id) prima/dopo |
| B-4 | Ownership check su endpoint per id | 404 solo per accessi cross-project espliciti — comportamento oggi impossibile da innescare dalla UI |
| B-5 | Frontend: wrapper + namespacing storage con migrazione chiavi legacy → namespace `thesis-agent` | Sessione/preferenze correnti conservate |

## 4. Verifica end-to-end (gate finale della migrazione)

1. `make ci` verde.
2. Parità tesi principale: Home resume card, Writing (34 capitoli), Sources (5),
   Knowledge (7 concetti), chat con memoria companion — identici a prima
   (smoke test + screenshot).
3. Isolamento: creare `thesis-002` di prova → deve vedere 0 documenti, 0 memorie,
   0 capitoli, 0 conversazioni, ricerca vuota; caricare 1 PDF in `thesis-002` →
   non appare in `thesis-agent`. Poi eliminare la tesi di prova.
4. Demo: `demo-thesis` invariato (9 capitoli).
5. Riavvio backend → le tesi create sopravvivono (registry su DB).

## 5. Cosa NON viene migrato (esplicitamente fuori scope)

- Nessun rename di `thesis-agent` → l'id resta; "Default Thesis" è la semantica.
- Nessuno spostamento del file-SoR `knowledge/thesis-agent/`.
- Nessun cambio al checkpointer LangGraph (thread ⊂ conversation ⊂ project è
  garantito dalla colonna su conversations).
- Niente multi-utente/collaborazione (fuori scope per ADR-0034; non richiesto).
