import { layoutCanvasNodes, nodeRadius } from "@/lib/canvasLayout";
import type { CanvasTransform } from "@/lib/canvasTransform";
import type { KnowledgeGraphNode, KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type ScreenRect = {
  left: number;
  top: number;
  width: number;
  height: number;
};

export function screenToWorld(
  screenX: number,
  screenY: number,
  containerRect: DOMRect,
  transform: CanvasTransform
): { x: number; y: number } {
  const localX = screenX - containerRect.left;
  const localY = screenY - containerRect.top;
  return {
    x: (localX - transform.x) / transform.scale,
    y: (localY - transform.y) / transform.scale,
  };
}

export function normalizeScreenRect(
  startX: number,
  startY: number,
  endX: number,
  endY: number,
  containerRect: DOMRect
): ScreenRect {
  const left = Math.min(startX, endX) - containerRect.left;
  const top = Math.min(startY, endY) - containerRect.top;
  return {
    left,
    top,
    width: Math.abs(endX - startX),
    height: Math.abs(endY - startY),
  };
}

export function slugsInMarquee(
  graph: KnowledgeGraphResponse,
  containerRect: DOMRect,
  transform: CanvasTransform,
  startX: number,
  startY: number,
  endX: number,
  endY: number
): string[] {
  const marquee = normalizeScreenRect(startX, startY, endX, endY, containerRect);
  if (marquee.width < 4 && marquee.height < 4) {
    return [];
  }

  const layout = layoutCanvasNodes(graph);
  const selected: string[] = [];

  for (const node of graph.nodes) {
    const pos = layout.get(node.slug);
    if (pos == null) continue;
    const radius = nodeRadius(node);
    const screenX = pos.x * transform.scale + transform.x;
    const screenY = pos.y * transform.scale + transform.y;
    const nodeLeft = screenX - radius;
    const nodeRight = screenX + radius;
    const nodeTop = screenY - radius;
    const nodeBottom = screenY + radius;
    const marqueeRight = marquee.left + marquee.width;
    const marqueeBottom = marquee.top + marquee.height;

    const intersects =
      nodeRight >= marquee.left &&
      nodeLeft <= marqueeRight &&
      nodeBottom >= marquee.top &&
      nodeTop <= marqueeBottom;

    if (intersects) {
      selected.push(node.slug);
    }
  }

  return selected;
}

export function applyNodeSelection(
  current: readonly string[],
  slug: string,
  additive: boolean
): string[] {
  if (additive) {
    const set = new Set(current);
    if (set.has(slug)) {
      set.delete(slug);
    } else {
      set.add(slug);
    }
    return [...set];
  }
  return [slug];
}

export function selectionLabel(nodes: KnowledgeGraphNode[], slugs: readonly string[]): string {
  if (slugs.length === 0) return "Nessuna selezione";
  if (slugs.length === 1) {
    const node = nodes.find((item) => item.slug === slugs[0]);
    return node?.title ?? slugs[0];
  }
  return `${slugs.length} nodi selezionati`;
}
