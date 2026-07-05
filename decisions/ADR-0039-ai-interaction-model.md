# ADR-0039: AI Interaction Model — Lateral Action Runner

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product
- **Context:** Chat-first UX competes with general assistants on wrong terms and encourages prompt engineering. Cursor/Copilot pattern: primary artifact center, AI lateral. v1.0 `/chat` is full-page default.
- **Decision:**

  ### Primary interaction model

  AI is a **lateral action runner**, not the central UI.

  ```text
  ┌──────────────┬─────────────────┬──────────────┐
  │   Outline    │     Editor      │  AI Panel    │
  │   (Writing)  │    (center)     │  (right)     │
  └──────────────┴─────────────────┴──────────────┘
  ```

  ### Action categories (not freeform first)

  | Action | Typical surface |
  |--------|-----------------|
  | Rewrite | Writing selection |
  | Deepen | Writing selection |
  | Find sources | Writing / Concept |
  | Verify | Writing / Chapter |
  | Compare | Concept / Sources |
  | Summarize | Source / Selection |
  | Explain | Knowledge concept |

  Actions invoke runtime via **ContextPacket + action id**; streaming preserved.

  ### Contextual panel

  Panel actions **change with selection and surface** (see Product Spec §5.6). No single static button row.

  ### Chat disposition

  - **`/ai`:** full-page power mode for advanced users — optional
  - **Not default home** (ADR-0036)
  - Writing module embeds panel; does not navigate away on action

  ### Academic production

  Writing actions MUST trigger OR-6 paths (persona OFF, REV-006, A/B) via Context Engine `writing_rules` — not duplicate prompts in frontend.

  ### Reviewer / Planner

  Not separate agents in v2.0 constitution — **modes/actions** on same engine (PX-6 polish). Separate agent topology requires Product ADR supersession.

- **Invariants:**
  - **INV-AI-1:** Default product entry is not full-page chat.
  - **INV-AI-2:** Writing desktop layout includes lateral AI panel (three-panel).
  - **INV-AI-3:** Standard actions use Context Engine (ADR-0038).
  - **INV-AI-4:** Frontend MUST NOT embed OR-6 oracle text as sole enforcement — runtime remains authoritative.
  - **INV-AI-5:** Proposal to make chat central requires Product Constitution vNext (P8), not engineering program alone.

- **Compliance checklist:**
  - [ ] **C1:** Home ≠ Chat page component
  - [ ] **C2:** Writing route renders AI panel slot
  - [ ] **C3:** Action catalog documented per surface in spec

- **Violation examples:**
  - "Put chat in the center" redesign → **FAIL** INV-AI-5
  - Writing page without panel → INV-AI-2

- **References:** ADR-0034, ADR-0036, ADR-0038, OR-6, W-06
