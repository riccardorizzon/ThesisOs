"use client";

import { cn } from "@/lib/cn";

export type SourcePeekSlotProps = {
  className?: string;
};

/**
 * Placeholder for Fonte tab peek reader — wired by PX2-EWO-004 (Integration B).
 * Layer: Business (Product Plane)
 */
export function SourcePeekSlot({ className }: SourcePeekSlotProps) {
  return (
    <div
      className={cn("flex h-full flex-col p-4", className)}
      data-testid="source-peek-slot"
      aria-label="Anteprima fonte"
    >
      <p className="text-sm font-medium text-ink">Anteprima fonte</p>
      <p className="mt-2 text-xs text-ink-muted">
        Seleziona una fonte dal corpus o dalla barra contesto per aprire il lettore
        compatto. Integrazione PX2-EWO-004.
      </p>
    </div>
  );
}
