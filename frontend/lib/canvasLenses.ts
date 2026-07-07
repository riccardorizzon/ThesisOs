import { LIBRARY_CONCEPTS, LIBRARY_SOURCES } from "@/lib/libraryStub";
import type {
  KnowledgeGraphEdge,
  KnowledgeGraphNode,
  KnowledgeGraphResponse,
  KnowledgeState,
} from "@/lib/knowledgeTypes";

export type CanvasLensId =
  | "L-all"
  | "L-gap"
  | "L-chapter"
  | "L-author"
  | "L-controversy"
  | "L-unread";

export type CanvasLensDefinition = {
  id: CanvasLensId;
  label: string;
  description: string;
};

export const CANVAS_LENSES: CanvasLensDefinition[] = [
  { id: "L-all", label: "Panorama", description: "Core + vicinato a 2 hop" },
  { id: "L-gap", label: "Lacune", description: "Concetti con meno di 2 fonti" },
  { id: "L-chapter", label: "Capitolo attivo", description: "Concetti del capitolo in scrittura" },
  { id: "L-author", label: "Autore", description: "Sottografo attorno all'autore selezionato" },
  { id: "L-controversy", label: "Controversie", description: "Nodi con edge contradicts" },
  { id: "L-unread", label: "Non letti", description: "Fonti senza annotazioni" },
];

export type CanvasFilterOptions = {
  lensId: CanvasLensId;
  hideDeprecated: boolean;
  coreOnly: boolean;
  knowledgeStates: KnowledgeState[] | "all";
  relationTypes: KnowledgeGraphEdge["relation"][] | "all";
};

export const DEFAULT_CANVAS_FILTERS: CanvasFilterOptions = {
  lensId: "L-all",
  hideDeprecated: true,
  coreOnly: false,
  knowledgeStates: "all",
  relationTypes: "all",
};

export type CanvasLensContext = {
  sourceCountByConceptSlug: Map<string, number>;
  activeChapterConceptSlugs: Set<string>;
  selectedAuthor: string | null;
  unreadSourceSlugs: Set<string>;
  conceptSlugsByAuthor: Map<string, Set<string>>;
};

/** Dev/catalog fallback when API enrichment is unavailable (PX5-EWO-006). */
export function buildStubLensContext(): CanvasLensContext {
  const sourceCountByConceptSlug = new Map<string, number>();
  for (const concept of LIBRARY_CONCEPTS) {
    sourceCountByConceptSlug.set(concept.id, concept.relatedSourceIds.length);
  }

  const conceptSlugsByAuthor = new Map<string, Set<string>>();
  for (const source of LIBRARY_SOURCES) {
    const author = source.subtitle?.trim();
    if (author == null || author.length === 0) continue;
    const bucket = conceptSlugsByAuthor.get(author) ?? new Set<string>();
    for (const conceptId of source.relatedConceptIds) {
      bucket.add(conceptId);
    }
    conceptSlugsByAuthor.set(author, bucket);
  }

  return {
    sourceCountByConceptSlug,
    activeChapterConceptSlugs: new Set(["aura", "stigmata"]),
    selectedAuthor: "Walter Benjamin",
    unreadSourceSlugs: new Set(["benjamin-opera-arte"]),
    conceptSlugsByAuthor,
  };
}

export function mergeSourceCounts(
  base: Map<string, number>,
  envelopes: Array<{ slug: string; linked_counts: { sources: number } }>
): Map<string, number> {
  const merged = new Map(base);
  for (const envelope of envelopes) {
    merged.set(envelope.slug, envelope.linked_counts.sources);
  }
  return merged;
}

function isConceptNode(node: KnowledgeGraphNode): boolean {
  return (node.kind ?? "concept") === "concept";
}

function expandWithSatellites(
  graph: KnowledgeGraphResponse,
  conceptSlugs: Set<string>
): Set<string> {
  const expanded = new Set(conceptSlugs);
  for (const node of graph.nodes) {
    if (isConceptNode(node)) continue;
    for (const edge of graph.edges) {
      if (edge.target !== node.slug || edge.link_kind == null) continue;
      if (edge.link_kind === "author_source") continue;
      if (conceptSlugs.has(edge.source)) {
        expanded.add(node.slug);
      }
    }
  }
  return expanded;
}

