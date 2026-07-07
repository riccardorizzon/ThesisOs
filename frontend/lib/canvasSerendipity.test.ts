import { describe, expect, it } from "vitest";

import {
  buildStubSerendipityContext,
  rankSerendipitySuggestions,
} from "@/lib/canvasSerendipity";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

const SAMPLE_GRAPH: KnowledgeGraphResponse = {
  schema_version: 1,
  focus_slug: "aura",
  depth: 2,
  view_mode: "graph",
  nodes: [
    {
      id: "aura",
      slug: "aura",
      title: "Aura",
      knowledge_state: "validated",
      is_core: true,
      degree: 2,
    },
    {
      id: "riproducibilita",
      slug: "riproducibilita",
      title: "Riproducibilità",
      knowledge_state: "linked",
      is_core: false,
      degree: 1,
    },
    {
      id: "stigmata",
      slug: "stigmata",
      title: "STIGMATA",
      knowledge_state: "referenced",
      is_core: false,
      degree: 3,
    },
    {
      id: "mito",
      slug: "mito",
      title: "Mito",
      knowledge_state: "validated",
      is_core: false,
      degree: 1,
    },
  ],
  edges: [
    { source: "aura", target: "riproducibilita", relation: "supports" },
    { source: "aura", target: "stigmata", relation: "contradicts" },
    { source: "mito", target: "stigmata", relation: "contradicts" },
    { source: "mito", target: "riproducibilita", relation: "related" },
  ],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 4,
    total_in_scope: 4,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

describe("canvasSerendipity", () => {
  const context = buildStubSerendipityContext();

  it("returns at most five deterministic suggestions", () => {
    const first = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    const second = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    expect(first.length).toBeLessThanOrEqual(5);
    expect(first).toEqual(second);
  });

  it("includes bridge suggestions from edge topology", () => {
    const suggestions = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    const bridge = suggestions.find((item) => item.type === "bridge");
    expect(bridge).toBeDefined();
    expect(bridge?.targetSlugs.length).toBeGreaterThanOrEqual(2);
    expect(bridge?.targetEdgeKeys.length).toBeGreaterThan(0);
  });

  it("includes decision tension from contradicts edges", () => {
    const suggestions = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    const tension = suggestions.find((item) => item.type === "decision-tension");
    expect(tension).toBeDefined();
    expect(tension?.subtitle).toContain("DEC-012");
  });

  it("includes unread source suggestion from reading state", () => {
    const suggestions = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    const unread = suggestions.find((item) => item.type === "unread-source");
    expect(unread).toBeDefined();
    expect(unread?.subtitle).toContain("Benjamin");
  });

  it("includes chapter gap for concepts outside active chapter", () => {
    const suggestions = rankSerendipitySuggestions(SAMPLE_GRAPH, context);
    const gap = suggestions.find((item) => item.type === "chapter-gap");
    expect(gap).toBeDefined();
    expect(gap?.subtitle).toContain("non cita");
  });
});
