# ADR-0034: Product Vision — Research Operating System

- **Status:** Accepted (Product Constitution v1.0 — ratified 2026-07-01)
- **Plane:** Product
- **Governance:** Subordinate to `docs/CONSTITUTION-GOVERNANCE.md`; defers to Runtime Constitution on conflict (P3)
- **Context:** ThesisOS v1.0 qualified the runtime (OR-1…OR-7, E.1) but the operator surface remains chat-centric and developer-oriented. Product v2 requires a frozen vision before UX implementation (PA-0). RFC-001 accepted Alternative C (Research OS) over chat-first, Notion-like, and document-RAG models.
- **Decision:** ThesisOS Product is a **Research Operating System** — a knowledge-centric workspace where sources, concepts, decisions, and writing form one system; AI maintains coherence **without** being the center of the interface. The academic thesis is the **first project template**, not the product definition.

- **Invariants (Product Constitution):**
  - **INV-PV-1:** ThesisOS Product is a Research OS, not a chatbot, not Notion+AI, not document-only RAG.
  - **INV-PV-2:** Concepts — not PDFs — are the conceptual center of the product (detailed in ADR-0037).
  - **INV-PV-3:** Product v2 is a **shell** over qualified runtime v1.0; PX milestones must not regress OR qualification.
  - **INV-PV-4:** First tenant is template-based (`project_id`); fashion-thesis content is not hardcoded into product chrome.
  - **INV-PV-5:** Governance (memory proposals, frozen decisions, corpus rules) remains; exposed as product flows, not engine jargon.

- **Non-goals (binding):** Compete with ChatGPT on open chat; standalone Zotero replacement; generic wiki; ghostwriting; multi-user collab as v2.0 core promise; runtime changes in PA-0; auto-generating engineering program in PA-0.

- **Compliance checklist (ASEP):**
  - [ ] **C1:** Vision doc and UX default do not position chat as primary home (see ADR-0036, ADR-0039)
  - [ ] **C2:** Marketing/onboarding copy matches Research OS positioning
  - [ ] **C3:** PX scope preserves OR-1…OR-7 regression
  - [ ] **C4:** No thesis-specific strings in AppShell without project template

- **Violation examples:**
  - Default route `/chat` with no Home → violates INV-PV-1 (with ADR-0036)
  - Removing memory proposal approval → violates INV-PV-5

- **References:** `docs/product/VISION.md`, `docs/product/rfc/RFC-001-research-os.md`, ADR-0035…0041
- **Supersedes:** none (first Product Vision ADR)
