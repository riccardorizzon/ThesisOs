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
  canvasNodeKind,
  isNodeVisible,
  layoutCanvasNodes,
  nodeRadius,
  panTransformToSlugs,
  truncateLabel,
  visibleWorldBounds,
} from "@/lib/canvasLayout";
import { applyNodeSelection, normalizeScreenRect, slugsInMarquee } from "@/lib/canvasSelection";
import {
  DEFAULT_CANVAS_TRANSFORM,
  type CanvasTransform,
} from "@/lib/canvasTransform";
import { cn } from "@/lib/cn";
import type { KnowledgeGraphEdge, KnowledgeGraphNode, KnowledgeGraphResponse, KnowledgeState } from "@/lib/knowledgeTypes";

const EDGE_STROKE: Record<KnowledgeGraphEdge["relation"], string> = {
  supports: "#16a34a",
  contradicts: "#ca8a04",
  extends: "#2563eb",
  related: "#94a3b8",
};

const SATELLITE_EDGE_STROKE = "#64748b";

function edgeStroke(edge: KnowledgeGraphEdge): string {
  if (edge.link_kind != null) return SATELLITE_EDGE_STROKE;
  return EDGE_STROKE[edge.relation];
}

function nodeNavigateTarget(node: KnowledgeGraphNode): string | null {
  switch (canvasNodeKind(node)) {
    case "concept":
      return `/knowledge/${node.slug}`;
    case "source":
      return `/sources/${node.slug}`;
    default:
      return null;
  }
}

export type ResearchCanvasViewportProps = {
  graph: KnowledgeGraphResponse;
  selectedSlugs: readonly string[];
  onSelectedSlugsChange: (slugs: string[]) => void;
  transform: CanvasTransform;
  onTransformChange: (transform: CanvasTransform) => void;
  highlightSlugs?: readonly string[];
  highlightEdgeKeys?: readonly string[];
  panRequest?: { key: number; slugs: string[] } | null;
};

function edgeKey(edge: KnowledgeGraphEdge): string {
  return `${edge.source}-${edge.target}-${edge.relation}`;
}

/**
 * PX-5 spatial canvas — pan/zoom viewport with concept node layer (PX5-EWO-003/004).
 * Layer: Business (Product Plane)
 */
