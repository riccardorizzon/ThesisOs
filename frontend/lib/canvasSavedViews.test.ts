import { describe, expect, it, beforeEach } from "vitest";

import { DEFAULT_CANVAS_TRANSFORM } from "@/lib/canvasTransform";
import {
  defaultSavedViewFilters,
  loadCanvasSavedViews,
  recentCanvasSavedViews,
  saveCanvasView,
} from "@/lib/canvasSavedViews";

describe("canvasSavedViews", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("saves and loads views", () => {
    const views = saveCanvasView([], {
      name: "Panorama STIGMATA",
      focus_slug: "stigmata",
      camera: DEFAULT_CANVAS_TRANSFORM,
      lens_id: "L-all",
      filters: defaultSavedViewFilters(),
      selected_ids: [],
      include_selection: false,
    });
    expect(views).toHaveLength(1);
    expect(loadCanvasSavedViews()).toHaveLength(1);
  });

  it("returns recent views sorted by updatedAt", () => {
    const first = saveCanvasView([], {
      name: "A",
      camera: DEFAULT_CANVAS_TRANSFORM,
      lens_id: "L-all",
      filters: defaultSavedViewFilters(),
      selected_ids: [],
      include_selection: false,
    });
    const second = saveCanvasView(first, {
      name: "B",
      camera: DEFAULT_CANVAS_TRANSFORM,
      lens_id: "L-gap",
      filters: defaultSavedViewFilters(),
      selected_ids: [],
      include_selection: false,
    });
    const recent = recentCanvasSavedViews(second, 1);
    expect(recent[0]?.name).toBe("B");
  });
});
