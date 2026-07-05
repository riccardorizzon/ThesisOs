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

export type ProgramGraphNode = {
  node_id: string;
  node_type: "ewo" | "integration";
  wave_id: string;
};

export type ProgramGraphWave = {
  wave_id: string;
  title: string;
  depends_on_wave?: string | null;
  execute_in_parallel: boolean;
  merge_order: string[];
  workorders: string[];
  unblocks?: string | null;
  wave_type?: string | null;
  status?: string | null;
  sub_agents: Record<string, string>;
  nodes: ProgramGraphNode[];
};

export type ProgramGraphEdge = {
  source: string;
  target: string;
  edge_type: "depends_on_wave" | "merge_order";
  wave_id?: string | null;
};

export type ProgramGraphObservation = {
  schema_version: 1;
  program_id: string;
  parent_program: string;
  source: string;
  waves: ProgramGraphWave[];
  edges: ProgramGraphEdge[];
};

export type KnowledgeGraphNode = {
  id: string;
  slug: string;
  title: string;
  knowledge_state: KnowledgeState;
  is_core: boolean;
  degree: number;
};

export type KnowledgeGraphEdge = {
  source: string;
  target: string;
  relation: "related" | "supports" | "extends" | "contradicts";
};

export type KnowledgeGraphResponse = {
  schema_version: 1;
  focus_slug?: string | null;
  depth: number;
  view_mode: "graph" | "list";
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
  limits: {
    default_visible: number;
    soft_limit: number;
    hard_limit: number;
    visible_count: number;
    total_in_scope: number;
    truncated: boolean;
    force_list_view: boolean;
    show_performance_banner: boolean;
  };
};

export type JobFsmObservation = {
  schema_version: 1;
  read_only: true;
  source: string;
  vocabulary_domains: Array<{
    domain: string;
    vocabulary: string;
    values: string[];
    notes: string;
  }>;
  aggregate_to_job_fsm: Array<{
    aggregate_status: string;
    job_fsm_subset: string;
    display_label: string;
  }>;
  projection_jobs: Array<{
    ewo_id: string;
    aggregate_status: string;
    job_fsm_subset: string;
    wave_id?: string | null;
  }>;
  inv_r_11_note: string;
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
