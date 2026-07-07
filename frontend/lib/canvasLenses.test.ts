import { describe, expect, it } from "vitest";

import {
  buildStubLensContext,
  DEFAULT_CANVAS_FILTERS,
  filterGraphByLens,
} from "@/lib/canvasLenses";
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
      knowledge_state: "deprecated",
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

describe("canvasLenses", () => {
  const context = buildStubLensContext();

  it("L-all returns all non-deprecated nodes by default", () => {
    const result = filterGraphByLens(SAMPLE_GRAPH, DEFAULT_CANVAS_FILTERS, context);
    expect(result.nodes.map((node) => node.slug)).toEqual(["aura", "riproducibilita", "mito"]);
  });

  it("L-controversy keeps nodes incident to contradicts edges", () => {
    const result = filterGraphByLens(
      SAMPLE_GRAPH,
      { ...DEFAULT_CANVAS_FILTERS, lensId: "L-controversy", hideDeprecated: false },
      context
    );
    expect(result.nodes.map((node) => node.slug).sort()).toEqual(["aura", "mito", "stigmata"]);
  });

  it("L-gap filters concepts with fewer than two sources", () => {
    const result = filterGraphByLens(
      SAMPLE_GRAPH,
      { ...DEFAULT_CANVAS_FILTERS, lensId: "L-gap" },
      context
    );
    expect(result.nodes.map((node) => node.slug)).toEqual(["aura", "riproducibilita", "mito"]);
  });

  it("popover filters compose with AND semantics", () => {
    const result = filterGraphByLens(
      SAMPLE_GRAPH,
      {
        ...DEFAULT_CANVAS_FILTERS,
        coreOnly: true,
        relationTypes: ["supports"],
      },
      context
    );
    expect(result.nodes.map((node) => node.slug)).toEqual(["aura"]);
    expect(result.edges).toHaveLength(0);
  });
});
