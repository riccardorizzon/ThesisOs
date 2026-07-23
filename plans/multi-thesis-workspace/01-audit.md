# Multi-Thesis Workspace — STEP 1: Audit completo

> Stato: **bozza per approvazione** · Data: 2026-07-23
> Fonti: ispezione diretta del DB live (`agentthesis-db-1`), lettura del codice, audit
> paralleli su backend, frontend e governance.
> Nessuna modifica al codice è stata effettuata.

## 0. Verdetto in una frase

ThesisOS ha **già un layer multi-progetto parziale** (PX-6.3): registry, switcher,
`project_id` su 4 tabelle. Ma **documenti, memoria, conversazioni, embeddings,
retrieval/RAG, eventi e gran parte dello stato browser sono ancora un pool unico
condiviso**, e il registry dei progetti è in-memory (si svuota a ogni riavvio).
La tesi attuale è il progetto `thesis-agent` ("Prima dei dieci minuti. Il processo
creativo nel fashion design").

## 1. Stato del database (verificato sul DB live)

Tabelle: 23. Con `project_id`: **4**.

| Tabella | project_id | Default | Note |
|---|---|---|---|
| `chapters` | SI | `'thesis-agent'` | 34 righe thesis-agent, 9 demo-thesis, 1 `cur-11-review-isolation` (residuo di test) |
| `sources` | SI | `'thesis-agent'` | 5 righe (solo thesis-agent). **Drift:** colonna presente solo via migrazione Alembic 0007 — manca nell'ORM `db/models.py` e in `contracts/db/schema.sql` |
| `concepts` | SI | — | 7 righe thesis-agent; unique `(project_id, slug)` (INV-KM-2) |
| `proposals` | SI | — | indice `(project_id, chapter_id)` |

**Senza** `project_id` (aggregati radice → pool condivisi tra tutte le tesi):

| Tabella | Righe oggi | Impatto |
|---|---|---|
| `documents` | 61 | Ogni tesi vede tutti i documenti |
| `memories` | 13 | Memoria unica condivisa (+ `memory_versions`) |
| `conversations` / `messages` | 131 / 418 | Scoping solo "soft" via `agent_runs.input.project_id` (JSON, hack) |
| `embeddings` (+ partizione `embeddings_part_text_multilingual_embedding_002`) | 2 208 | Retrieval/RAG cross-tesi |
| `events` | 2 321 | Outbox senza scope |
| `agent_runs` / `agent_steps` | 316 | Solo JSON input |
| `tasks` | 105 | Nessuno scope |
| `notes`, `citations` | 0 / n | Scope indiretto via FK a document/chapter/source |

Tabelle figlie (`chunks`, `document_versions`, `chapter_versions`, `memory_versions`,
`messages`, `agent_steps`, `concept_*`) ereditano lo scope via FK dal padre: **non**
serve aggiungere colonne lì, basta scopare gli aggregati radice.

**Non esiste una tabella `projects`**: l'identità dei progetti vive solo in
`backend/app/services/project_registry.py` (lista Python in-memory, righe 37–52).
`POST /projects` appende alla lista → **le tesi create si perdono al riavvio del
backend**.

## 2. Risoluzione del progetto nel backend

Nessun header (`X-Project-Id` non esiste). Meccanismi attuali:

| Meccanismo | Dove |
|---|---|
| Path `/projects/{project_id}/…` | context, sources, knowledge, companion resume, conformance |
| Query `?project_id=` | chapters list, conversations list, proposals list |
| Body JSON `project_id` | chat, create conversation/chapter/proposal |
| LangGraph `configurable.project_id` | `services/conversation/service.py:290–295` |
| **Default hardcoded** `"thesis-agent"` | `schemas/context.py:8`, `db/models.py:127`, `schemas/chapter.py:23,52`, `services/chapter/service.py:224,441`, `services/sources/repository.py:45,55`, `services/knowledge/service.py:38` |

### Router: chi è project-aware e chi no

| Router | Project-aware | Note |
|---|---|---|
| `api/projects.py`, `api/project_registry.py` | SI | registry in-memory |
| `api/sources.py`, `api/knowledge.py` | SI (path) | knowledge ha fallback a catalogo globale |
| `api/chapters.py` | Parziale | list/create sì; **get/patch/delete per id senza check di ownership** |
| `api/conversations.py`, `api/chat.py` | Parziale | list/create sì; messages per id no |
| `api/proposals.py` | SI (list/create) | accept/reject per id |
| `api/documents.py` | **NO** | upload/list/get globali |
| `api/memory.py` | **NO** | memoria globale |
| `api/search.py` | **NO** | ricerca su tutto il corpus |
| `api/writing_actions.py` | **NO** | retrieval globale nel panel di scrittura |
| `api/export.py`, `api/citations.py`, `api/jobs.py` | **NO** | |
| `api/conformance.py` | Finto | `del project_id` — il path viene ignorato (righe 15,23,31) |

### Retrieval / RAG (criticità principale)

- `services/retrieval/service.py:270–312` — ricerca ibrida pgvector **senza filtro
  project**; filtra solo per `document_ids` / `source_types`.
- `graph/retriever.py:50–53` — il RAG della chat recupera dal corpus globale.
- `services/writing/panel.py:67` — panel di scrittura: ricerca globale.
- Upload: `document/service.py:245–251` registra sempre la source sotto
  `thesis-agent`.

### Companion / memoria: hardcoded sulla tesi principale

- `api/projects.py:75` — resume companion: pacchetto pieno **solo** per
  `thesis-agent`, vuoto per gli altri.
- `graph/memory_context.py:26–28`, `graph/workspace_context.py:66–68`,
  `graph/conversation.py:111` — iniezione memoria/workspace/enforcement **solo** per
  il progetto primario.
- `services/workspace/thesis_sor.py:17,26` — SoR su file:
  `knowledge/thesis-agent/` (override env `THESIS_AGENT_KNOWLEDGE_ROOT`).
- `services/workspace/snapshot.py:79` — snapshot legge i capitoli **senza filtro
  project** (`ChapterListFilters()` vuoto).
- `services/chapter/service.py:266–294` — `copy_demo_structure` scandisce tutti i
  capitoli e crea righe col default `thesis-agent`.
- MemoryService: nessun parametro project; chiavi di memoria globali
  (`thesis_memory_sync.py`).

### Event bus / runtime

- `contracts/events/events.json` — nessun payload contiene `project_id`.
- `runtime/events.py:54–66` — envelope `RuntimeEvent` senza campo project.
- Checkpoints LangGraph: keyed per `thread_id` (= conversation), nessuna partizione
  per progetto (accettabile se conversazione ⊂ progetto è garantito a livello DB).

## 3. Frontend

### Stato attivo

- Attivo: `localStorage["thesisos:active-project-id"]` + cookie
  `thesisos-active-project-id` per SSR (`lib/projectPrefs.ts:17–25`).
- Default: `"thesis-agent"` duplicato in più punti (`projectContext.ts:9`,
  `projectPrefs.ts:18–19`, `conversationClient.ts:3`, `sourcesClient.ts:7`,
  `knowledgeClient.ts:15`).
- Switch: `ProjectSwitcher.tsx:45–50` → `setActiveProjectId` + `window.location.reload()`.
- Welcome: "Nuova tesi" crea progetto via `POST /projects` e lo attiva; "Esplora
  demo" forza `demo-thesis`.
- **Conflitto chat**: `ShellRouter.tsx:17–18,33–40` su `/` e `/ai` forza
  `thesis-agent` se il progetto attivo è demo → con più tesi questo pinning è rotto.

### Client API

| Client | Project-aware | Problema |
|---|---|---|
| `sourcesClient`, `conversationClient`, `contextClient`+`contextLoadClient`, `companionClient`, `proposalClient` | SI | — |
| `chapterClient` | Parziale | get/update/delete/export/copy-demo senza project |
| `knowledgeClient` | Rotto | path-capable ma default hardcoded, **non legge l'id attivo** (`knowledgeClient.ts:15,24,…`); le pagine SSR `knowledge/page.tsx:17`, `research/page.tsx:11`, `research/canvas/page.tsx:13–18` caricano sempre thesis-agent |
| `documentClient`, `memoryClient` | **NO** | API backend non scoped |
| `corpusClient.searchRemote` | **NO** | `POST /search` senza project (`corpusClient.ts:188–192`) |

### Persistenza browser non scoped (leak su switch)

Chiavi globali non namespaced per progetto: `thesisos:session-state`,
`thesisos:project-prefs` (un solo blob per tutte le tesi), `thesisos:proposals`,
`thesisos:recent-sources`, `thesisos:chapter-linked-sources`,
`thesisos:canvas-saved-views`, `thesisos:canvas-last-view-id`,
`thesisos:canvas-basket` (sessionStorage), `thesisos:outline-order`.
Store zustand (`store.ts`, `documentStore.ts`, `memoryStore.ts`) globali — oggi
salvati solo dal full reload dello switcher.

## 4. Governance: cosa è già deciso

- **ADR-0040 INV-PS-5**: "`project_id` scopes all product state from PX-1 onward" —
  il multi-thesis è *completamento* di un invariante già ratificato, non una nuova
  visione.
- **ADR-0045 INV-COMP-6**: isolamento companion/context/retrieval/memoria tra
  progetti; `project_id` propagato via HTTP → conversazioni → LangGraph config.
- **ADR-0034 INV-PV-4**: la tesi è il *primo template*, niente hardcoding della tesi
  fashion nel chrome.
- **PX-6.3** (`docs/product/specs/px6-polish-experience-v1.md` §7): multi-project
  switch = piano prodotto esistente; programma `.asep/programs/thesisos-product-v2.yaml`
  con PX-6 `status: blocked`.
- **RC-BUNDLE L-01** (limite noto accettato per RC): "isolation is registry-scoped,
  not DB-partitioned" — questo task chiude L-01.
- **ADR-0014**: lo scope va in RunContext/config, **non** in GraphState.
- **Constitution C1–C8**: scoping = layer Business; contratti (OpenAPI, schema.sql,
  events.json) sono superfici C5 → modifiche additive + ADR; C6 vieta di rompere i
  milestone qualificati su thesis-agent; review order C7.
- Trigger "Product Constitution bump" solo se si sconfina in multi-tenant/collab
  multi-utente (non è questo caso: single-user, più tesi).

## 5. Risposte alle 8 domande del task

1. **Dove è hardcoded la tesi attuale** → §2 (default backend), §3 (default frontend),
   più seeds Alembic 0006/0007/0009 e file-SoR `knowledge/thesis-agent/`.
2. **Componenti che assumono una sola tesi** → documents/memory/search/export/
   writing_actions API; retrieval service; snapshot workspace; MemoryService;
   companion graph nodes; registry in-memory; ShellRouter chat pinning; storage
   browser non namespaced.
3. **Servizi da rendere thesis-aware** → DocumentService, MemoryService,
   RetrievalService, writing panel, ExportService, ChapterService (mutazioni per id),
   ConversationService (colonna vera), EventPublisher, ProjectRegistry (persistente).
4. **Modifiche DB** → tabella `projects`; `project_id` su `documents`, `memories`,
   `conversations`, `notes`, `tasks`, `agent_runs`, `events` (additive + backfill
   `thesis-agent`); indici; allineamento ORM/contract per `sources`.
5. **Modifiche API** → param `project_id` (opzionale, default thesis-agent) su
   documents/memory/search/writing-actions/export; ownership check su endpoint per
   id; `PATCH /projects/{id}` per rename; conformance: usare davvero il path param.
6. **Modifiche frontend** → wrapper fetch unico che inietta il progetto attivo; fix
   `knowledgeClient` + pagine SSR; namespacing storage per progetto; reset store su
   switch; fix ShellRouter; prefs per-progetto; UI rename.
7. **Memoria e retrieval** → colonna su `memories`; filtro project su ricerca
   ibrida (join `documents.project_id`); chiavi memoria companion scoped; RAG chat e
   writing panel filtrati.
8. **Rischi di regressione** → vedi §6.

## 6. Registro dei rischi

| # | Rischio | Mitigazione |
|---|---|---|
| R1 | Backfill errato → documenti/memorie della tesi principale "spariscono" | Migrazioni additive: prima colonna nullable, backfill `thesis-agent`, poi NOT NULL; verifica count prima/dopo; downgrade testato |
| R2 | Retrieval filtrato per progetto degrada le risposte della tesi attuale | Default = thesis-agent ⇒ stesso corpus di oggi; test di parità sul RAG prima/dopo |
| R3 | Rottura API per client esistenti | Tutti i nuovi param opzionali con default thesis-agent; nessuna route rimossa |
| R4 | Companion (fase delicata: file-SoR) | Non toccare `knowledge/thesis-agent/`; altri progetti restano DB-only |
| R5 | Registry DB rompe la welcome/demo | Seed idempotente di `thesis-agent` + `demo-thesis` nella stessa migrazione |
| R6 | Leak di stato browser tra tesi | Namespacing chiavi + migrazione una-tantum delle chiavi esistenti al namespace thesis-agent |
| R7 | Milestone OR/dogfood qualificati (C6) | Gate `make ci` + test isolamento per ogni commit; nessun comportamento default modificato |
| R8 | Riga chapters `cur-11-review-isolation` orfana | Decisione esplicita in migrazione (spostare a demo-thesis o eliminare) — richiede conferma owner |
