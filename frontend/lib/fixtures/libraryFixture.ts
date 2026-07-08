/** Test-only library catalog data (M7.1). Not imported from product runtime paths. */

import type { LibraryConcept, LibrarySource } from "@/lib/libraryTypes";

export const FIXTURE_LIBRARY_SOURCES: LibrarySource[] = [
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

export const FIXTURE_LIBRARY_CONCEPTS: LibraryConcept[] = [
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

export function fixtureSourceById(id: string): LibrarySource | undefined {
  return FIXTURE_LIBRARY_SOURCES.find((s) => s.id === id);
}

export function fixtureConceptById(id: string): LibraryConcept | undefined {
  return FIXTURE_LIBRARY_CONCEPTS.find((c) => c.id === id);
}
