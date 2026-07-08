import { PageSkeleton } from "@/components/ui/PageSkeleton";

export default function ResearchCanvasLoading() {
  return (
    <PageSkeleton
      label="Caricamento canvas di ricerca"
      testId="research-canvas-page-skeleton"
      blocks={2}
    />
  );
}
