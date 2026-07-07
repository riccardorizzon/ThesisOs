import { describe, expect, it } from "vitest";

import { applyNodeSelection } from "@/lib/canvasSelection";

describe("canvasSelection", () => {
  it("replaces selection on single select", () => {
    expect(applyNodeSelection(["aura"], "stigmata", false)).toEqual(["stigmata"]);
  });

  it("toggles slug on additive select", () => {
    expect(applyNodeSelection(["aura"], "stigmata", true)).toEqual(["aura", "stigmata"]);
    expect(applyNodeSelection(["aura", "stigmata"], "aura", true)).toEqual(["stigmata"]);
  });
});
