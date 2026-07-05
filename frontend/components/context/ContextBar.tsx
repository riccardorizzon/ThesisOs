"use client";

import type { ContextPacket } from "@/lib/contextClient";
import {
  dispatchOpenContestoTab,
  formatScopeChipLabel,
} from "@/lib/contextClient";
import { cn } from "@/lib/cn";
import { ContextSummary } from "@/components/context/ContextSummary";

export type ContextBarWarningState = {
  active: boolean;
  message?: string;
};

export type ContextBarProps = {
  packet?: ContextPacket;
  loading?: boolean;
  selectionAnchor?: string | null;
  warningState?: ContextBarWarningState;
  className?: string;
  onScopeClick?: () => void;
  onOpenContestoTab?: () => void;
};

function ContextBarSkeleton() {
  return (
    <div
      className="flex min-h-contextbar flex-1 items-center gap-3"
      data-testid="context-bar-skeleton"
      aria-hidden="true"
    >
      <div className="h-6 w-28 animate-pulse rounded-md bg-surface-muted" />
      <div className="h-4 w-48 animate-pulse rounded bg-surface-muted" />
      <div className="h-4 w-32 animate-pulse rounded bg-surface-muted" />
    </div>
  );
}

/**
 * Context Engine summary bar — Spec §4.2, §6.4, ADR-0038.
 * Displays packet state only; no assembly logic.
 * Layer: Business (Product Plane)
 */
export function ContextBar({
  packet,
  loading = false,
  selectionAnchor,
  warningState,
  className,
  onScopeClick,
  onOpenContestoTab,
}: ContextBarProps) {
  const showContent = !loading && packet;
  const warningActive = warningState?.active ?? false;
  const scopeLabel = packet
    ? formatScopeChipLabel(packet, selectionAnchor)
    : "";

  const handleCountsClick = () => {
    onOpenContestoTab?.();
    dispatchOpenContestoTab();
  };

  return (
    <div
      className={cn(
        "flex h-contextbar min-h-contextbar items-center gap-3 rounded-lg border px-4 py-2 shadow-sm transition-[opacity,background-color,border-color] duration-150",
        warningActive
          ? "border-warning/30 bg-warning/5"
          : "border-border bg-surface",
        className
      )}
      aria-label="Contesto attivo per le azioni AI"
      aria-busy={loading}
      data-testid="context-bar"
    >
      {loading ? (
        <ContextBarSkeleton />
      ) : showContent ? (
        <div
          className="flex min-w-0 flex-1 items-center gap-3 opacity-100 transition-opacity duration-150"
          data-testid="context-bar-content"
        >
        <button
          type="button"
          className={cn(
            "shrink-0 rounded-md bg-accent-subtle px-2 py-0.5 text-sm font-medium text-accent transition-colors hover:bg-accent-subtle/80",
            warningActive && "inline-flex items-center gap-1"
          )}
          aria-label={`Ambito: ${scopeLabel}. Vai alla sezione nell'outline`}
          data-testid="context-scope-chip"
          onClick={onScopeClick}
        >
          {warningActive && (
            <span aria-hidden="true" className="text-warning">
              ▲
            </span>
          )}
          {scopeLabel}
        </button>

        {packet && (
          <ContextSummary
            packet={packet}
            className="min-w-0 truncate"
            onCountsClick={handleCountsClick}
          />
        )}

        {warningState?.message && (
          <p
            className="hidden truncate text-xs text-warning sm:block"
            data-testid="context-bar-warning-message"
          >
            {warningState.message}
          </p>
        )}
        </div>
      ) : null}

      {showContent && (
        <button
          type="button"
          className="shrink-0 text-sm text-ink-subtle transition-colors hover:text-ink"
          aria-label="Riepilogo contesto AI"
          title="Contesto assemblato per le azioni AI in questo ambito"
          data-testid="context-info-button"
        >
          ⓘ
        </button>
      )}
    </div>
  );
}
