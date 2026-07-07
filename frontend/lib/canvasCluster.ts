import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type ClusterChip = {
  id: string;
  label: string;
  memberSlugs: string[];
  x: number;
  y: number;
};

export function exceedsHardLimit(
  graph: KnowledgeGraphResponse,
  clusterMode: boolean
): boolean {
  if (clusterMode) return false;
  return graph.nodes.length >= graph.limits.hard_limit;
}

export function buildClusterChips(
  graph: KnowledgeGraphResponse,
  layout: Map<string, { x: number; y: number }>
): ClusterChip[] {
  const concepts = graph.nodes.filter((node) => (node.kind ?? "concept") === "concept");
  if (concepts.length <= 12) return [];

  const distant = concepts
    .map((node) => {
      const pos = layout.get(node.slug);
      if (pos == null) return null;
      const distance = Math.hypot(pos.x, pos.y);
      return { node, pos, distance };
    })
    .filter((entry): entry is NonNullable<typeof entry> => entry != null)
    .sort((a, b) => b.distance - a.distance);

  const clusterMembers = distant.slice(0, Math.max(0, distant.length - 8));
  if (clusterMembers.length < 3) return [];

  const centroidX =
    clusterMembers.reduce((sum, entry) => sum + entry.pos.x, 0) / clusterMembers.length;
  const centroidY =
    clusterMembers.reduce((sum, entry) => sum + entry.pos.y, 0) / clusterMembers.length;

  return [
    {
      id: "cluster-distant",
      label: `${clusterMembers.length} nodi`,
      memberSlugs: clusterMembers.map((entry) => entry.node.slug),
      x: centroidX,
      y: centroidY,
    },
  ];
}

export function graphWithClusterCollapse(
  graph: KnowledgeGraphResponse,
  clusterMode: boolean,
  expandedClusterIds: ReadonlySet<string>,
  chips: readonly ClusterChip[]
): KnowledgeGraphResponse {
  if (!clusterMode || chips.length === 0) return graph;

  const collapsedSlugs = new Set<string>();
  for (const chip of chips) {
    if (expandedClusterIds.has(chip.id)) continue;
    for (const slug of chip.memberSlugs) {
      collapsedSlugs.add(slug);
    }
  }

  if (collapsedSlugs.size === 0) return graph;

  const nodes = graph.nodes.filter((node) => !collapsedSlugs.has(node.slug));
  const nodeSlugs = new Set(nodes.map((node) => node.slug));
  const edges = graph.edges.filter(
    (edge) => nodeSlugs.has(edge.source) && nodeSlugs.has(edge.target)
  );

  return {
    ...graph,
    nodes,
    edges,
    limits: {
      ...graph.limits,
      visible_count: nodes.length,
    },
  };
}
