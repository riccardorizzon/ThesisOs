"use client";

import dynamic from "next/dynamic";

import { PageSkeleton } from "@/components/ui/PageSkeleton";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

const ResearchCanvasShell = dynamic(
  () =>
    import("@/components/research/canvas/ResearchCanvasShell").then(
      (mod) => mod.ResearchCanvasShell
    ),
  {
    loading: () => (
      <PageSkeleton
        label="Caricamento canvas di ricerca"
        testId="research-canvas-skeleton"
        blocks={2}
      />
    ),
    ssr: false,
  }
);

export type ResearchCanvasShellLazyProps = {
  graph: KnowledgeGraphResponse;
  focus?: string;
  view?: string;
};

/** Lazy-loaded research canvas — defers heavy client bundle (M7.2). */
export function ResearchCanvasShellLazy(props: ResearchCanvasShellLazyProps) {
  return <ResearchCanvasShell {...props} />;
}
