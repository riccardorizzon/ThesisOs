# Thesis Agent — Fashion Design (STIGMATA)

> **Non è una migrazione di Kimi.** È la trasformazione di mesi di lavoro in una
> knowledge base strutturata che ThesisOS può usare come fondazione per il writer
> e per il contesto operativo (M2 memory).

**Origine:** estratto dalla chat Kimi Claw (sessione esportata, giugno 2026).
**Materiale binario** (PDF, immagini): va importato in `04_KNOWLEDGE/` — vedi
`04_KNOWLEDGE/README.md`.

**Entry point unico:** questo file. I file `*.md` alla root di questa cartella
(`IDENTITY.md`, `WRITING_RULES.md`, …) sono **alias di compatibilità** — reindirizzano
ai path canonici sotto; non duplicare contenuto lì.

## Come leggere

| Ordine | Cartella | Contenuto |
|--------|----------|-----------|
| 1 | `01_SYSTEM/` | Chi è l'agente, come si comporta, memoria |
| 2 | `02_METHOD/` | Protocolli di revisione, ricerca, scrittura |
| 3 | `03_PROJECT/` | Stato tesi, decisioni congelate, terminologia |
| 4 | `04_KNOWLEDGE/` | Corpus documentale (import da Kimi) |
| 5 | `05_MEMORY/` | Memoria operativa (permanente / temporanea / changelog) |
| 6 | `chapters/` | Capitoli promossi in M6 (§1.1–2.4, cap. 3 metodologico) |

### Path canonici (fonte di verità)

| Concetto | Path canonico | Alias root (compatibilità) |
|----------|---------------|----------------------------|
| Identità | `01_SYSTEM/Identity.md` | `IDENTITY.md` |
| Protocollo memoria | `01_SYSTEM/Memory-Protocol.md` | `MEMORY_PROTOCOL.md` |
| Regole scrittura | `02_METHOD/Writing-Rules.md` | `WRITING_RULES.md` |
| Protocollo revisione | `02_METHOD/Review-Protocol.md` | `REVIEW_PROTOCOL.md` |
| Policy fonti | `02_METHOD/Source-Classification.md` | `SOURCE_POLICY.md` |
| Regole progetto | `03_PROJECT/Project-Rules.md` | `PROJECT_RULES.md` |
| Regole università | `03_PROJECT/University-Rules.md` | `UNIVERSITY_RULES.md` |
| Regole relatrice | `03_PROJECT/Relatrice-Rules.md` | `RELATRICE_RULES.md` |

## Integrazione ThesisOS

| Questo agente | ThesisOS (M2+) |
|---------------|----------------|
| `01_SYSTEM` + regole in `02_METHOD` | `memories` kind `editable` (singleton, sempre iniettato) |
| `03_PROJECT/Thesis-State.md`, `Decisions.md` | `memories` kind `thesis`, `decision` |
| `05_MEMORY/Permanent.md` | approvato dall'utente → `editable` / `decision` |
| `04_KNOWLEDGE/*` | M3 `documents` + M4 retrieval (RAG) |
| Writer route (M6) | legge `plan` + `retrieved_context` + operational memory |

**Fonte di verità runtime:** dopo l'import, ThesisOS `memories` e `documents` vincono
su questi file markdown. Questa directory è il **blueprint** e il mirror di lavoro
fino alla promozione in DB.

## Oggetto della tesi

**Titolo di lavoro:** processo creativo nel fashion design contemporaneo.
**Caso applicativo:** collezione STIGMATA (non oggetto principale di ricerca).
**Metodo:** qualitativo, interpretativo, tracciabile alle fonti — non quantitativo.

## Artefatti congelati

Materializzati in `03_PROJECT/` (checksum in front-matter dove applicabile):

- CORE THEORY MAP v2.1 → `Core-Theory-Map.md`
- BIBLIOGRAPHY_MASTER v1.0 → `Bibliography-Master.md`
- OUTLINE_MASTER v1.0 → `Outline-Master.md`
- STIGMATA_DOCUMENTATION_FRAMEWORK v1.0 → `Stigmata-Framework.md`

## Stato capitoli

| Capitolo | File | Stato |
|----------|------|-------|
| Cap. 1 (§1.1–1.3) | `chapters/ch01/` × 3 | Congelato · promosso M6 |
| Cap. 2 (§2.1–2.4) | `chapters/ch02/` × 4 | Congelato · promosso M6 |
| Cap. 3 metodologico | `chapters/ch03/CAP03_progettazione_metodologica.md` | Progettazione approvata · §3.1 **PRONTO PER REVISIONE** |

Dettaglio runtime: `03_PROJECT/Thesis-State.md` · promozione: `_migration/promotion-log.md`.
