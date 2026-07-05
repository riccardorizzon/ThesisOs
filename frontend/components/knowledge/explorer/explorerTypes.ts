import type { ConfidenceLevel, KnowledgeState } from "@/lib/knowledgeTypes";

export type ExplorerFilterState = {
  knowledgeState: KnowledgeState | "all";
  coreOnly: boolean;
  confidence: ConfidenceLevel | "all";
  showCandidates: boolean;
};

export const EXPLORER_STATE_OPTIONS: {
  value: KnowledgeState | "all";
  label: string;
}[] = [
  { value: "all", label: "Tutti gli stati" },
  { value: "candidate", label: "Candidato" },
  { value: "validated", label: "Validato" },
  { value: "linked", label: "Collegato" },
  { value: "referenced", label: "Citato in tesi" },
  { value: "deprecated", label: "Deprecato" },
];

export const EXPLORER_CONFIDENCE_OPTIONS: {
  value: ConfidenceLevel | "all";
  label: string;
}[] = [
  { value: "all", label: "Tutte" },
  { value: "alta", label: "Alta" },
  { value: "media", label: "Media" },
  { value: "bassa", label: "Bassa" },
];