export function ResearchCanvasViewport({
  graph,
  selectedSlugs,
  onSelectedSlugsChange,
  transform,
  onTransformChange,
  highlightSlugs = [],
  highlightEdgeKeys = [],
  panRequest = null,
}: ResearchCanvasViewportProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const [size, setSize] = useState({ width: 800, height: 560 });
  const selectedSet = useMemo(() => new Set(selectedSlugs), [selectedSlugs]);
  const highlightSlugSet = useMemo(() => new Set(highlightSlugs), [highlightSlugs]);
  const highlightEdgeSet = useMemo(() => new Set(highlightEdgeKeys), [highlightEdgeKeys]);
  const panRef = useRef<{
    active: boolean;
    startX: number;
    startY: number;
    tx: number;
    ty: number;
  }>({
    active: false,
    startX: 0,
    startY: 0,
    tx: 0,
    ty: 0,
  });
  const marqueeRef = useRef<{
    active: boolean;
    startX: number;
    startY: number;
    endX: number;
    endY: number;
  }>({
    active: false,
    startX: 0,
    startY: 0,
    endX: 0,
    endY: 0,
  });
  const [marqueeRect, setMarqueeRect] = useState<{
    left: number;
    top: number;
    width: number;
    height: number;
  } | null>(null);

  const layout = useMemo(() => layoutCanvasNodes(graph), [graph]);

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
    onTransformChange({
      x: size.width / 2 - pos.x,
      y: size.height / 2 - pos.y,
      scale: 1,
    });
    onSelectedSlugsChange([focusSlug]);
  }, [graph.focus_slug, layout, onSelectedSlugsChange, onTransformChange, size.width, size.height]);

  useEffect(() => {
    if (panRequest == null || panRequest.slugs.length === 0) return;
    const pan = panTransformToSlugs(
      panRequest.slugs,
      layout,
      size.width,
      size.height,
      transform.scale
    );
    if (pan == null) return;
    onTransformChange({
      x: pan.x,
      y: pan.y,
      scale: transform.scale,
    });
    onSelectedSlugsChange([...panRequest.slugs]);
  }, [panRequest, layout, onSelectedSlugsChange, onTransformChange, size.height, size.width, transform.scale]);

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

  const handleWheel = useCallback(
    (event: ReactWheelEvent<HTMLDivElement>) => {
      event.preventDefault();
      const factor = event.deltaY > 0 ? 0.92 : 1.08;
      onTransformChange({
        ...transform,
        scale: Math.min(CANVAS_ZOOM_MAX, Math.max(CANVAS_ZOOM_MIN, transform.scale * factor)),
      });
    },
    [onTransformChange, transform]
  );

  const finishMarquee = useCallback(
    (clientX: number, clientY: number) => {
      const container = containerRef.current;
      if (container == null || !marqueeRef.current.active) return;

      marqueeRef.current.active = false;
      marqueeRef.current.endX = clientX;
      marqueeRef.current.endY = clientY;
      setMarqueeRect(null);

      const slugs = slugsInMarquee(
        graph,
        container.getBoundingClientRect(),
        transform,
        marqueeRef.current.startX,
        marqueeRef.current.startY,
        clientX,
        clientY
      );
      if (slugs.length > 0) {
        onSelectedSlugsChange(slugs);
      }
    },
    [graph, onSelectedSlugsChange, transform]
  );

  const handlePointerDown = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      if (event.button !== 0) return;

      if (event.shiftKey) {
        marqueeRef.current = {
          active: true,
          startX: event.clientX,
          startY: event.clientY,
          endX: event.clientX,
          endY: event.clientY,
        };
        const container = containerRef.current;
        if (container != null) {
          setMarqueeRect(
            normalizeScreenRect(
              event.clientX,
              event.clientY,
              event.clientX,
              event.clientY,
              container.getBoundingClientRect()
            )
          );
        }
        event.currentTarget.setPointerCapture(event.pointerId);
        return;
      }

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
    if (marqueeRef.current.active) {
      marqueeRef.current.endX = event.clientX;
      marqueeRef.current.endY = event.clientY;
      const container = containerRef.current;
      if (container != null) {
        setMarqueeRect(
          normalizeScreenRect(
            marqueeRef.current.startX,
            marqueeRef.current.startY,
            event.clientX,
            event.clientY,
            container.getBoundingClientRect()
          )
        );
      }
      return;
    }

    if (!panRef.current.active) return;
    const dx = event.clientX - panRef.current.startX;
    const dy = event.clientY - panRef.current.startY;
    onTransformChange({
      ...transform,
      x: panRef.current.tx + dx,
      y: panRef.current.ty + dy,
    });
  }, [onTransformChange, transform]);

  const handlePointerUp = useCallback(
    (event: ReactPointerEvent<HTMLDivElement>) => {
      if (marqueeRef.current.active) {
        finishMarquee(event.clientX, event.clientY);
      } else {
        panRef.current.active = false;
      }
      event.currentTarget.releasePointerCapture(event.pointerId);
    },
    [finishMarquee]
  );

  const handleNodeClick = useCallback(
    (event: React.MouseEvent, slug: string) => {
      event.stopPropagation();
      const additive = event.metaKey || event.ctrlKey;
      onSelectedSlugsChange(applyNodeSelection(selectedSlugs, slug, additive));
    },
    [onSelectedSlugsChange, selectedSlugs]
  );

  const showLabels = transform.scale >= 0.6;

  return (
    <div
      ref={containerRef}
      className="relative h-full min-h-[560px] cursor-grab overflow-hidden bg-bg active:cursor-grabbing"
      data-testid="research-canvas-viewport"
      onWheel={handleWheel}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerLeave={(event) => {
        if (marqueeRef.current.active) {
          finishMarquee(event.clientX, event.clientY);
        } else {
          panRef.current.active = false;
        }
      }}
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
            const key = edgeKey(edge);
            const isHighlighted = highlightEdgeSet.has(key);
            const isSatelliteLink = edge.link_kind != null;
            return (
              <line
                key={key}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke={edgeStroke(edge)}
                strokeWidth={isHighlighted ? 4 : isSatelliteLink ? 1 : edge.relation === "related" ? 1 : 2}
                strokeDasharray={
                  isSatelliteLink || edge.relation === "contradicts" ? "6 4" : undefined
                }
                className={cn(isHighlighted && "animate-pulse")}
                data-testid={`canvas-edge-${edge.source}-${edge.target}`}
              />
            );
          })}

          {visibleNodes.map((node) => {
            const pos = layout.get(node.slug);
            if (pos == null) return null;
            const radius = nodeRadius(node);
            const kind = canvasNodeKind(node);
            const isSelected = selectedSet.has(node.slug);
            const isFocus = graph.focus_slug === node.slug;
            const isHighlighted = highlightSlugSet.has(node.slug);
            const navigateTarget = nodeNavigateTarget(node);

            return (
              <g
                key={node.slug}
                transform={`translate(${pos.x},${pos.y})`}
                className="pointer-events-auto cursor-pointer"
                data-testid={`canvas-node-${node.slug}`}
                data-node-kind={kind}
                data-highlighted={isHighlighted ? "true" : undefined}
                onPointerDown={(event) => event.stopPropagation()}
                onClick={(event) => handleNodeClick(event, node.slug)}
                onDoubleClick={(event) => {
                  event.stopPropagation();
                  if (navigateTarget != null) {
                    router.push(navigateTarget);
                  }
                }}
              >
                {isHighlighted && (
                  <circle
                    r={radius + 10}
                    className="fill-none stroke-accent stroke-[2px] animate-pulse"
                  />
                )}
                {kind === "concept" && (
                  <>
                    <circle
                      r={radius}
                      className={cn(
                        "fill-surface stroke-accent transition-[stroke-width]",
                        isSelected || isFocus || isHighlighted ? "stroke-[3px]" : "stroke-[2px]",
                        node.is_core && "fill-accent-subtle",
                        isHighlighted && "fill-accent/20"
                      )}
                    />
                    {node.is_core && (
                      <circle r={radius + 4} className="fill-none stroke-accent/40 stroke-[1px]" />
                    )}
                  </>
                )}
                {kind === "source" && (
                  <rect
                    x={-radius}
                    y={-radius * 0.75}
                    width={radius * 2}
                    height={radius * 1.5}
                    rx={4}
                    className={cn(
                      "fill-surface stroke-accent",
                      isSelected || isHighlighted ? "stroke-[3px]" : "stroke-[2px]"
                    )}
                  />
                )}
                {kind === "author" && (
                  <circle
                    r={radius}
                    className={cn(
                      "fill-accent-subtle stroke-accent",
                      isSelected || isHighlighted ? "stroke-[3px]" : "stroke-[2px]"
                    )}
                  />
                )}
                {kind === "decision" && (
                  <rect
                    x={-radius}
                    y={-radius}
                    width={radius * 2}
                    height={radius * 2}
                    transform="rotate(45)"
                    className={cn(
                      "fill-surface stroke-warning",
                      isSelected || isHighlighted ? "stroke-[3px]" : "stroke-[2px]"
                    )}
                  />
                )}
                {kind === "chapter" && (
                  <rect
                    x={-radius}
                    y={-radius * 0.6}
                    width={radius * 2}
                    height={radius * 1.2}
                    rx={2}
                    className={cn(
                      "fill-bg stroke-border",
                      isSelected || isHighlighted ? "stroke-[3px]" : "stroke-[2px]"
                    )}
                  />
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
                {kind === "concept" && (
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
                )}
              </g>
            );
          })}
        </g>
      </svg>

      {marqueeRect != null && marqueeRect.width + marqueeRect.height > 0 && (
        <div
          className="pointer-events-none absolute border border-accent bg-accent/10"
          style={{
            left: marqueeRect.left,
            top: marqueeRect.top,
            width: marqueeRect.width,
            height: marqueeRect.height,
          }}
          data-testid="canvas-marquee"
        />
      )}

      <div className="pointer-events-none absolute bottom-3 right-3 rounded-md border border-border bg-surface/90 px-2 py-1 text-xs text-ink-muted">
        {Math.round(transform.scale * 100)}%
      </div>
    </div>
  );
}

export { EDGE_STROKE, DEFAULT_CANVAS_TRANSFORM };
