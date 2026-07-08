import type { ReviewChapter } from "@/components/review/reviewTypes";

export const FIXTURE_REVIEW_CHAPTERS: ReviewChapter[] = [
  {
    id: "cap-1",
    title: "Capitolo 1 — Introduzione",
    status: "revisione",
    pendingChanges: 3,
  },
  {
    id: "cap-2",
    title: "Capitolo 2 — Metodo",
    status: "bozza",
    pendingChanges: 0,
  },
  {
    id: "cap-3",
    title: "Capitolo 3 — Analisi",
    status: "revisione",
    pendingChanges: 1,
  },
];
