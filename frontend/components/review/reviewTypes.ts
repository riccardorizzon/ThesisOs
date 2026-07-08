export type ReviewChapterStatus = "bozza" | "revisione" | "approvato";

export type ReviewChapter = {
  id: string;
  title: string;
  status: ReviewChapterStatus;
  pendingChanges: number;
};

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
