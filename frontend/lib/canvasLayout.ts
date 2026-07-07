import type { KnowledgeGraphNode, KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

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
export function layoutCanvasNodes(
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

export function nodeRadius(node: KnowledgeGraphNode): number {
  return node.is_core ? 32 : 24;
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
