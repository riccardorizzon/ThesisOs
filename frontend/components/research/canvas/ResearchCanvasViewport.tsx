"use client";

import { useRouter } from "next/navigation";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type WheelEvent as ReactWheelEvent,
} from "react";

import { KnowledgeLifecycleBadge } from "@/components/knowledge/shared/KnowledgeBadges";
import {
  CANVAS_ZOOM_MAX,
  CANVAS_ZOOM_MIN,
  isNodeVisible,
  layoutCanvasNodes,
  nodeRadius,
  truncateLabel,
  visibleWorldBounds,
} from "@/lib/canvasLayout";
import { cn } from "@/lib/cn";
import type { KnowledgeGraphEdge, KnowledgeGraphResponse, KnowledgeState } from "@/lib/knowledgeTypes";

const EDGE_STROKE: Record<KnowledgeGraphEdge["relation"], string> = {
  supports: "#16a34a",
  contradicts: "#ca8a04",
  extends: "#2563eb",
  related: "#94a3b8",
};

export type ResearchCanvasViewportProps = {
  graph: KnowledgeGraphResponse;
};

function edgeKey(edge: KnowledgeGraphEdge): string {
  return `${edge.source}-${edge.target}-${edge.relation}`;
}

/**
 * PX-5 spatial canvas — pan/zoom viewport with concept node layer (PX5-EWO-003).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasViewport({ graph }: ResearchCanvasViewportProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const [size, setSize] = useState({ width: 800, height: 560 });
  const [transform, setTransform] = useState({ x: 400, y: 280, scale: 1 });
  const [selectedSlug, setSelectedSlug] = useState<string | null>(
    graph.focus_slug ?? null
  );
  const panRef = useRef<{ active: boolean; startX: number; startY: number; tx: number; ty: number }>({
    active: false,
    startX: 0,
    startY: 0,
    tx: 0,
    ty: 0,
  });

  const layout = useMemo(() => layoutCanvasNodes(graph), [graph]);
  const titleBySlug = useMemo(() => {
    const map = new Map<string, string>();
    for (const node of graph.nodes) {
      map.set(node.slug, node.title);
    }
    return map;
  }, [graph.nodes]);

  useEffect(() => {
    const element = containerRef.current;
    if (element == null) return;

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry == null) return;
      setSize({
        width: entry.contentRect.width,
        height: entry.contentRect.height,
      });
    });
    observer.observe(element);
    setSize({
      width: element.clientWidth || 800,
      height: element.clientHeight || 560,
    });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const focusSlug = graph.focus_slug;
    if (focusSlug == null) return;
    const pos = layout.get(focusSlug);
    if (pos == null) return;
    setTransform({
      x: size.width / 2 - pos.x,
      y: size.height / 2 - pos.y,
      scale: 1,
    });
    setSelectedSlug(focusSlug);
  }, [graph.focus_slug, layout, size.width, size.height]);

  const bounds = useMemo(
    () => visibleWorldBounds(size.width, size.height, transform),
    [size.width, size.height, transform]
  );

  const visibleNodes = useMemo(
    () =>
      graph.nodes.filter((node) => {
        const pos = layout.get(node.slug);
        if (pos == null) return false;
        return isNodeVisible(pos.x, pos.y, nodeRadius(node), bounds);
      }),
    [graph.nodes, layout, bounds]
  );

  const visibleSlugs = useMemo(
    () => new Set(visibleNodes.map((node) => node.slug)),
    [visibleNodes]
  );

  const visibleEdges = useMemo(
    () =>
      graph.edges.filter(
        (edge) => visibleSlugs.has(edge.source) && visibleSlugs.has(edge.target)
      ),
    [graph.edges, visibleSlugs]
  );

  const handleWheel = useCallback((event: ReactWheelEvent<HTMLDivElement>) => {
    event.preventDefault();
    const factor = event.deltaY > 0 ? 0.92 : 1.08;
    setTransform((current) => ({
      ...current,
      scale: Math.min(CANVAS_ZOOM_MAX, Math.max(CANVAS_ZOOM_MIN, current.scale * factor)),
    }));
  }, []);

  const handlePointerDown = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      if (event.button !== 0) return;
      panRef.current = {
        active: true,
        startX: event.clientX,
        startY: event.clientY,
        tx: transform.x,
        ty: transform.y,
      };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    [transform.x, transform.y]
  );

  const handlePointerMove = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    if (!panRef.current.active) return;
    const dx = event.clientX - panRef.current.startX;
    const dy = event.clientY - panRef.current.startY;
    setTransform((current) => ({
      ...current,
      x: panRef.current.tx + dx,
      y: panRef.current.ty + dy,
    }));
  }, []);

  const handlePointerUp = useCallback((event: ReactPointerEvent<HTMLDivElement>) => {
    panRef.current.active = false;
    event.currentTarget.releasePointerCapture(event.pointerId);
  }, []);

  const showLabels = transform.scale >= 0.6;

  return (
    <div
      ref={containerRef}
      className="relative h-[min(640px,calc(100vh-14rem))] cursor-grab overflow-hidden rounded-lg border border-border bg-bg active:cursor-grabbing"
      data-testid="research-canvas-viewport"
      onWheel={handleWheel}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={handlePointerUp}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.08]"
        style={{
          backgroundImage:
            "radial-gradient(circle, currentColor 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
        aria-hidden
      />

      <svg
        className="absolute inset-0 h-full w-full touch-none select-none"
        role="img"
        aria-label="Mappa concettuale"
      >
        <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
          {visibleEdges.map((edge) => {
            const source = layout.get(edge.source);
            const target = layout.get(edge.target);
            if (source == null || target == null) return null;
            return (
              <line
                key={edgeKey(edge)}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={EDGE_STROKE[edge.relation]}
                strokeWidth={edge.relation === "related" ? 1 : 2}
                strokeDasharray={edge.relation === "contradicts" ? "6 4" : undefined}
                data-testid={`canvas-edge-${edge.source}-${edge.target}`}
              />
            );
          })}

          {visibleNodes.map((node) => {
            const pos = layout.get(node.slug);
            if (pos == null) return null;
            const radius = nodeRadius(node);
            const isSelected = selectedSlug === node.slug;
            const isFocus = graph.focus_slug === node.slug;

            return (
              <g
                key={node.slug}
                transform={`translate(${pos.x},${pos.y})`}
                className="pointer-events-auto cursor-pointer"
                data-testid={`canvas-node-${node.slug}`}
                onClick={(event) => {
                  event.stopPropagation();
                  setSelectedSlug(node.slug);
                }}
                onDoubleClick={(event) => {
                  event.stopPropagation();
                  router.push(`/knowledge/${node.slug}`);
                }}
              >
                <circle
                  r={radius}
                  className={cn(
                    "fill-surface stroke-accent transition-[stroke-width]",
                    isSelected || isFocus ? "stroke-[3px]" : "stroke-[2px]",
                    node.is_core && "fill-accent-subtle"
                  )}
                />
                {node.is_core && (
                  <circle r={radius + 4} className="fill-none stroke-accent/40 stroke-[1px]" />
                )}
                {showLabels && (
                  <text
                    y={radius + 16}
                    textAnchor="middle"
                    className="fill-ink text-[11px] font-medium"
                  >
                    {truncateLabel(node.title)}
                  </text>
                )}
                <foreignObject
                  x={radius - 28}
                  y={radius - 8}
                  width={56}
                  height={24}
                  className="overflow-visible"
                >
                  <KnowledgeLifecycleBadge
                    state={node.knowledge_state as KnowledgeState}
                    className="scale-90 origin-top-left"
                  />
                </foreignObject>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="pointer-events-none absolute bottom-3 right-3 rounded-md border border-border bg-surface/90 px-2 py-1 text-xs text-ink-muted">
        {Math.round(transform.scale * 100)}%
      </div>

      {selectedSlug != null && (
        <div
          className="pointer-events-none absolute left-3 top-3 max-w-xs rounded-md border border-border bg-surface/95 px-3 py-2 text-xs text-ink-muted shadow-sm"
          data-testid="canvas-selection-chip"
        >
          Selezionato:{" "}
          <span className="font-medium text-ink">
            {titleBySlug.get(selectedSlug) ?? selectedSlug}
          </span>
          <span className="mt-1 block text-ink-subtle">
            Doppio clic → Explain · Trascina sfondo → pan · Rotella → zoom
          </span>
        </div>
      )}
    </div>
  );
}

export { EDGE_STROKE };
