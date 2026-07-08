import type { CanvasLensContext } from "@/lib/canvasLenses";
import { emptyLensContext } from "@/lib/canvasLenses";
import type { DecisionRef } from "@/lib/contextClient";
import { formatDecisionDisplayId } from "@/lib/decisionClient";
import type { KnowledgeGraphEdge, KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type SerendipitySuggestionType =
  | "bridge"
  | "unread-source"
  | "decision-tension"
  | "chapter-gap";

export type SerendipitySuggestion = {
  id: string;
  type: SerendipitySuggestionType;
  title: string;
  subtitle: string;
  actionLabel: string;
  targetSlugs: string[];
  targetEdgeKeys: string[];
  rank: number;
};

export type SerendipityContext = CanvasLensContext & {
  decisions: DecisionRef[];
  activeChapterLabel: string | null;
};

const MAX_SUGGESTIONS = 5;

const TYPE_RANK: Record<SerendipitySuggestionType, number> = {
  bridge: 1,
  "decision-tension": 2,
  "unread-source": 3,
  "chapter-gap": 4,
};

export function emptySerendipityContext(): SerendipityContext {
  return {
    ...emptyLensContext(),
    decisions: [],
    activeChapterLabel: null,
  };
}

function edgeKey(edge: KnowledgeGraphEdge): string {
  return `${edge.source}-${edge.target}-${edge.relation}`;
}

function nodeTitle(graph: KnowledgeGraphResponse, slug: string): string {
  return graph.nodes.find((node) => node.slug === slug)?.title ?? slug;
}

function neighborMap(graph: KnowledgeGraphResponse): Map<string, Set<string>> {
  const neighbors = new Map<string, Set<string>>();
  for (const node of graph.nodes) {
    neighbors.set(node.slug, new Set<string>());
  }
  for (const edge of graph.edges) {
    neighbors.get(edge.source)?.add(edge.target);
    neighbors.get(edge.target)?.add(edge.source);
  }
  return neighbors;
}

function hasDirectEdge(graph: KnowledgeGraphResponse, a: string, b: string): boolean {
  return graph.edges.some(
    (edge) =>
      (edge.source === a && edge.target === b) || (edge.source === b && edge.target === a)
  );
}

function findBridgeSuggestions(graph: KnowledgeGraphResponse): SerendipitySuggestion[] {
  const slugs = graph.nodes.map((node) => node.slug).sort();
  const neighbors = neighborMap(graph);
  const suggestions: SerendipitySuggestion[] = [];

  for (let i = 0; i < slugs.length; i += 1) {
    for (let j = i + 1; j < slugs.length; j += 1) {
      const a = slugs[i];
      const b = slugs[j];
      if (hasDirectEdge(graph, a, b)) continue;

      const na = neighbors.get(a) ?? new Set<string>();
      const nb = neighbors.get(b) ?? new Set<string>();
      const bridges = [...na].filter((slug) => nb.has(slug)).sort();
      if (bridges.length === 0) continue;

      const bridge = bridges[0];
      const edgeKeys = graph.edges
        .filter(
          (edge) =>
            (edge.source === a && edge.target === bridge) ||
            (edge.source === bridge && edge.target === a) ||
            (edge.source === b && edge.target === bridge) ||
            (edge.source === bridge && edge.target === b)
        )
        .map(edgeKey);

      suggestions.push({
        id: `bridge:${a}:${b}:${bridge}`,
        type: "bridge",
        title: "Ponte concetti",
        subtitle: `${nodeTitle(graph, a)} ↔ ${nodeTitle(graph, b)} via ${nodeTitle(graph, bridge)}`,
        actionLabel: "Mostra",
        targetSlugs: [a, b, bridge],
        targetEdgeKeys: edgeKeys,
        rank: TYPE_RANK.bridge,
      });
    }
  }

  return suggestions;
}

function findUnreadSourceSuggestions(
  graph: KnowledgeGraphResponse,
  context: SerendipityContext
): SerendipitySuggestion[] {
  const graphSlugs = new Set(graph.nodes.map((node) => node.slug));
  const suggestions: SerendipitySuggestion[] = [];

  const unreadSlugs = [...context.unreadSourceSlugs].sort();
  for (const sourceSlug of unreadSlugs) {
    const sourceNode = graph.nodes.find(
      (node) => node.slug === sourceSlug && node.kind === "source"
    );
    if (sourceNode == null) continue;

    const conceptSlugs = graph.edges
      .filter(
        (edge) =>
          edge.link_kind === "concept_source" &&
          edge.target === sourceSlug &&
          graphSlugs.has(edge.source)
      )
      .map((edge) => edge.source)
      .sort();
    if (conceptSlugs.length === 0) continue;

    suggestions.push({
      id: `unread:${sourceSlug}`,
      type: "unread-source",
      title: "Fonte non letta",
      subtitle: sourceNode.title,
      actionLabel: "Apri",
      targetSlugs: conceptSlugs.slice(0, 2),
      targetEdgeKeys: [],
      rank: TYPE_RANK["unread-source"],
    });
  }

  return suggestions;
}

function findDecisionTensionSuggestions(
  graph: KnowledgeGraphResponse,
  context: SerendipityContext
): SerendipitySuggestion[] {
  const controversial = new Set<string>();
  for (const edge of graph.edges) {
    if (edge.relation !== "contradicts") continue;
    controversial.add(edge.source);
    controversial.add(edge.target);
  }
  if (controversial.size === 0) return [];

  const binding = context.decisions
    .filter((decision) => decision.binding)
    .sort((a, b) => formatDecisionDisplayId(a).localeCompare(formatDecisionDisplayId(b)));

  const suggestions: SerendipitySuggestion[] = [];
  for (const decision of binding) {
    const conceptSlug = [...controversial].sort()[0];
    if (conceptSlug == null) continue;

    const displayId = formatDecisionDisplayId(decision);
    const edgeKeys = graph.edges
      .filter((edge) => edge.relation === "contradicts")
      .filter((edge) => edge.source === conceptSlug || edge.target === conceptSlug)
      .map(edgeKey);

    suggestions.push({
      id: `decision:${decision.id}:${conceptSlug}`,
      type: "decision-tension",
      title: "Tensione decisionale",
      subtitle: `${displayId} vs ${nodeTitle(graph, conceptSlug)}`,
      actionLabel: "Mostra",
      targetSlugs: [conceptSlug],
      targetEdgeKeys: edgeKeys,
      rank: TYPE_RANK["decision-tension"],
    });
    break;
  }

  return suggestions;
}

function findChapterGapSuggestions(
  graph: KnowledgeGraphResponse,
  context: SerendipityContext
): SerendipitySuggestion[] {
  if (context.activeChapterConceptSlugs.size === 0) return [];

  const gaps = graph.nodes
    .filter((node) => !context.activeChapterConceptSlugs.has(node.slug))
    .filter((node) => node.knowledge_state !== "deprecated")
    .sort((a, b) => a.slug.localeCompare(b.slug));

  if (gaps.length === 0) return [];

  const chapterLabel = context.activeChapterLabel ?? "capitolo attivo";
  return gaps.slice(0, 2).map((node) => ({
    id: `chapter-gap:${node.slug}`,
    type: "chapter-gap" as const,
    title: "Lacuna capitolo",
    subtitle: `${chapterLabel} non cita ${node.title}`,
    actionLabel: "Mostra",
    targetSlugs: [node.slug],
    targetEdgeKeys: [],
    rank: TYPE_RANK["chapter-gap"],
  }));
}

/**
 * Deterministic serendipity suggestions from graph topology + reading state (PX5-EWO-007).
 * Layer: Business (Product Plane)
 */
export function rankSerendipitySuggestions(
  graph: KnowledgeGraphResponse,
  context: SerendipityContext
): SerendipitySuggestion[] {
  const candidates = [
    ...findBridgeSuggestions(graph),
    ...findDecisionTensionSuggestions(graph, context),
    ...findUnreadSourceSuggestions(graph, context),
    ...findChapterGapSuggestions(graph, context),
  ];

  const seen = new Set<string>();
  const unique = candidates.filter((suggestion) => {
    if (seen.has(suggestion.id)) return false;
    seen.add(suggestion.id);
    return true;
  });

  return unique
    .sort((a, b) => {
      if (a.rank !== b.rank) return a.rank - b.rank;
      return a.id.localeCompare(b.id);
    })
    .slice(0, MAX_SUGGESTIONS);
}
