/**
 * Library module stub data — Sources + Knowledge (PX-1)
 * Layer: Business (Product Plane)
 * Replaced by API in PX-3 (sources) / PX-4 (concepts).
 */

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

/** PX-1 corpus preview — aligned with thesis-agent knowledge base */
export const LIBRARY_SOURCES: LibrarySource[] = [
  {
    id: "benjamin-opera-arte",
    title: "L'opera d'arte nell'epoca della riproducibilità tecnica",
    subtitle: "Walter Benjamin",
    meta: "1936 · Libro",
    status: "approvata",
    relatedConceptIds: ["aura", "riproducibilita"],
  },
  {
    id: "barthes-mythologies",
    title: "Mythologies",
    subtitle: "Roland Barthes",
    meta: "1957 · Saggio",
    status: "esclusa",
    relatedConceptIds: ["mito", "stigmata"],
  },
  {
    id: "albers-interaction-color",
    title: "Interaction of Color",
    subtitle: "Josef Albers",
    meta: "1963 · Libro",
    status: "candidata",
    relatedConceptIds: ["percezione", "stigmata"],
  },
  {
    id: "csikszentmihalyi-flow",
    title: "Flow",
    subtitle: "Mihaly Csikszentmihalyi",
    meta: "1990 · Libro",
    status: "candidata",
    relatedConceptIds: ["esperienza", "percezione"],
  },
  {
    id: "hollander-sex-suits",
    title: "Sex and Suits",
    subtitle: "Anne Hollander",
    meta: "1994 · Saggio",
    status: "approvata",
    relatedConceptIds: ["abbigliamento", "stigmata"],
  },
];

export const LIBRARY_CONCEPTS: LibraryConcept[] = [
  {
    id: "stigmata",
    title: "STIGMATA",
    subtitle: "Framework centrale della tesi",
    meta: "4 fonti collegate",
    definition:
      "Segno percettivo che condensa significato culturale — asse teorico del corpus.",
    relatedSourceIds: [
      "barthes-mythologies",
      "albers-interaction-color",
      "hollander-sex-suits",
    ],
  },
  {
    id: "aura",
    title: "Aura",
    subtitle: "Benjamin — unicità dell'originale",
    meta: "1 fonte collegata",
    definition:
      "Presenza unica dell'oggetto nel tempo e nello spazio — erode con la riproducibilità.",
    relatedSourceIds: ["benjamin-opera-arte"],
  },
  {
    id: "riproducibilita",
    title: "Riproducibilità tecnica",
    subtitle: "Meccanica della diffusione visiva",
    meta: "1 fonte collegata",
    relatedSourceIds: ["benjamin-opera-arte"],
  },
  {
    id: "percezione",
    title: "Percezione visiva",
    subtitle: "Intersezione colore, forma, corpo",
    meta: "2 fonti collegate",
    relatedSourceIds: ["albers-interaction-color", "csikszentmihalyi-flow"],
  },
  {
    id: "mito",
    title: "Mito borghese",
    subtitle: "Barthes — naturalizzazione ideologica",
    meta: "1 fonte collegata",
    relatedSourceIds: ["barthes-mythologies"],
  },
  {
    id: "abbigliamento",
    title: "Abbigliamento come segno",
    subtitle: "Moda e identità visiva",
    meta: "1 fonte collegata",
    relatedSourceIds: ["hollander-sex-suits"],
  },
  {
    id: "esperienza",
    title: "Esperienza estetica",
    subtitle: "Flow e coinvolgimento percettivo",
    meta: "1 fonte collegata",
    relatedSourceIds: ["csikszentmihalyi-flow"],
  },
];

export function getSourceById(id: string): LibrarySource | undefined {
  return LIBRARY_SOURCES.find((s) => s.id === id);
}

export function getConceptById(id: string): LibraryConcept | undefined {
  return LIBRARY_CONCEPTS.find((c) => c.id === id);
}

export function getConceptsForSource(sourceId: string): LibraryConcept[] {
  const source = getSourceById(sourceId);
  if (source == null) return [];
  return source.relatedConceptIds
    .map((id) => getConceptById(id))
    .filter((c): c is LibraryConcept => c != null);
}

export function getSourcesForConcept(conceptId: string): LibrarySource[] {
  const concept = getConceptById(conceptId);
  if (concept == null) return [];
  return concept.relatedSourceIds
    .map((id) => getSourceById(id))
    .filter((s): s is LibrarySource => s != null);
}

export function sourceStatusMeta(status: SourceStatus): string {
  return SOURCE_STATUS_LABELS[status];
}
