import { describe, expect, it } from "vitest";

import { resolveApiBase } from "@/lib/apiBase";

describe("resolveApiBase", () => {
  it("uses a dedicated same-origin API namespace in the browser", () => {
    expect(resolveApiBase(true)).toBe("/api");
  });

  it("returns internal backend URL on server", () => {
    expect(resolveApiBase(false)).toMatch(/^https?:\/\//);
  });
});
