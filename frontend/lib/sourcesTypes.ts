import type {
  ConfidenceLevel,
  CreatedBy,
  KnowledgeState,
  ProposalState,
} from "@/lib/knowledgeTypes";

export type RelatedConceptRef = {
  id: string;
  slug: string;
  title: string;
};

export type SourceListItem = {
  id: string;
  slug: string;
  type: "source";
  title: string;
  subtitle?: string | null;
  summary?: string | null;
  confidence: ConfidenceLevel;
  knowledge_state: KnowledgeState;
  linked_counts: {
    sources: number;
    chapters: number;
    concepts: number;
    decisions: number;
    authors: number;
    citations: number;
  };
  created_by: CreatedBy;
  proposal_state: ProposalState;
  is_core: boolean;
  related_concepts: RelatedConceptRef[];
  corpus_status?: string | null;
  document_id?: string | null;
  deletable?: boolean;
};

export type SourceListResponse = {
  sources: SourceListItem[];
  total: number;
};

export type SourcesFilterState = {
  query: string;
  knowledgeState: KnowledgeState | "all";
  confidence: ConfidenceLevel | "all";
  includeDeprecated: boolean;
};

export const KNOWLEDGE_STATE_FILTER_OPTIONS: {
  value: KnowledgeState | "all";
  label: string;
}[] = [
  { value: "all", label: "Tutti gli stati" },
  { value: "candidate", label: "Candidato" },
  { value: "validated", label: "Validato" },
  { value: "linked", label: "Collegato" },
  { value: "deprecated", label: "Deprecato" },
];

export const CONFIDENCE_FILTER_OPTIONS: {
  value: ConfidenceLevel | "all";
  label: string;
}[] = [
  { value: "all", label: "Tutte" },
  { value: "alta", label: "Alta" },
  { value: "media", label: "Media" },
  { value: "bassa", label: "Bassa" },
  { value: "non_valutata", label: "Non valutata" },
];
