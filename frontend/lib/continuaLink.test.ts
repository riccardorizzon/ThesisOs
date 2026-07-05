import { describe, expect, it, beforeEach, afterEach } from "vitest";

import { buildContinuaLink, mergeContinuaTarget } from "./continuaLink";
import { SESSION_STATE_STORAGE_KEY } from "./sessionState";

describe("buildContinuaLink", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  const fallback = { href: "/writing/2", label: "Cap. 2 — Quadro teorico" };

  it("returns fallback when no session persisted", () => {
    expect(buildContinuaLink({ fallback })).toEqual(fallback);
  });

  it("builds deep link from last session state", () => {
    localStorage.setItem(
      SESSION_STATE_STORAGE_KEY,
      JSON.stringify({
        chapterId: "cap-03",
        chapterTitle: "Cap. 3 — Metodologia",
        section: "3.2",
        source: "src-benjamin",
        panel: "fonte",
        updatedAt: new Date().toISOString(),
      })
    );

    expect(buildContinuaLink({ fallback })).toEqual({
      href: "/writing/cap-03?section=3.2&source=src-benjamin&panel=fonte#section-3-2",
      label: "Cap. 3 — Metodologia · §3.2",
    });
  });

  it("mergeContinuaTarget wraps chapter fallback", () => {
    localStorage.setItem(
      SESSION_STATE_STORAGE_KEY,
      JSON.stringify({
        chapterId: "3",
        chapterTitle: "Cap. 3",
        updatedAt: new Date().toISOString(),
      })
    );
    expect(mergeContinuaTarget(fallback).href).toBe("/writing/3");
  });
});
