"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { CanvasFilterPopover } from "@/components/research/canvas/CanvasFilterPopover";
import { ResearchCanvasViewport } from "@/components/research/canvas/ResearchCanvasViewport";
import { ResearchInspectorRail } from "@/components/research/canvas/ResearchInspectorRail";
import { ResearchLensRail } from "@/components/research/canvas/ResearchLensRail";
import { SerendipityStrip } from "@/components/research/canvas/SerendipityStrip";
import { loadContext } from "@/lib/contextLoad";
import {
  buildStubLensContext,
  DEFAULT_CANVAS_FILTERS,
  filterGraphByLens,
  lensLabel,
  mergeSourceCounts,
  type CanvasFilterOptions,
  type CanvasLensContext,
  type CanvasLensId,
} from "@/lib/canvasLenses";
import {
  buildStubSerendipityContext,
  rankSerendipitySuggestions,
  type SerendipityContext,
  type SerendipitySuggestion,
} from "@/lib/canvasSerendipity";
import { DEFAULT_CANVAS_TRANSFORM, type CanvasTransform } from "@/lib/canvasTransform";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";
import { cn } from "@/lib/cn";

const DESKTOP_MIN_WIDTH = 1024;

function useDesktopCanvas(): boolean {
  const [isDesktop, setIsDesktop] = useState(true);

  useEffect(() => {
    const query = window.matchMedia(`(min-width: ${DESKTOP_MIN_WIDTH}px)`);
    const update = () => setIsDesktop(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return isDesktop;
}

export type ResearchCanvasShellProps = {
  graph: KnowledgeGraphResponse;
  focus?: string;
  view?: string;
};

/**
 * PX-5 canvas shell — layout, lenses, inspector, serendipity (PX5-EWO-004…007).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasShell({ graph, focus, view }: ResearchCanvasShellProps) {
  const isDesktop = useDesktopCanvas();
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>(
    graph.focus_slug != null ? [graph.focus_slug] : []
  );
  const [transform, setTransform] = useState<CanvasTransform>(DEFAULT_CANVAS_TRANSFORM);
  const [filters, setFilters] = useState<CanvasFilterOptions>(DEFAULT_CANVAS_FILTERS);
  const [lensContext, setLensContext] = useState<CanvasLensContext>(() => buildStubLensContext());
  const [serendipityContext, setSerendipityContext] = useState<SerendipityContext>(() =>
    buildStubSerendipityContext()
  );
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [lensLoading, setLensLoading] = useState(false);
  const [highlightSlugs, setHighlightSlugs] = useState<string[]>([]);
  const [highlightEdgeKeys, setHighlightEdgeKeys] = useState<string[]>([]);
  const [panRequest, setPanRequest] = useState<{ key: number; slugs: string[] } | null>(null);
  const [panRequestKey, setPanRequestKey] = useState(0);

  const filteredGraph = useMemo(
    () => filterGraphByLens(graph, filters, lensContext),
    [graph, filters, lensContext]
  );

  const serendipitySuggestions = useMemo(
    () => rankSerendipitySuggestions(filteredGraph, serendipityContext),
    [filteredGraph, serendipityContext]
  );

  useEffect(() => {
    let cancelled = false;

    async function enrichLensContext() {
      setLensLoading(true);
      try {
        const [contextPacket, knowledgeList] = await Promise.all([
          loadContext({ surface: "research" }),
          listKnowledgeObjects({ type: "concept" }).catch(() => null),
        ]);

        if (cancelled) return;

        const chapterConceptSlugs = new Set<string>();
        if (contextPacket.entity?.type === "chapter") {
          for (const concept of contextPacket.concepts) {
            if (concept.slug != null) chapterConceptSlugs.add(concept.slug);
            else chapterConceptSlugs.add(concept.id);
          }
        } else {
          for (const concept of contextPacket.concepts) {
            if (concept.slug != null) chapterConceptSlugs.add(concept.slug);
          }
        }

        const base = buildStubLensContext();
        const chapterLabel =
          contextPacket.entity?.type === "chapter"
            ? contextPacket.entity.title
            : "Capitolo attivo";

        setLensContext({
          ...base,
          activeChapterConceptSlugs:
            chapterConceptSlugs.size > 0 ? chapterConceptSlugs : base.activeChapterConceptSlugs,
          sourceCountByConceptSlug:
            knowledgeList != null
              ? mergeSourceCounts(base.sourceCountByConceptSlug, knowledgeList.objects)
              : base.sourceCountByConceptSlug,
        });
        setSerendipityContext({
          ...base,
          activeChapterConceptSlugs:
            chapterConceptSlugs.size > 0 ? chapterConceptSlugs : base.activeChapterConceptSlugs,
          sourceCountByConceptSlug:
            knowledgeList != null
              ? mergeSourceCounts(base.sourceCountByConceptSlug, knowledgeList.objects)
              : base.sourceCountByConceptSlug,
          decisions: contextPacket.decisions,
          activeChapterLabel: chapterLabel,
        });
      } finally {
        if (!cancelled) setLensLoading(false);
      }
    }

    void enrichLensContext();
    return () => {
      cancelled = true;
    };
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedSlugs([]);
  }, []);

  const setLensId = useCallback((lensId: CanvasLensId) => {
    setLensLoading(true);
    setFilters((current) => ({ ...current, lensId }));
    window.setTimeout(() => setLensLoading(false), 200);
  }, []);

  const activateSerendipitySuggestion = useCallback((suggestion: SerendipitySuggestion) => {
    const nextKey = panRequestKey + 1;
    setPanRequestKey(nextKey);
    setPanRequest({ key: nextKey, slugs: suggestion.targetSlugs });
    setHighlightSlugs(suggestion.targetSlugs);
    setHighlightEdgeKeys(suggestion.targetEdgeKeys);
    window.setTimeout(() => {
      setHighlightSlugs([]);
      setHighlightEdgeKeys([]);
    }, 2000);
  }, [panRequestKey]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        clearSelection();
        return;
      }
      if (event.key === "\\" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setInspectorOpen((open) => !open);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [clearSelection]);

  if (!isDesktop) {
    return (
      <div className="mx-auto max-w-content px-4 py-8" data-testid="canvas-desktop-required">
        <Link
          href="/research"
          className="text-sm font-medium text-accent hover:underline cursor-pointer"
        >
          ← Research
        </Link>
        <p className="mt-4 text-sm text-ink-muted">
          La mappa richiede desktop (≥1024px).
        </p>
      </div>
    );
  }

  return (
    <div
      className="mx-auto flex w-full max-w-[1400px] flex-col gap-3 px-4 py-4"
      data-testid="research-canvas-shell"
    >
      <header
        className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-3"
        data-testid="canvas-header-bar"
      >
        <div className="flex min-w-0 flex-wrap items-center gap-3">
          <Link
            href="/research"
            className="text-sm font-medium text-accent hover:underline cursor-pointer"
          >
            ← Research
          </Link>
          <div>
            <h1 className="text-lg font-semibold text-ink">Mappa concettuale</h1>
            {focus != null && (
              <p className="text-xs text-ink-subtle">
                Focus: <span className="font-mono">{focus}</span>
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 text-xs text-ink-muted">
            <span>Lente</span>
            <select
              value={filters.lensId}
              onChange={(event) => setLensId(event.target.value as CanvasLensId)}
              className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-ink"
              data-testid="canvas-lens-dropdown"
              aria-label="Lente attiva"
            >
              {(["L-all", "L-gap", "L-chapter", "L-author", "L-controversy", "L-unread"] as CanvasLensId[]).map(
                (lensId) => (
                  <option key={lensId} value={lensId}>
                    {lensLabel(lensId)}
                  </option>
                )
              )}
            </select>
          </label>
          <CanvasFilterPopover filters={filters} onChange={setFilters} />
          <button
            type="button"
            disabled
            className="rounded-md border border-border px-2 py-1 text-xs text-ink-subtle"
            data-testid="canvas-save-view-button"
          >
            Salva vista
          </button>
          <button
            type="button"
            disabled
            className="rounded-md border border-border px-2 py-1 text-xs text-ink-subtle"
            data-testid="canvas-basket-badge"
          >
            Basket 0
          </button>
          <p className="text-xs text-ink-subtle" data-testid="canvas-node-count">
            {filteredGraph.limits.visible_count} / {filteredGraph.limits.total_in_scope} concetti
          </p>
        </div>
      </header>

      {filteredGraph.limits.show_performance_banner && (
        <p
          className="rounded-md border border-warning/30 bg-warning/5 px-3 py-2 text-sm text-warning"
          data-testid="canvas-performance-banner"
        >
          Canvas ampio — applica un filtro o riduci la profondità (soft limit{" "}
          {filteredGraph.limits.soft_limit})
        </p>
      )}

      {view != null && (
        <p className="text-sm text-ink-muted" data-testid="canvas-saved-view-notice">
          Vista salvata <span className="font-mono">{view}</span> — ripristino camera in wave
          futura.
        </p>
      )}

      <div
        className="flex min-h-[640px] overflow-hidden rounded-lg border border-border bg-surface"
        data-testid="canvas-three-region-shell"
      >
        <aside
          className="hidden w-[240px] shrink-0 border-r border-border bg-surface p-3 lg:block"
          data-testid="canvas-lens-slot"
        >
          <ResearchLensRail activeLensId={filters.lensId} onLensChange={setLensId} />
        </aside>

        <div className="relative min-w-0 flex-1">
          {lensLoading && (
            <div
              className="pointer-events-none absolute inset-x-0 top-0 z-10 h-1 animate-pulse bg-accent/30"
              data-testid="canvas-lens-loading"
            />
          )}
          <ResearchCanvasViewport
            graph={filteredGraph}
            selectedSlugs={selectedSlugs}
            onSelectedSlugsChange={setSelectedSlugs}
            transform={transform}
            onTransformChange={setTransform}
            highlightSlugs={highlightSlugs}
            highlightEdgeKeys={highlightEdgeKeys}
            panRequest={panRequest}
          />
        </div>

        {inspectorOpen && (
          <aside
            className={cn(
              "hidden w-[320px] shrink-0 border-l border-border bg-surface p-3 xl:block"
            )}
            data-testid="canvas-inspector-slot"
          >
            <ResearchInspectorRail selectedSlugs={selectedSlugs} graph={filteredGraph} />
          </aside>
        )}
      </div>

      <SerendipityStrip
        suggestions={serendipitySuggestions}
        onSuggestionActivate={activateSerendipitySuggestion}
      />

      <footer
        className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-surface px-4 py-3"
        data-testid="canvas-action-bar"
      >
        <p className="text-sm text-ink-muted" data-testid="canvas-selection-count">
          {selectedSlugs.length === 0
            ? "Nessuna selezione"
            : `${selectedSlugs.length} selezionat${selectedSlugs.length === 1 ? "o" : "i"}`}
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled
            className="rounded-md border border-border px-3 py-1.5 text-sm text-ink-subtle"
            data-testid="canvas-add-basket-button"
          >
            Aggiungi al basket
          </button>
          <button
            type="button"
            disabled
            className="rounded-md bg-accent/40 px-3 py-1.5 text-sm text-ink-subtle"
            data-testid="canvas-writing-handoff-button"
          >
            Porta in Scrittura
          </button>
        </div>
      </footer>
    </div>
  );
}
