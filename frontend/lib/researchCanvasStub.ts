import { LIBRARY_CONCEPTS } from "@/lib/libraryStub";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

/**
 * Dev fallback when Knowledge graph API is unavailable.
 * Layer: Business (Product Plane)
 */
export function buildStubResearchGraph(focus?: string): KnowledgeGraphResponse {
  const focusSlug = focus ?? "stigmata";
  const nodes = LIBRARY_CONCEPTS.slice(0, 8).map((concept, index) => ({
    id: concept.id,
    slug: concept.id,
    title: concept.title,
    knowledge_state: "validated" as const,
    is_core: index === 0,
    degree: concept.relatedSourceIds.length,
  }));

  const edges: KnowledgeGraphResponse["edges"] = [];
  for (let i = 1; i < nodes.length; i += 1) {
    edges.push({
      source: nodes[0].slug,
      target: nodes[i].slug,
      relation: i % 3 === 0 ? "contradicts" : i % 2 === 0 ? "supports" : "related",
    });
  }
  if (nodes.length > 3) {
    edges.push({ source: nodes[1].slug, target: nodes[2].slug, relation: "extends" });
  }

  return {
    schema_version: 1,
    focus_slug: focusSlug,
    depth: 2,
    view_mode: "graph",
    nodes,
    edges,
    limits: {
      default_visible: 80,
      soft_limit: 150,
      hard_limit: 300,
      visible_count: nodes.length,
      total_in_scope: LIBRARY_CONCEPTS.length,
      truncated: false,
      force_list_view: false,
      show_performance_banner: false,
    },
  };
}
