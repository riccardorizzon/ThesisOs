import { describe, expect, it } from "vitest";

import {
  rankSerendipitySuggestions,
  type SerendipityContext,
} from "@/lib/canvasSerendipity";
import { buildLensContextFromGraph } from "@/lib/canvasLenses";
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
    {
      id: "benjamin-opera-arte",
      slug: "benjamin-opera-arte",
      title: "L'opera d'arte nell'epoca della riproducibilità tecnica",
      knowledge_state: "linked",
      is_core: false,
      degree: 1,
      kind: "source",
    },
  ],
  edges: [
    { source: "aura", target: "riproducibilita", relation: "supports" },
    { source: "aura", target: "stigmata", relation: "contradicts" },
    { source: "mito", target: "stigmata", relation: "contradicts" },
    { source: "mito", target: "riproducibilita", relation: "related" },
    {
      source: "aura",
      target: "benjamin-opera-arte",
      relation: "related",
      link_kind: "concept_source",
    },
  ],
  limits: {
    default_visible: 80,
    soft_limit: 150,
    hard_limit: 300,
    visible_count: 5,
    total_in_scope: 5,
    truncated: false,
    force_list_view: false,
    show_performance_banner: false,
  },
};

const TEST_SERENDIPITY_CONTEXT: SerendipityContext = {
  ...buildLensContextFromGraph(SAMPLE_GRAPH),
  activeChapterConceptSlugs: new Set(["aura", "stigmata"]),
  unreadSourceSlugs: new Set(["benjamin-opera-arte"]),
  decisions: [
    {
      id: "dec-012",
      title: "DEC-012",
      summary: "DEC-012 — vincolo metodologico sul corpus visivo",
      binding: true,
    },
  ],
  activeChapterLabel: "Cap. 3",
};

describe("canvasSerendipity", () => {
  const context = TEST_SERENDIPITY_CONTEXT;

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
    const graph: KnowledgeGraphResponse = {
      schema_version: 1,
      focus_slug: "aura",
      depth: 1,
      view_mode: "graph",
      nodes: [
        {
          id: "aura",
          slug: "aura",
          title: "Aura",
          knowledge_state: "validated",
          is_core: true,
          degree: 1,
        },
        {
          id: "benjamin-opera-arte",
          slug: "benjamin-opera-arte",
          title: "L'opera d'arte nell'epoca della riproducibilità tecnica",
          knowledge_state: "linked",
          is_core: false,
          degree: 1,
          kind: "source",
        },
      ],
      edges: [
        {
          source: "aura",
          target: "benjamin-opera-arte",
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
    const context: SerendipityContext = {
      ...buildLensContextFromGraph(graph),
      unreadSourceSlugs: new Set(["benjamin-opera-arte"]),
      decisions: [],
      activeChapterLabel: null,
    };
    const suggestions = rankSerendipitySuggestions(graph, context);
    const unread = suggestions.find((item) => item.type === "unread-source");
    expect(unread).toBeDefined();
    expect(unread?.subtitle).toContain("opera d'arte");
  });

  it("includes chapter gap for concepts outside active chapter", () => {
    const graph: KnowledgeGraphResponse = {
      schema_version: 1,
      focus_slug: "aura",
      depth: 1,
      view_mode: "graph",
      nodes: [
        {
          id: "aura",
          slug: "aura",
          title: "Aura",
          knowledge_state: "validated",
          is_core: true,
          degree: 0,
        },
        {
          id: "mito",
          slug: "mito",
          title: "Mito",
          knowledge_state: "validated",
          is_core: false,
          degree: 0,
        },
      ],
      edges: [],
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
    const context: SerendipityContext = {
      ...buildLensContextFromGraph(graph),
      activeChapterConceptSlugs: new Set(["aura"]),
      decisions: [],
      activeChapterLabel: "Cap. 3",
    };
    const suggestions = rankSerendipitySuggestions(graph, context);
    const gap = suggestions.find((item) => item.type === "chapter-gap");
    expect(gap).toBeDefined();
    expect(gap?.subtitle).toContain("non cita");
  });
});
