import { ResearchCanvasShellLazy } from "@/components/research/ResearchCanvasShellLazy";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type ResearchCanvasPageProps = {
  graph: KnowledgeGraphResponse;
  focus?: string;
  view?: string;
};

/**
 * PX-5 canvas page — server wrapper for lazy client shell (M7.2).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasPage({ graph, focus, view }: ResearchCanvasPageProps) {
  return <ResearchCanvasShellLazy graph={graph} focus={focus} view={view} />;
}
