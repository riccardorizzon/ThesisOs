/**
 * PX-1 stub data for review workflow — replaced by API in PX-2+.
 * Layer: Business (Product Plane)
 */

export type ReviewChapterStatus = "bozza" | "revisione" | "approvato";

export type ReviewChapter = {
  id: string;
  title: string;
  status: ReviewChapterStatus;
  pendingChanges: number;
};

export const REVIEW_CHAPTERS: ReviewChapter[] = [
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

export function reviewStatusLabel(status: ReviewChapterStatus): string {
  switch (status) {
    case "bozza":
      return "Bozza";
    case "revisione":
      return "In revisione";
    case "approvato":
      return "Approvato";
  }
}
