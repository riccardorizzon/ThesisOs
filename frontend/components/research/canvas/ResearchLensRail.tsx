"use client";

import { cn } from "@/lib/cn";
import { CANVAS_LENSES, type CanvasLensId } from "@/lib/canvasLenses";

export type ResearchLensRailProps = {
  activeLensId: CanvasLensId;
  onLensChange: (lensId: CanvasLensId) => void;
  className?: string;
};

/**
 * Vertical lens rail for research canvas (PX5-EWO-006).
 * Layer: Business (Product Plane)
 */
export function ResearchLensRail({
  activeLensId,
  onLensChange,
  className,
}: ResearchLensRailProps) {
  return (
    <nav
      aria-label="Lenti di scoperta"
      className={cn("flex h-full flex-col gap-2", className)}
      data-testid="canvas-lens-rail"
    >
      <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">Lenti</p>
      {CANVAS_LENSES.map((lens) => {
        const active = lens.id === activeLensId;
        return (
          <button
            key={lens.id}
            type="button"
            onClick={() => onLensChange(lens.id)}
            className={cn(
              "rounded-md border px-3 py-2 text-left transition-colors cursor-pointer",
              active
                ? "border-accent border-l-[3px] bg-accent-subtle/40"
                : "border-border bg-surface hover:bg-surface-muted"
            )}
            data-testid={`canvas-lens-${lens.id}`}
          >
            <span className="block text-sm font-medium text-ink">{lens.label}</span>
            <span className="mt-0.5 block text-xs text-ink-muted">{lens.description}</span>
          </button>
        );
      })}
    </nav>
  );
}
