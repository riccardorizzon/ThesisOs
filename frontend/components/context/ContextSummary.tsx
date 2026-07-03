import type { ContextPacket } from "@/lib/contextClient";
import {
  contextBarCounts,
  formatContextBarLabel,
} from "@/lib/contextClient";
import { cn } from "@/lib/cn";

export type ContextSummaryProps = {
  packet: ContextPacket;
  className?: string;
};

/**
 * Composable context counts — Spec §6.4 (fonti · concetti · decisioni · citazioni).
 * Layer: Business (Product Plane)
 */
export function ContextSummary({ packet, className }: ContextSummaryProps) {
  const label = formatContextBarLabel(contextBarCounts(packet));

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
