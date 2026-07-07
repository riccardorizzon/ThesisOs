import { describe, expect, it } from "vitest";

import { canvasNodeKind, layoutCanvasNodes } from "@/lib/canvasLayout";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

const SAMPLE_GRAPH: KnowledgeGraphResponse = {
  schema_version: 1,
  focus_slug: "stigmata",
  depth: 2,
  view_mode: "graph",
  nodes: [
    {
      id: "stigmata",
      slug: "stigmata",
      title: "STIGMATA",
      knowledge_state: "linked",
      is_core: true,
      degree: 2,
      kind: "concept",
    },
    {
      id: "barthes-mythologies",
      slug: "barthes-mythologies",
      title: "Mythologies",
      knowledge_state: "linked",
      is_core: false,
      degree: 1,
      kind: "source",
    },
  ],
  edges: [
    {
      source: "stigmata",
      target: "barthes-mythologies",
      relation: "related",
      link_kind: "concept_source",
    },
  ],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 2,
    total_in_scope: 2,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

describe("layoutCanvasNodes satellites", () => {
  it("positions satellites near parent concept", () => {
    const layout = layoutCanvasNodes(SAMPLE_GRAPH);
    const concept = layout.get("stigmata");
    const source = layout.get("barthes-mythologies");
    expect(concept).toBeDefined();
    expect(source).toBeDefined();
    if (concept == null || source == null) return;

    const dx = source.x - concept.x;
    const dy = source.y - concept.y;
    const distance = Math.hypot(dx, dy);
    expect(distance).toBeGreaterThan(40);
    expect(distance).toBeLessThan(120);
  });

  it("defaults unknown kind to concept", () => {
    const node = SAMPLE_GRAPH.nodes[0];
    expect(canvasNodeKind(node)).toBe("concept");
  });
});
