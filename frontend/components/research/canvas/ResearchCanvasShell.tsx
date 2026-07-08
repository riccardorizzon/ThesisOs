"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { CanvasHardLimitModal } from "@/components/research/canvas/CanvasHardLimitModal";
import { CanvasMinimap } from "@/components/research/canvas/CanvasMinimap";
import { CanvasFilterPopover } from "@/components/research/canvas/CanvasFilterPopover";
import { ResearchBasketDrawer } from "@/components/research/canvas/ResearchBasketDrawer";
import { ResearchCanvasViewport } from "@/components/research/canvas/ResearchCanvasViewport";
import { ResearchInspectorRail } from "@/components/research/canvas/ResearchInspectorRail";
import { ResearchLensRail } from "@/components/research/canvas/ResearchLensRail";
import { SaveViewModal } from "@/components/research/canvas/SaveViewModal";
import { SerendipityStrip } from "@/components/research/canvas/SerendipityStrip";
import { loadContext } from "@/lib/contextLoad";
import {
  addToCanvasBasket,
  basketItemsFromSlugs,
  loadCanvasBasket,
  removeFromCanvasBasket,
  stageCanvasBasketHandoff,
  type CanvasBasketItem,
} from "@/lib/canvasBasket";
import {
  buildClusterChips,
  exceedsHardLimit,
  graphWithClusterCollapse,
} from "@/lib/canvasCluster";
import { layoutCanvasNodes } from "@/lib/canvasLayout";
import {
  getCanvasSavedView,
  loadCanvasSavedViews,
  saveCanvasView,
  type CanvasSavedView,
} from "@/lib/canvasSavedViews";
import {
  buildLensContextFromGraph,
  DEFAULT_CANVAS_FILTERS,
  filterGraphByLens,
  lensLabel,
  mergeSourceCounts,
  type CanvasFilterOptions,
  type CanvasLensContext,
  type CanvasLensId,
} from "@/lib/canvasLenses";
import {
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
  const router = useRouter();
  const canvasRegionRef = useRef<HTMLDivElement>(null);
  const isDesktop = useDesktopCanvas();
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>(
    graph.focus_slug != null ? [graph.focus_slug] : []
  );
  const [transform, setTransform] = useState<CanvasTransform>(DEFAULT_CANVAS_TRANSFORM);
  const [filters, setFilters] = useState<CanvasFilterOptions>(DEFAULT_CANVAS_FILTERS);
  const [lensContext, setLensContext] = useState<CanvasLensContext>(() =>
    buildLensContextFromGraph(graph)
  );
  const [serendipityContext, setSerendipityContext] = useState<SerendipityContext>(() => ({
    ...buildLensContextFromGraph(graph),
    decisions: [],
    activeChapterLabel: null,
  }));
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [lensLoading, setLensLoading] = useState(false);
  const [highlightSlugs, setHighlightSlugs] = useState<string[]>([]);
  const [highlightEdgeKeys, setHighlightEdgeKeys] = useState<string[]>([]);
  const [panRequest, setPanRequest] = useState<{ key: number; slugs: string[] } | null>(null);
  const [panRequestKey, setPanRequestKey] = useState(0);
  const [basketItems, setBasketItems] = useState<CanvasBasketItem[]>([]);
  const [basketOpen, setBasketOpen] = useState(false);
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const [savedViews, setSavedViews] = useState<CanvasSavedView[]>([]);
  const [saveToast, setSaveToast] = useState<string | null>(null);
  const [clusterMode, setClusterMode] = useState(false);
  const [expandedClusterIds, setExpandedClusterIds] = useState<Set<string>>(() => new Set());
  const [viewportSize, setViewportSize] = useState({ width: 800, height: 560 });
  const [minimapOpen, setMinimapOpen] = useState(true);

  const filteredGraph = useMemo(
    () => filterGraphByLens(graph, filters, lensContext),
    [graph, filters, lensContext]
  );

  const layout = useMemo(() => layoutCanvasNodes(filteredGraph), [filteredGraph]);
  const clusterChips = useMemo(
    () => (clusterMode ? buildClusterChips(filteredGraph, layout) : []),
    [clusterMode, filteredGraph, layout]
  );
  const displayGraph = useMemo(
    () =>
      graphWithClusterCollapse(filteredGraph, clusterMode, expandedClusterIds, clusterChips),
    [filteredGraph, clusterMode, expandedClusterIds, clusterChips]
  );

  const hardLimitBlocked = exceedsHardLimit(filteredGraph, clusterMode);

  const serendipitySuggestions = useMemo(
    () => rankSerendipitySuggestions(displayGraph, serendipityContext),
    [displayGraph, serendipityContext]
  );

  useEffect(() => {
    setBasketItems(loadCanvasBasket());
    setSavedViews(loadCanvasSavedViews());
  }, []);

  useEffect(() => {
    if (view == null) return;
    const saved = getCanvasSavedView(savedViews, view);
    if (saved == null) return;
    setTransform(saved.camera);
    setFilters(saved.filters);
    if (saved.include_selection && saved.selected_ids.length > 0) {
      setSelectedSlugs(saved.selected_ids);
    }
  }, [view, savedViews]);

  useEffect(() => {
    const element = canvasRegionRef.current;
    if (element == null) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry == null) return;
      setViewportSize({
        width: entry.contentRect.width,
        height: entry.contentRect.height,
      });
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

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

        const base = buildLensContextFromGraph(graph);
        const chapterLabel =
          contextPacket.entity?.type === "chapter"
            ? contextPacket.entity.title
            : "Capitolo attivo";

        setLensContext({
          ...base,
          activeChapterConceptSlugs: chapterConceptSlugs,
          sourceCountByConceptSlug:
            knowledgeList != null
              ? mergeSourceCounts(base.sourceCountByConceptSlug, knowledgeList.objects)
              : base.sourceCountByConceptSlug,
        });
        setSerendipityContext({
          ...base,
          activeChapterConceptSlugs: chapterConceptSlugs,
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

  const addSelectionToBasket = useCallback(
    (slugs: readonly string[]) => {
      const incoming = basketItemsFromSlugs(filteredGraph, slugs);
      if (incoming.length === 0) return;
      setBasketItems((current) => addToCanvasBasket(current, incoming));
    },
    [filteredGraph]
  );

  const handleBasketHandoff = useCallback(() => {
    if (basketItems.length === 0) return;
    stageCanvasBasketHandoff(basketItems);
    setBasketOpen(false);
    router.push("/writing?panel=contesto&canvasBasket=1");
  }, [basketItems, router]);

  const handleSaveView = useCallback(
    (payload: { name: string; description?: string; includeSelection: boolean }) => {
      const next = saveCanvasView(savedViews, {
        name: payload.name,
        description: payload.description,
        focus_slug: focus ?? graph.focus_slug,
        camera: transform,
        lens_id: filters.lensId,
        filters,
        selected_ids: payload.includeSelection ? [...selectedSlugs] : [],
        include_selection: payload.includeSelection,
      });
      setSavedViews(next);
      setSaveToast("Vista salvata");
      window.setTimeout(() => setSaveToast(null), 2500);
    },
    [savedViews, focus, graph.focus_slug, transform, filters, selectedSlugs]
  );

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
        if (basketOpen) {
          setBasketOpen(false);
          return;
        }
        clearSelection();
        return;
      }
      if (event.key === "\\" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setInspectorOpen((open) => !open);
      }
      if (event.key.toLowerCase() === "b" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setBasketOpen((open) => !open);
      }
      if (event.key.toLowerCase() === "s" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setSaveModalOpen(true);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [clearSelection, basketOpen]);

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
            className="rounded-md border border-border px-2 py-1 text-xs text-ink hover:bg-surface-muted cursor-pointer"
            data-testid="canvas-save-view-button"
            onClick={() => setSaveModalOpen(true)}
          >
            Salva vista
          </button>
          <button
            type="button"
            className="rounded-md border border-border px-2 py-1 text-xs text-ink hover:bg-surface-muted cursor-pointer"
            data-testid="canvas-basket-badge"
            onClick={() => setBasketOpen(true)}
          >
            Basket {basketItems.length}
          </button>
          <button
            type="button"
            className="rounded-md border border-border px-2 py-1 text-xs text-ink-muted cursor-pointer"
            data-testid="canvas-minimap-toggle"
            onClick={() => setMinimapOpen((open) => !open)}
          >
            Minimap {minimapOpen ? "on" : "off"}
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

      {saveToast != null && (
        <p className="text-sm text-success" data-testid="canvas-save-toast">
          {saveToast}
        </p>
      )}

      {view != null && (
        <p className="text-sm text-ink-muted" data-testid="canvas-saved-view-notice">
          Vista salvata <span className="font-mono">{view}</span>
          {getCanvasSavedView(savedViews, view)?.name != null && (
            <>
              {" "}
              — {getCanvasSavedView(savedViews, view)?.name}
            </>
          )}
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

        <div className="relative min-w-0 flex-1" ref={canvasRegionRef}>
          {lensLoading && (
            <div
              className="pointer-events-none absolute inset-x-0 top-0 z-10 h-1 animate-pulse bg-accent/30"
              data-testid="canvas-lens-loading"
            />
          )}
          <ResearchCanvasViewport
            graph={displayGraph}
            selectedSlugs={selectedSlugs}
            onSelectedSlugsChange={setSelectedSlugs}
            transform={transform}
            onTransformChange={setTransform}
            highlightSlugs={highlightSlugs}
            highlightEdgeKeys={highlightEdgeKeys}
            panRequest={panRequest}
          />
          {minimapOpen && (
            <CanvasMinimap
              graph={displayGraph}
              transform={transform}
              viewportWidth={viewportSize.width}
              viewportHeight={viewportSize.height}
            />
          )}
        </div>

        {inspectorOpen && (
          <aside
            className={cn(
              "hidden w-[320px] shrink-0 border-l border-border bg-surface p-3 xl:block"
            )}
            data-testid="canvas-inspector-slot"
          >
            <ResearchInspectorRail
              selectedSlugs={selectedSlugs}
              graph={displayGraph}
              onAddToBasket={addSelectionToBasket}
            />
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
            disabled={selectedSlugs.length === 0}
            className={cn(
              "rounded-md border border-border px-3 py-1.5 text-sm",
              selectedSlugs.length === 0
                ? "text-ink-subtle"
                : "text-ink hover:bg-surface-muted cursor-pointer"
            )}
            data-testid="canvas-add-basket-button"
            onClick={() => addSelectionToBasket(selectedSlugs)}
          >
            Aggiungi al basket
          </button>
          <button
            type="button"
            disabled={basketItems.length === 0}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium",
              basketItems.length === 0
                ? "bg-accent/40 text-ink-subtle"
                : "bg-accent text-on-accent cursor-pointer"
            )}
            data-testid="canvas-writing-handoff-button"
            onClick={handleBasketHandoff}
          >
            Porta in Scrittura
          </button>
        </div>
      </footer>

      <ResearchBasketDrawer
        open={basketOpen}
        items={basketItems}
        onClose={() => setBasketOpen(false)}
        onRemove={(slug) => setBasketItems((current) => removeFromCanvasBasket(current, slug))}
        onHandoff={handleBasketHandoff}
      />
      <SaveViewModal
        open={saveModalOpen}
        onClose={() => setSaveModalOpen(false)}
        onSave={handleSaveView}
      />
      <CanvasHardLimitModal
        open={hardLimitBlocked}
        nodeCount={filteredGraph.nodes.length}
        hardLimit={filteredGraph.limits.hard_limit}
        activeLensId={filters.lensId}
        clusterMode={clusterMode}
        onChooseLens={(lensId) => setLensId(lensId)}
        onEnableCluster={() => setClusterMode(true)}
      />
    </div>
  );
}
