/**
 * Knowledge Object envelope types — PX3-EWO-001
 * Layer: Business (Product Plane)
 * Spec: px3-knowledge-experience-v2 §3.1
 */

export type KnowledgeObjectType = "concept" | "source";

export type KnowledgeState =
  | "candidate"
  | "validated"
  | "linked"
  | "referenced"
  | "deprecated";

export type ConfidenceLevel = "alta" | "media" | "bassa" | "non_valutata";

export type CreatedBy = "operatore" | "importazione" | "estrazione" | "ai";

export type ProposalState =
  | "nessuna"
  | "in_attesa"
  | "approvata"
  | "rifiutata";

export type LinkedCounts = {
  sources: number;
  chapters: number;
  concepts: number;
  decisions: number;
  authors: number;
  citations: number;
};

export type KnowledgeObjectEnvelope = {
  id: string;
  slug: string;
  type: KnowledgeObjectType;
  title: string;
  subtitle?: string | null;
  summary?: string | null;
  confidence: ConfidenceLevel;
  knowledge_state: KnowledgeState;
  linked_counts: LinkedCounts;
  created_by: CreatedBy;
  proposal_state: ProposalState;
  is_core: boolean;
};

export type KnowledgeObjectListResponse = {
  objects: KnowledgeObjectEnvelope[];
  total: number;
};

export type ConceptDetailEnvelope = KnowledgeObjectEnvelope & {
  definition?: string | null;
};

export type ConceptHeaderEnvelope = {
  id: string;
  slug: string;
  title: string;
  subtitle?: string | null;
  confidence: ConfidenceLevel;
  knowledge_state: KnowledgeState;
  is_core: boolean;
};

export type ConceptDefinitionEnvelope = {
  slug: string;
  definition?: string | null;
  source_count: number;
};

export type ConformanceProjection = {
  schema_version: 1;
  program_id: string;
  derived_at: string;
  supervisor: { state: string; reason?: string | null };
  waves: Record<
    string,
    { status: string; jobs: Record<string, { status: string }> }
  >;
  gates: { ci: string; coverage: string };
};

export const KNOWLEDGE_STATE_LABELS: Record<KnowledgeState, string> = {
  candidate: "Candidato",
  validated: "Validato",
  linked: "Collegato",
  referenced: "Citato in tesi",
  deprecated: "Deprecato",
};

export const CONFIDENCE_LABELS: Record<ConfidenceLevel, string> = {
  alta: "Alta",
  media: "Media",
  bassa: "Bassa",
  non_valutata: "Non valutata",
};

export const KNOWLEDGE_TYPE_LABELS: Record<KnowledgeObjectType, string> = {
  concept: "Concetto",
  source: "Fonte",
};
