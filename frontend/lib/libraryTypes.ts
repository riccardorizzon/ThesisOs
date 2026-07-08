/** Shared library/source types — no runtime stub data (M7.1). */

export type SourceStatus = "candidata" | "approvata" | "esclusa";

export const SOURCE_STATUS_LABELS: Record<SourceStatus, string> = {
  candidata: "Candidata",
  approvata: "Approvata",
  esclusa: "Esclusa",
};

export const SOURCE_STATUS_OPTIONS: SourceStatus[] = [
  "candidata",
  "approvata",
  "esclusa",
];

export type LibrarySource = {
  id: string;
  title: string;
  subtitle?: string;
  meta?: string;
  status: SourceStatus;
  relatedConceptIds: string[];
};

export type LibraryConcept = {
  id: string;
  title: string;
  subtitle?: string;
  meta?: string;
  definition?: string;
  relatedSourceIds: string[];
};

export function sourceStatusMeta(status: SourceStatus): string {
  return SOURCE_STATUS_LABELS[status];
}

export function corpusStatusFromApi(
  corpusStatus: string | null | undefined,
  knowledgeState?: string
): SourceStatus {
  if (corpusStatus === "candidata" || corpusStatus === "approvata" || corpusStatus === "esclusa") {
    return corpusStatus;
  }
  if (knowledgeState === "deprecated") return "esclusa";
  if (knowledgeState === "validated" || knowledgeState === "linked") return "approvata";
  return "candidata";
}
