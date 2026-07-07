import type {
  CanvasNodeKind,
  KnowledgeGraphNode,
  KnowledgeGraphResponse,
} from "@/lib/knowledgeTypes";

export const CANVAS_ZOOM_MIN = 0.25;
export const CANVAS_ZOOM_MAX = 4;

export type CanvasNodePosition = {
  slug: string;
  x: number;
  y: number;
};

const RING_RADIUS = 200;
const NODE_SPACING = 120;

/**
 * Radial layout from focus concept — product spec §5.1 initial layout.
 */
export function panTransformToSlugs(
  slugs: readonly string[],
  layout: Map<string, CanvasNodePosition>,
  viewportWidth: number,
  viewportHeight: number,
  scale: number
): { x: number; y: number } | null {
  const positions = slugs
    .map((slug) => layout.get(slug))
    .filter((position): position is CanvasNodePosition => position != null);
  if (positions.length === 0) return null;

  const centerX = positions.reduce((sum, position) => sum + position.x, 0) / positions.length;
  const centerY = positions.reduce((sum, position) => sum + position.y, 0) / positions.length;

  return {
    x: viewportWidth / 2 - centerX * scale,
    y: viewportHeight / 2 - centerY * scale,
  };
}

export function canvasNodeKind(node: KnowledgeGraphNode): CanvasNodeKind {
  return node.kind ?? "concept";
}

function layoutConceptNodes(
  graph: KnowledgeGraphResponse
): Map<string, CanvasNodePosition> {
  const positions = new Map<string, CanvasNodePosition>();
  const focusSlug = graph.focus_slug ?? graph.nodes[0]?.slug;
  if (focusSlug == null) return positions;

  positions.set(focusSlug, { slug: focusSlug, x: 0, y: 0 });

  const neighbors = graph.nodes.filter((node) => node.slug !== focusSlug);
  if (neighbors.length === 0) return positions;

  if (neighbors.length <= 8) {
    neighbors.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / neighbors.length - Math.PI / 2;
      positions.set(node.slug, {
        slug: node.slug,
        x: Math.cos(angle) * RING_RADIUS,
        y: Math.sin(angle) * RING_RADIUS,
      });
    });
    return positions;
  }

  const perRing = 8;
  let ring = 0;
  let placed = 0;

  while (placed < neighbors.length) {
    const countOnRing = Math.min(perRing + ring * 2, neighbors.length - placed);
    const radius = RING_RADIUS + ring * NODE_SPACING;
    for (let i = 0; i < countOnRing; i += 1) {
      const node = neighbors[placed];
      const angle = (2 * Math.PI * i) / countOnRing - Math.PI / 2;
      positions.set(node.slug, {
        slug: node.slug,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
      });
      placed += 1;
    }
    ring += 1;
  }

  return positions;
}

function satelliteOrbitRadius(kind: CanvasNodeKind): number {
  switch (kind) {
    case "source":
      return 72;
    case "author":
      return 96;
    case "decision":
      return 56;
    case "chapter":
      return 64;
    default:
      return 48;
  }
}

function parentSlugForSatellite(
  node: KnowledgeGraphNode,
  graph: KnowledgeGraphResponse
): string | null {
  for (const edge of graph.edges) {
    if (edge.target !== node.slug || edge.link_kind == null) continue;
    if (edge.link_kind === "author_source") continue;
    return edge.source;
  }
  if (node.kind === "author") {
    for (const edge of graph.edges) {
      if (edge.source === node.slug && edge.link_kind === "author_source") {
        for (const conceptEdge of graph.edges) {
          if (
            conceptEdge.target === edge.target &&
            conceptEdge.link_kind === "concept_source"
          ) {
            return conceptEdge.source;
          }
        }
      }
    }
  }
  return null;
}

/**
 * Radial layout from focus concept — product spec §5.1 initial layout.
 * Satellites orbit their parent concept (PX5-EWO-008).
 */
export function layoutCanvasNodes(
  graph: KnowledgeGraphResponse
): Map<string, CanvasNodePosition> {
  const conceptNodes = graph.nodes.filter((node) => canvasNodeKind(node) === "concept");
  const positions = layoutConceptNodes({
    ...graph,
    nodes: conceptNodes,
    edges: graph.edges.filter((edge) => edge.link_kind == null),
  });

  const satellites = graph.nodes.filter((node) => canvasNodeKind(node) !== "concept");
  const grouped = new Map<string, KnowledgeGraphNode[]>();
  for (const satellite of satellites) {
    const parent = parentSlugForSatellite(satellite, graph);
    if (parent == null) continue;
    const bucket = grouped.get(parent) ?? [];
    bucket.push(satellite);
    grouped.set(parent, bucket);
  }

  for (const [parent, items] of grouped) {
    const parentPos = positions.get(parent);
    if (parentPos == null) continue;
    items.forEach((satellite, index) => {
      const angle = (2 * Math.PI * index) / items.length - Math.PI / 2;
      const orbit = satelliteOrbitRadius(canvasNodeKind(satellite));
      positions.set(satellite.slug, {
        slug: satellite.slug,
        x: parentPos.x + Math.cos(angle) * orbit,
        y: parentPos.y + Math.sin(angle) * orbit,
      });
    });
  }

  return positions;
}

export function nodeRadius(node: KnowledgeGraphNode): number {
  switch (canvasNodeKind(node)) {
    case "source":
      return 20;
    case "author":
      return 14;
    case "decision":
      return 16;
    case "chapter":
      return 18;
    case "concept":
    default:
      return node.is_core ? 32 : 24;
  }
}

export function truncateLabel(title: string, max = 32): string {
  if (title.length <= max) return title;
  return `${title.slice(0, max - 1)}…`;
}

export type ViewportBounds = {
  left: number;
  top: number;
  right: number;
  bottom: number;
};

/** World-space bounds visible in the viewport (with margin for node size). */
export function visibleWorldBounds(
  width: number,
  height: number,
  transform: { x: number; y: number; scale: number },
  margin = 80
): ViewportBounds {
  return {
    left: (-transform.x - margin) / transform.scale,
    top: (-transform.y - margin) / transform.scale,
    right: (width - transform.x + margin) / transform.scale,
    bottom: (height - transform.y + margin) / transform.scale,
  };
}

export function isNodeVisible(
  x: number,
  y: number,
  radius: number,
  bounds: ViewportBounds
): boolean {
  return (
    x + radius >= bounds.left &&
    x - radius <= bounds.right &&
    y + radius >= bounds.top &&
    y - radius <= bounds.bottom
  );
}
