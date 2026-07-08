"use client";

import dynamic from "next/dynamic";

import { PageSkeleton } from "@/components/ui/PageSkeleton";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

const KnowledgeGraphPanel = dynamic(
  () =>
    import("@/components/knowledge/graph/KnowledgeGraphPanel").then(
      (mod) => mod.KnowledgeGraphPanel
    ),
  {
    loading: () => (
      <PageSkeleton
        label="Caricamento grafo concetti"
        testId="knowledge-graph-skeleton"
        blocks={2}
      />
    ),
    ssr: false,
  }
);

export type KnowledgeGraphPanelLazyProps = {
  graph: KnowledgeGraphResponse;
  className?: string;
};

/** Lazy-loaded knowledge graph panel — M7.2 performance track. */
export function KnowledgeGraphPanelLazy(props: KnowledgeGraphPanelLazyProps) {
  return <KnowledgeGraphPanel {...props} />;
}