function slugsForLens(
  graph: KnowledgeGraphResponse,
  lensId: CanvasLensId,
  context: CanvasLensContext
): Set<string> {
  const concepts = graph.nodes.filter(isConceptNode);
  const all = new Set(concepts.map((node) => node.slug));

  switch (lensId) {
    case "L-all":
      return expandWithSatellites(graph, all);
    case "L-gap":
      return expandWithSatellites(
        graph,
        new Set(
          concepts
            .filter((node) => (context.sourceCountByConceptSlug.get(node.slug) ?? 0) < 2)
            .map((node) => node.slug)
        )
      );
    case "L-chapter":
      if (context.activeChapterConceptSlugs.size === 0) {
        return new Set<string>();
      }
      return expandWithSatellites(
        graph,
        new Set(
          concepts
            .filter((node) => context.activeChapterConceptSlugs.has(node.slug))
            .map((node) => node.slug)
        )
      );
    case "L-author": {
      if (context.selectedAuthor == null) return new Set<string>();
      const seeds = context.conceptSlugsByAuthor.get(context.selectedAuthor) ?? new Set<string>();
      const expanded = new Set<string>();
      for (const slug of seeds) {
        if (!all.has(slug)) continue;
        expanded.add(slug);
        for (const edge of graph.edges) {
          if (edge.source === slug && all.has(edge.target)) expanded.add(edge.target);
          if (edge.target === slug && all.has(edge.source)) expanded.add(edge.source);
        }
      }
      return expandWithSatellites(graph, expanded);
    }
    case "L-controversy": {
      const slugs = new Set<string>();
      for (const edge of graph.edges) {
        if (edge.link_kind != null || edge.relation !== "contradicts") continue;
        slugs.add(edge.source);
        slugs.add(edge.target);
      }
      return expandWithSatellites(graph, slugs);
    }
    case "L-unread": {
      const slugs = new Set<string>();
      for (const sourceSlug of context.unreadSourceSlugs) {
        const source = LIBRARY_SOURCES.find((item) => item.id === sourceSlug);
        if (source == null) continue;
        for (const conceptId of source.relatedConceptIds) {
          if (all.has(conceptId)) slugs.add(conceptId);
        }
      }
      return expandWithSatellites(graph, slugs);
    }
    default:
      return expandWithSatellites(graph, all);
  }
}

export function filterGraphByLens(
  graph: KnowledgeGraphResponse,
  filters: CanvasFilterOptions,
  context: CanvasLensContext
): KnowledgeGraphResponse {
  let allowed = slugsForLens(graph, filters.lensId, context);

  const nodes = graph.nodes.filter((node) => {
    if (!allowed.has(node.slug)) return false;
    if (filters.hideDeprecated && node.knowledge_state === "deprecated") return false;
    if (filters.coreOnly && !node.is_core) return false;
    if (
      filters.knowledgeStates !== "all" &&
      !filters.knowledgeStates.includes(node.knowledge_state)
    ) {
      return false;
    }
    return true;
  });

  const nodeSlugs = new Set(nodes.map((node) => node.slug));
  const edges = graph.edges.filter((edge) => {
    if (!nodeSlugs.has(edge.source) || !nodeSlugs.has(edge.target)) return false;
    if (edge.link_kind != null) return true;
    if (filters.relationTypes !== "all" && !filters.relationTypes.includes(edge.relation)) {
      return false;
    }
    return true;
  });

  const visibleCount = nodes.length;
  return {
    ...graph,
    nodes,
    edges,
    limits: {
      ...graph.limits,
      visible_count: visibleCount,
      show_performance_banner: visibleCount > graph.limits.soft_limit,
    },
  };
}

export function lensLabel(lensId: CanvasLensId): string {
  return CANVAS_LENSES.find((lens) => lens.id === lensId)?.label ?? lensId;
}
