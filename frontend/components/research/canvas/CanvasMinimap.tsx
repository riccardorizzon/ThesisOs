"use client";

import { useMemo } from "react";

import { layoutCanvasNodes, visibleWorldBounds } from "@/lib/canvasLayout";
import type { CanvasTransform } from "@/lib/canvasTransform";
import type { KnowledgeGraphResponse } from "@/lib/knowledgeTypes";

export type CanvasMinimapProps = {
  graph: KnowledgeGraphResponse;
  transform: CanvasTransform;
  viewportWidth: number;
  viewportHeight: number;
};

function boundsForLayout(layout: Map<string, { x: number; y: number }>) {
  const positions = [...layout.values()];
  if (positions.length === 0) {
    return { minX: -100, maxX: 100, minY: -100, maxY: 100 };
  }
  const xs = positions.map((pos) => pos.x);
  const ys = positions.map((pos) => pos.y);
  return {
    minX: Math.min(...xs) - 80,
    maxX: Math.max(...xs) + 80,
    minY: Math.min(...ys) - 80,
    maxY: Math.max(...ys) + 80,
  };
}

/**
 * Optional minimap with viewport rectangle (PX5-EWO-011).
 */
export function CanvasMinimap({
  graph,
  transform,
  viewportWidth,
  viewportHeight,
}: CanvasMinimapProps) {
  const layout = useMemo(() => layoutCanvasNodes(graph), [graph]);
  const world = useMemo(() => boundsForLayout(layout), [layout]);
  const width = 140;
  const height = 96;
  const scaleX = width / (world.maxX - world.minX);
  const scaleY = height / (world.maxY - world.minY);
  const scale = Math.min(scaleX, scaleY);

  const toMini = (x: number, y: number) => ({
    x: (x - world.minX) * scale,
    y: (y - world.minY) * scale,
  });

  const viewport = visibleWorldBounds(viewportWidth, viewportHeight, transform, 0);
  const topLeft = toMini(viewport.left, viewport.top);
  const bottomRight = toMini(viewport.right, viewport.bottom);
  const rectX = topLeft.x;
  const rectY = topLeft.y;
  const rectW = Math.max(8, bottomRight.x - topLeft.x);
  const rectH = Math.max(8, bottomRight.y - topLeft.y);

  return (
    <div
      className="pointer-events-none absolute bottom-3 left-3 rounded-md border border-border bg-surface/90 p-1 shadow-sm"
      data-testid="canvas-minimap"
      aria-hidden
    >
      <svg width={width} height={height}>
        {graph.nodes.map((node) => {
          const pos = layout.get(node.slug);
          if (pos == null) return null;
          const mini = toMini(pos.x, pos.y);
          return (
            <circle
              key={node.slug}
              cx={mini.x}
              cy={mini.y}
              r={node.kind === "concept" || node.kind == null ? 2.5 : 1.5}
              className="fill-accent/70"
            />
          );
        })}
        <rect
          x={rectX}
          y={rectY}
          width={rectW}
          height={rectH}
          className="fill-none stroke-accent stroke-[1.5px]"
          data-testid="canvas-minimap-viewport"
        />
      </svg>
    </div>
  );
}
