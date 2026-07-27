# ADR-0036: Information Architecture

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product
- **Context:** v1.0 frontend exposes Chat, Workspace, Library, Memory, Outline (stub), Settings — a developer layout. Product v2 requires a researcher-facing IA frozen before PX-1.
- **Decision:**

  ### Primary navigation (sidebar)

  ```text
  Home
  Research
  Writing
  Manoscritto
  Sources
  Knowledge
  ─────────
  Settings
  ```

  **Amendment (2026-07-27):** Manoscritto added as sixth primary module between Writing
  and Sources — read-only thesis manuscript reader (`/manuscript`). Review and AI remain
  adjunct surfaces outside primary nav.

  ### Default entry

  - **`/` redirects to Home**, not `/chat`.
  - `/chat` deprecated as primary; absorbed into `/ai` (power mode) or Writing AI panel.

  ### Route map

  | Route | Module |
  |-------|--------|
  | `/` | Home |
  | `/research`, `/research/[conceptId]` | Research |
  | `/writing`, `/writing/[chapterId]` | Writing |
  | `/manuscript`, `/manuscript/[chapterId]` | Manoscritto |
  | `/sources`, `/sources/[sourceId]` | Sources |
  | `/knowledge`, `/knowledge/[conceptId]` | Knowledge |
  | `/ai` | AI power mode (optional full chat) |
  | `/settings` | Settings |

  ### Legacy route disposition

  | Legacy | Disposition |
  |--------|-------------|
  | `/chat` | Redirect or embed under `/ai`; not default home |
  | `/library` | `/sources` |
  | `/memory` | `/knowledge` + `/settings` (admin) |
  | `/workspace` | `/writing` |
  | `/outline` | Writing left panel |
  | `/documents/*` | `/sources/*` (PX-3) |

- **Invariants:**
  - **INV-IA-1:** Sidebar contains exactly these six primary modules + Settings: Home,
    Research, Writing, Manoscritto, Sources, Knowledge (no Memory/Corpus/Chat as top-level).
  - **INV-IA-2:** Home is the default landing route after auth/load.
  - **INV-IA-3:** Writing uses fixed three-panel layout (outline | editor | AI panel) on desktop — ADR-0039.
  - **INV-IA-4:** IA changes require Product Constitution amendment (P8) or ADR-0036 supersession — not silent route adds.

- **Compliance checklist:**
  - [ ] **C1:** `frontend/app/page.tsx` (or equivalent) default → Home
  - [ ] **C2:** Root layout nav matches sidebar spec
  - [ ] **C3:** No new top-level nav item without ADR update

- **Violation examples:**
  - Restoring `/chat` as home → INV-IA-2
  - Adding "Admin" exposing OR gates in nav → INV-IA-1

- **References:** ADR-0034, ADR-0039, `docs/product/specs/thesisos-product-ux-v1.md` §4
