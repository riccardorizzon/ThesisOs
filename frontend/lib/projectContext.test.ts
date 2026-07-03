import { describe, expect, it } from "vitest";

import {
  DEFAULT_PRODUCT_ID,
  DEFAULT_PROJECT_ID,
  defaultProjectContext,
  projectContextToQuery,
  resolveProjectContext,
  resolveProjectContextForSurface,
} from "@/lib/projectContext";

describe("defaultProjectContext", () => {
  it("returns thesis-agent / thesisos defaults", () => {
    expect(defaultProjectContext()).toEqual({
      project_id: DEFAULT_PROJECT_ID,
      product_id: DEFAULT_PRODUCT_ID,
    });
  });
});

describe("resolveProjectContext", () => {
  it("applies defaults when options omitted", () => {
    expect(resolveProjectContext()).toMatchObject(defaultProjectContext());
  });

  it("passes through workspace and session ids", () => {
    expect(
      resolveProjectContext({
        workspaceId: "ws-1",
        sessionId: "sess-1",
      })
    ).toEqual({
      project_id: DEFAULT_PROJECT_ID,
      product_id: DEFAULT_PRODUCT_ID,
      workspace_id: "ws-1",
      session_id: "sess-1",
    });
  });
});

describe("resolveProjectContextForSurface", () => {
  it("tags home surface", () => {
    expect(resolveProjectContextForSurface("home").surface).toBe("home");
  });

  it("tags writing surface", () => {
    expect(resolveProjectContextForSurface("writing").surface).toBe("writing");
  });
});

describe("projectContextToQuery", () => {
  it("maps scope to API query fields", () => {
    const ctx = resolveProjectContext({
      workspaceId: "ws-1",
      sessionId: "sess-1",
    });
    expect(
      projectContextToQuery(ctx, {
        surface: "writing",
        entityType: "chapter",
        entityId: "ch-2",
      })
    ).toEqual({
      surface: "writing",
      entityType: "chapter",
      entityId: "ch-2",
      productId: DEFAULT_PRODUCT_ID,
      workspaceId: "ws-1",
      sessionId: "sess-1",
    });
  });
});
