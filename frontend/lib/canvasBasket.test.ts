import { describe, expect, it, beforeEach } from "vitest";

import {
  addToCanvasBasket,
  CANVAS_BASKET_HANDOFF_KEY,
  CANVAS_BASKET_STORAGE_KEY,
  consumeCanvasBasketHandoff,
  loadCanvasBasket,
  stageCanvasBasketHandoff,
} from "@/lib/canvasBasket";
import { projectStorageKey } from "@/lib/projectScope";

describe("canvasBasket", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("adds items without duplicates", () => {
    const next = addToCanvasBasket([], [
      { slug: "aura", title: "Aura", kind: "concept" },
      { slug: "aura", title: "Aura", kind: "concept" },
    ]);
    expect(next).toHaveLength(1);
    expect(loadCanvasBasket()).toHaveLength(1);
  });

  it("stages and consumes handoff payload", () => {
    stageCanvasBasketHandoff([{ slug: "aura", title: "Aura", kind: "concept" }]);
    expect(
      sessionStorage.getItem(projectStorageKey(CANVAS_BASKET_HANDOFF_KEY))
    ).not.toBeNull();
    const items = consumeCanvasBasketHandoff();
    expect(items).toHaveLength(1);
    expect(consumeCanvasBasketHandoff()).toHaveLength(0);
  });

  it("persists basket in session storage", () => {
    addToCanvasBasket([], [{ slug: "stigmata", title: "STIGMATA", kind: "concept" }]);
    expect(
      sessionStorage.getItem(projectStorageKey(CANVAS_BASKET_STORAGE_KEY))
    ).toContain("stigmata");
  });
});
