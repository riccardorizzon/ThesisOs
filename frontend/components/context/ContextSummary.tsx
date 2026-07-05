import type { ContextPacket } from "@/lib/contextClient";
import {
  contextBarCounts,
  formatContextBarLabel,
} from "@/lib/contextClient";
import { cn } from "@/lib/cn";

export type ContextSummaryProps = {
  packet: ContextPacket;
  className?: string;
  onCountsClick?: () => void;
};

/**
 * Composable context counts — Spec §6.4 (fonti · decisioni · voci · citazioni).
 * Layer: Business (Product Plane)
 */
export function ContextSummary({
  packet,
  className,
  onCountsClick,
}: ContextSummaryProps) {
  const label = formatContextBarLabel(contextBarCounts(packet));

  if (onCountsClick) {
    return (
      <button
        type="button"
        className={cn(
          "text-sm tabular-nums text-ink-muted transition-colors hover:text-ink",
          className
        )}
        aria-label={`Riepilogo contesto: ${label}. Apri scheda Contesto`}
        data-testid="context-summary"
        onClick={onCountsClick}
      >
        {label}
      </button>
    );
  }

  return (
    <p
      className={cn("text-sm tabular-nums text-ink-muted", className)}
      aria-label={`Riepilogo contesto: ${label}`}
      data-testid="context-summary"
    >
      {label}
    </p>
  );
}
