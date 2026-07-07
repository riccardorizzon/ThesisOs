# M7 Architecture Lock

> **Status:** DRAFT until signed at M7.0b gate  
> **Authority:** `plans/m7-product-hardening-plan.md` · ADR-0044  
> **Rule:** from sign-off until M7 PASS — **no contract changes** without Architect unlock.

---

## Purpose

Freeze API, DB schema, endpoint names, and payload shapes **before** Wave 1 implementation.
During M7 waves, builders implement against this document only — no drive-by contract edits.

---

## Sign-off checklist

| # | Item | Owner | Status |
|---|------|-------|--------|
| L1 | API endpoints listed below are final for M7 | Architect | ☐ |
| L2 | DB schema changes limited to migration `0007` (+ proposal table if needed) | Architect | ☐ |
| L3 | Request/response JSON shapes reviewed | Architect | ☐ |
| L4 | Naming conventions locked (snake_case API, camelCase FE clients) | Architect | ☐ |
| L5 | No new GraphState fields | Architect | ☐ |
| L6 | No new ASEP / builder_engine modules | Architect | ☐ |
| L7 | OpenAPI update deferred to Wave 4 (`P-DOCS-SYNC`) | Architect | ☐ |

**Sign:** `Architecture Lock PASS` recorded in `plans/m7-dashboard.md` with date.

---

## Frozen API surface (M7)

### Existing — do not rename

| Method | Path | Notes |
|--------|------|-------|
| POST | `/upload` | Document ingest |
| GET | `/documents`, `/documents/{id}` | List/detail |
| POST | `/documents/{id}/index` | Manual re-index |
| POST | `/search` | Hybrid corpus search |
| GET/POST/PATCH | `/chapters`, `/chapters/{id}` | Chapter CRUD |
| POST | `/chat` | SSE; **extend** body with optional `conversation_id` |
| POST | `/writing/actions` | SSE; **extend** to pass retrieval context |
| GET | `/projects/{project_id}/sources` | **change impl** → DB only |
| GET | `/projects/{project_id}/sources/{slug}` | DB only |
| GET | `/projects/{project_id}/sources/bibliography/export` | BibTeX from DB |
| GET | `/projects/{project_id}/knowledge/objects` | DB only, no catalog fallback |
| GET | `/projects/{project_id}/knowledge/search` | DB only |
| GET | `/projects/{project_id}/context` | Unchanged shape |

### New endpoints (M7 only)

| Method | Path | Request | Response |
|--------|------|---------|----------|
| GET | `/conversations` | `?project_id=` | `{ items: ConversationSummary[] }` |
| POST | `/conversations` | `{ project_id, title? }` | `ConversationSummary` |
| GET | `/conversations/{id}/messages` | — | `{ items: Message[] }` |
| GET | `/proposals` | `?project_id=&chapter_id=` | `{ items: Proposal[] }` |
| POST | `/proposals` | `{ project_id, chapter_id, original, proposed, action, metadata? }` | `Proposal` |
| POST | `/proposals/{id}/accept` | `{ expected_chapter_version? }` | `{ chapter: Chapter }` |
| POST | `/proposals/{id}/reject` | `{ reason? }` | `{ proposal: Proposal }` |
| GET | `/export/chapters/{id}.md` | — | `text/markdown` file download |

### Explicitly out of M7

- `/jobs` (remains 501)
- `/outline`, `/summarize` (not implemented)
- Auth endpoints
- Multi-project CRUD beyond existing in-memory registry

---

## Frozen DB schema (M7)

| Change | Migration | Content |
|--------|-----------|---------|
| Populate `sources` table | `0007_sources_populated.py` | Seed from legacy catalog; project_id scoped |
| `proposals` table (if not reusing chapter_versions) | `0007` or `0008` | id, project_id, chapter_id, status, original, proposed, action, created_at |
| **No** changes to `GraphState` / LangGraph tables beyond checkpointer usage |

Existing tables used as-is: `conversations`, `messages`, `concepts`, `documents`, `chunks`, `embeddings`, `chapters`, `chapter_versions`.

---

## Frozen payloads (key shapes)

### POST `/chat` (extended)

```json
{
  "message": "string",
  "conversation_id": "uuid | null",
  "project_id": "string"
}
```

### Proposal

```json
{
  "id": "uuid",
  "project_id": "string",
  "chapter_id": "uuid",
  "status": "pending | accepted | rejected",
  "original": "string",
  "proposed": "string",
  "action": "rewrite | verify | expand | find-sources",
  "created_at": "iso8601"
}
```

### SourceListItem (unchanged schema; data from DB)

Uses existing `app/schemas/knowledge.py` types — no field renames in M7.

---

## Naming lock

| Layer | Convention | Example |
|-------|------------|---------|
| REST paths | kebab-case segments | `/bibliography/export` |
| JSON fields | snake_case | `conversation_id` |
| TS client functions | camelCase | `listConversations()` |
| DB columns | snake_case | `project_id` |
| Packet IDs | `P-{DOMAIN}-{LAYER}` | `P-SOURCES-DB` |

---

## Unlock procedure

To change a locked contract mid-M7:

1. Record reason in `plans/m7-dashboard.md` blocker section
2. Architect approves unlock in PR description
3. Update **this file** with version bump
4. Re-run `make ci` on all open branches (rebase required)

---

*Version: 1.0 — 2026-07-07*
