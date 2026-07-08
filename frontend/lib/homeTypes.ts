export type ActivityItem = {
  entityType: "chapter" | "source" | "concept" | "decision";
  title: string;
  subtitle?: string;
  meta?: string;
  href?: string;
};
