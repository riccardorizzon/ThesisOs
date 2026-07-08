import {
  DEFAULT_PRODUCT_ID,
  DEFAULT_PROJECT_ID,
  type ContextPacket,
} from "@/lib/contextClient";

/** Test-only context packet fixture (M7.1). */
export const FIXTURE_CONTEXT_PACKET: ContextPacket = {
  schema_version: "0.2",
  project_context: {
    project_id: DEFAULT_PROJECT_ID,
    product_id: DEFAULT_PRODUCT_ID,
  },
  presentation: { surface: "writing" },
  project: {
    title: "Tesi STIGMATA",
    phase: "Sviluppo argomentativo",
    progress_pct: 42,
  },
  entity: null,
  selection_anchor: null,
  relevant_sources: [],
  concepts: [],
  decisions: [
    {
      id: "stub-corpus-02",
      title: "CORPUS-02",
      summary: "Barthes Mythologies — escluso dal corpus attivo",
      binding: true,
    },
    {
      id: "stub-corpus-03",
      title: "CORPUS-03",
      summary: "Bourriaud / estetica relazionale — escluso",
      binding: true,
    },
  ],
  definitions: [],
  citations_available: [],
  corpus_constraints: [
    "CORPUS-02: Barthes Mythologies — escluso dal corpus attivo",
    "CORPUS-03: Bourriaud / estetica relazionale — escluso",
  ],
  writing_rules: [
    "Italiano accademico; termini da Terminology.md",
    "Corpus approvato only (Bibliography-Master)",
  ],
  memory_proposals_pending: 0,
  recent_activity: [],
  token_budget: 8000,
};
