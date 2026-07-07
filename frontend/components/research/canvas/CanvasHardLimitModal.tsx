"use client";

import type { CanvasLensId } from "@/lib/canvasLenses";
import { lensLabel } from "@/lib/canvasLenses";

export type CanvasHardLimitModalProps = {
  open: boolean;
  nodeCount: number;
  hardLimit: number;
  activeLensId: CanvasLensId;
  clusterMode: boolean;
  onChooseLens: (lensId: CanvasLensId) => void;
  onEnableCluster: () => void;
};

/**
 * Blocking modal when hard node limit exceeded (PX5-EWO-011).
 */
export function CanvasHardLimitModal({
  open,
  nodeCount,
  hardLimit,
  activeLensId,
  clusterMode,
  onChooseLens,
  onEnableCluster,
}: CanvasHardLimitModalProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
      data-testid="canvas-hard-limit-modal"
      role="alertdialog"
      aria-labelledby="canvas-hard-limit-title"
    >
      <div className="w-full max-w-md rounded-lg border border-border bg-surface p-5 shadow-lg">
        <h2 id="canvas-hard-limit-title" className="text-base font-semibold text-ink">
          Mappa troppo grande
        </h2>
        <p className="mt-2 text-sm text-ink-muted">
          {nodeCount} nodi visibili — limite {hardLimit}. Scegli un filtro o attiva il
          raggruppamento per continuare (RR-5).
        </p>
        <p className="mt-1 text-xs text-ink-subtle">
          Lente attuale: {lensLabel(activeLensId)}
          {clusterMode ? " · cluster attivo" : ""}
        </p>
        <div className="mt-4 flex flex-col gap-2">
          <button
            type="button"
            className="rounded-md border border-border px-3 py-2 text-sm text-ink hover:bg-surface-muted cursor-pointer"
            data-testid="hard-limit-choose-gap"
            onClick={() => onChooseLens("L-gap")}
          >
            Applica lente Lacune
          </button>
          <button
            type="button"
            className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-on-accent cursor-pointer"
            data-testid="hard-limit-enable-cluster"
            onClick={onEnableCluster}
          >
            Attiva raggruppamento cluster
          </button>
        </div>
      </div>
    </div>
  );
}
