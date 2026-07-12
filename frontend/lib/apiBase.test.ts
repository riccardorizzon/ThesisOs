import { describe, expect, it } from "vitest";

import { resolveApiBase } from "@/lib/apiBase";

describe("resolveApiBase", () => {
  it("returns empty string in browser for same-origin API", () => {
    expect(resolveApiBase(true)).toBe("");
  });

  it("returns internal backend URL on server", () => {
    expect(resolveApiBase(false)).toMatch(/^https?:\/\//);
  });
});
