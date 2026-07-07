"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { ResearchCanvasViewport } from "@/components/research/canvas/ResearchCanvasViewport";
import { selectionLabel } from "@/lib/canvasSelection";
import { DEFAULT_CANVAS_TRANSFORM, type CanvasTransform } from "@/lib/canvasTransform";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

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
 * PX-5 canvas shell — three-region layout + selection model (PX5-EWO-004).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasShell({ graph, focus, view }: ResearchCanvasShellProps) {
  const isDesktop = useDesktopCanvas();
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>(
    graph.focus_slug != null ? [graph.focus_slug] : []
  );
  const [transform, setTransform] = useState<CanvasTransform>(DEFAULT_CANVAS_TRANSFORM);

  const clearSelection = useCallback(() => {
    setSelectedSlugs([]);
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        clearSelection();
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

  const selectionSummary = selectionLabel(graph.nodes, selectedSlugs);

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
              disabled
              className="rounded-md border border-border bg-surface-muted px-2 py-1 text-xs text-ink-subtle"
              data-testid="canvas-lens-dropdown"
              aria-label="Lente (disponibile a breve)"
            >
              <option>Panorama</option>
            </select>
          </label>
          <button
            type="button"
            disabled
            className="rounded-md border border-border px-2 py-1 text-xs text-ink-subtle"
            data-testid="canvas-filters-button"
          >
            Filtri
          </button>
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
            {graph.limits.visible_count} / {graph.limits.total_in_scope} concetti
          </p>
        </div>
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
          <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">Lenti</p>
          <p className="mt-2 text-sm text-ink-muted">Disponibili nel prossimo aggiornamento.</p>
        </aside>

        <div className="min-w-0 flex-1">
          <ResearchCanvasViewport
            graph={graph}
            selectedSlugs={selectedSlugs}
            onSelectedSlugsChange={setSelectedSlugs}
            transform={transform}
            onTransformChange={setTransform}
          />
        </div>

        <aside
          className="hidden w-[320px] shrink-0 border-l border-border bg-surface p-3 xl:block"
          data-testid="canvas-inspector-slot"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
            Inspector
          </p>
          <p className="mt-2 text-sm text-ink-muted">
            Seleziona un nodo sulla mappa. Dettaglio completo nel prossimo aggiornamento.
          </p>
          {selectedSlugs.length > 0 && (
            <p className="mt-3 text-sm text-ink" data-testid="canvas-inspector-selection-preview">
              {selectionSummary}
            </p>
          )}
        </aside>
      </div>

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
