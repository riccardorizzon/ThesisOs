# Multi-Thesis Workspace — STEP 4: Roadmap a piccoli commit

> Stato: **bozza per approvazione** · Data: 2026-07-23
> Regole per ogni commit: TDD (test rosso → verde), `make ci` verde, diff minimo,
> reversibile singolarmente (revert pulito o `alembic downgrade`), dichiarazione di
> layer nel PR (ADR-0030 §4), review order C7. Nessun commit dipende da quelli di
> wave successive.

## Wave 0 — Governance e contratti (nessun runtime cambiato)

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C0 | `docs: ADR-0047 multi-thesis workspace` | ADR + aggiornamento `contracts/openapi/openapi.yaml` (param opzionali, PATCH /projects) e `contracts/db/schema.sql` target | revert (solo docs) |

## Wave 1 — Thesis Manager (fondamenta)

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C1 | `feat(db): projects table + seed` (Layer: Business) | Migrazione M-A; ORM `Project`; test seed idempotente | downgrade M-A |
| C2 | `feat(backend): registry DB-backed` | `ProjectRegistryService` su DB, id sequenziali `thesis-NNN`, `PATCH /projects/{id}`; API `GET/POST` invariate; test: create → restart (nuova sessione) → progetto ancora presente | revert commit (registry torna in-memory) |
| C3 | `refactor(backend): resolver di scope unico` | `resolve_project_id()`; sostituisce i default literal sparsi; zero cambi di comportamento (test di parità) | revert |

## Wave 2 — Partizione dati (una tabella per commit)

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C4 | `feat(db): documents.project_id` | Migrazione M-B + ORM + `DocumentService`/API con param opzionale; upload nel progetto attivo; test isolamento documenti | downgrade M-B + revert |
| C5 | `feat(backend): retrieval project-scoped` | Filtro su ricerca ibrida, `/search`, `graph/retriever`, writing panel; test parità RAG thesis-agent + test isolamento | revert (filtro rimosso) |
| C6 | `feat(db): memories.project_id` | Migrazione M-C + `MemoryService` scoped + `/memory` param; chiavi companion scoped; test isolamento memoria | downgrade M-C + revert |
| C7 | `feat(db): conversations.project_id` | Migrazione M-D (backfill da scope AgentRun) + service/API; chat binding via colonna; test: lista conversazioni per progetto | downgrade M-D + revert |
| C8 | `feat(db): tasks/notes/agent_runs/events project_id` | Migrazione M-E + campo evento additivo (Layer: Runtime per l'envelope); test contratto eventi | downgrade M-E + revert |

## Wave 3 — Chiusura falle backend

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C9 | `fix(backend): ownership checks` | get/patch/delete per id su chapters/proposals/conversations verificano il progetto quando fornito; `copy_demo_structure(project_id)`; snapshot workspace filtrato; conformance usa il path param | revert |
| C10 | `fix(backend): knowledge fallback` | Il catalogo statico non riempie più i progetti vuoti; contract/ORM `Source` allineati (M-F) | revert |

## Wave 4 — Frontend

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C11 | `feat(frontend): scope injection unica` | Wrapper fetch con progetto attivo; fix `knowledgeClient` + SSR knowledge/research/canvas; rimozione default duplicati | revert |
| C12 | `feat(frontend): storage namespaced per progetto` | Chiavi `thesisos:{pid}:…` + migrazione una-tantum chiavi legacy → `thesis-agent`; reset store su switch | revert (chiavi legacy intatte) |
| C13 | `feat(frontend): UX multi-tesi` | ShellRouter senza pinning chat; "Nuova tesi" con nome; rename in Settings → `PATCH /projects`; prefs per-progetto | revert |

## Wave 5 — Qualificazione

| # | Commit | Contenuto | Rollback |
|---|---|---|---|
| C14 | `test(e2e): suite isolamento multi-tesi` | Scenario §4 del piano di migrazione automatizzato (thesis-002 vuota, upload isolato, demo invariata, restart-persistenza) | revert (solo test) |
| C15 | `chore(data): pulizia cur-11-review-isolation` (M-G) | Solo dopo conferma owner | downgrade |
| C16 | `docs: aggiornamento README/getting-started/px6` | PX-6.3 marcato completato; L-01 chiuso nel RC bundle | revert (solo docs) |

## Dipendenze

```text
C0 → C1 → C2 → C3 → {C4 → C5, C6, C7, C8} → C9 → C10 → {C11 → C12 → C13} → C14 → C15 → C16
```

I commit dentro le graffe sono tra loro indipendenti (ordinati per rischio). Dopo
**ogni** commit il sistema è deployabile e la tesi attuale funziona come oggi.

## Stima di massima

- Wave 0–1: 1 sessione. Wave 2: 2–3 sessioni (retrieval è il punto delicato).
- Wave 3–4: 1–2 sessioni. Wave 5: 1 sessione.

## STEP 5 — Punto di stop

L'implementazione parte **solo dopo approvazione esplicita** di questi quattro
documenti. Decisioni aperte da confermare in approvazione:

1. **ID default**: mantenere `thesis-agent` (raccomandato) vs rename fisico a
   `thesis-main` (sconsigliato: alto rischio, zero valore funzionale).
2. **Capitolo orfano** `cur-11-review-isolation`: eliminare (raccomandato) o
   spostare in demo-thesis.
3. **Nuove tesi**: id sequenziali `thesis-002/003/…` (come richiesto) — conferma.
