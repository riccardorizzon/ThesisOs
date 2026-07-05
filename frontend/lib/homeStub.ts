import type { ProgressChapter } from "@/lib/progress";

/** Fallback when chapters API unavailable — PX-1 stub */
export const STUB_CHAPTERS: ProgressChapter[] = [
  { id: "1", title: "Cap. 1 — Introduzione", status: "approved", weight: 1 },
  { id: "2", title: "Cap. 2 — Quadro teorico", status: "review", weight: 1.2 },
  { id: "3", title: "Cap. 3 — Metodologia", status: "draft", weight: 1 },
  { id: "4", title: "Cap. 4 — Analisi", status: "draft", weight: 1.5 },
  { id: "5", title: "Cap. 5 — STIGMATA", status: "draft", weight: 1 },
];

export type ActivityItem = {
  entityType: "chapter" | "source" | "concept" | "decision";
  title: string;
  subtitle?: string;
  meta?: string;
  href?: string;
};

/** Placeholder activity feed — ADR-0040 INV-PS-4 until activities API */
export const HOME_ACTIVITY_STUB: ActivityItem[] = [
  {
    entityType: "chapter",
    title: "Cap. 2 — Quadro teorico",
    subtitle: "In revisione",
    meta: "2 ore fa",
    href: "/writing/2",
  },
  {
    entityType: "source",
    title: "Benjamin — L'opera d'arte nell'epoca della riproducibilità",
    subtitle: "Fonte approvata",
    meta: "Ieri",
    href: "/sources",
  },
  {
    entityType: "decision",
    title: "CORPUS-02 — Esclusione Mythologies",
    subtitle: "Decisione vincolante",
    meta: "3 giorni fa",
    href: "/knowledge",
  },
];
