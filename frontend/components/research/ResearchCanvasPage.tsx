import { ResearchCanvasShell } from "@/components/research/canvas/ResearchCanvasShell";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type ResearchCanvasPageProps = {
  graph: KnowledgeGraphResponse;
  focus?: string;
  view?: string;
};

/**
 * PX-5 canvas page — server wrapper for client shell (PX5-EWO-004).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasPage({ graph, focus, view }: ResearchCanvasPageProps) {
  return <ResearchCanvasShell graph={graph} focus={focus} view={view} />;
}
