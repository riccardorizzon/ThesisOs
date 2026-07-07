import Link from "next/link";

import { ResearchCanvasViewport } from "@/components/research/canvas/ResearchCanvasViewport";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type ResearchCanvasPageProps = {
  graph: KnowledgeGraphResponse;
  focus?: string;
  view?: string;
};

/**
 * PX-5 canvas shell — header + spatial viewport (PX5-EWO-003).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasPage({ graph, focus, view }: ResearchCanvasPageProps) {
  return (
    <div className="mx-auto max-w-content space-y-4">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link
            href="/research"
            className="text-sm font-medium text-accent hover:underline cursor-pointer"
          >
            ← Research
          </Link>
          <p className="mt-2 text-xs font-medium uppercase tracking-wide text-ink-subtle">
            PX-5
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-ink">Mappa concettuale</h1>
          <p className="mt-1 text-sm text-ink-muted">
            Canvas spaziale — pan/zoom, nodi concetto, relazioni tipizzate.
          </p>
          {focus != null && (
            <p className="mt-1 text-xs text-ink-subtle">
              Focus: <span className="font-mono">{focus}</span>
            </p>
          )}
        </div>
        <p className="text-xs text-ink-subtle" data-testid="canvas-node-count">
          {graph.limits.visible_count} / {graph.limits.total_in_scope} concetti · depth{" "}
          {graph.depth}
        </p>
      </header>

      {graph.limits.show_performance_banner && (
        <p
          className="rounded-md border border-warning/30 bg-warning/5 px-3 py-2 text-sm text-warning"
          data-testid="canvas-performance-banner"
        >
          Canvas ampio — applica un filtro o riduci la profondità (soft limit{" "}
          {graph.limits.soft_limit})
        </p>
      )}

      {view != null && (
        <p className="text-sm text-ink-muted">
          Vista salvata <span className="font-mono">{view}</span> — ripristino camera in wave
          futura.
        </p>
      )}

      <ResearchCanvasViewport graph={graph} />
    </div>
  );
}
