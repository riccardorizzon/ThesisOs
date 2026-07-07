import {
  DEFAULT_CANVAS_FILTERS,
  type CanvasFilterOptions,
  type CanvasLensId,
} from "@/lib/canvasLenses";
import type { CanvasTransform } from "@/lib/canvasTransform";

export const CANVAS_SAVED_VIEWS_KEY = "thesisos:canvas-saved-views";
export const CANVAS_LAST_VIEW_KEY = "thesisos:canvas-last-view-id";

export type CanvasSavedView = {
  id: string;
  name: string;
  description?: string;
  focus_slug?: string | null;
  camera: CanvasTransform;
  lens_id: CanvasLensId;
  filters: CanvasFilterOptions;
  selected_ids: string[];
  include_selection: boolean;
  updatedAt: string;
};

function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof localStorage !== "undefined";
}

export function loadCanvasSavedViews(): CanvasSavedView[] {
  if (!isBrowser()) return [];
  try {
    const raw = localStorage.getItem(CANVAS_SAVED_VIEWS_KEY);
    if (raw == null) return [];
    const parsed = JSON.parse(raw) as CanvasSavedView[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistViews(views: CanvasSavedView[]): void {
  if (!isBrowser()) return;
  localStorage.setItem(CANVAS_SAVED_VIEWS_KEY, JSON.stringify(views));
}

export function saveCanvasView(
  views: readonly CanvasSavedView[],
  draft: Omit<CanvasSavedView, "id" | "updatedAt">
): CanvasSavedView[] {
  const view: CanvasSavedView = {
    ...draft,
    id: `view-${Date.now()}`,
    updatedAt: new Date().toISOString(),
  };
  const next = [view, ...views].slice(0, 20);
  persistViews(next);
  if (isBrowser()) {
    localStorage.setItem(CANVAS_LAST_VIEW_KEY, view.id);
  }
  return next;
}

export function getCanvasSavedView(
  views: readonly CanvasSavedView[],
  id: string
): CanvasSavedView | undefined {
  return views.find((view) => view.id === id);
}

export function recentCanvasSavedViews(
  views: readonly CanvasSavedView[],
  limit = 3
): CanvasSavedView[] {
  return [...views]
    .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
    .slice(0, limit);
}

export function defaultSavedViewFilters(): CanvasFilterOptions {
  return { ...DEFAULT_CANVAS_FILTERS };
}
