import type { DecisionRef } from "@/lib/contextClient";
import { cn } from "@/lib/cn";

export type DecisionBadgeProps = {
  decisions: DecisionRef[];
  className?: string;
  /** Amber emphasis when binding decision conflicts with selection — wired by Integration A */
  conflict?: boolean;
};

export function bindingDecisions(decisions: DecisionRef[]): DecisionRef[] {
  return decisions.filter((d) => d.binding);
}

/**
 * Binding decision count/summary from ContextPacket.
 * Layer: Business (Product Plane)
 */
export function DecisionBadge({
  decisions,
  className,
  conflict = false,
}: DecisionBadgeProps) {
  const binding = bindingDecisions(decisions);
  if (binding.length === 0) {
    return null;
  }

  const titles = binding.map((d) => d.title ?? d.id).join(", ");
  const summaries = binding.map((d) => d.summary).join("; ");
  const label =
    binding.length === 1 ? "decisione vincolante" : "decisioni vincolanti";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium tabular-nums",
        conflict
          ? "border border-warning/30 bg-warning/10 text-warning"
          : "bg-accent-subtle text-accent",
        className
      )}
      title={summaries}
      data-testid="decision-badge"
      data-conflict={conflict ? "true" : "false"}
      aria-label={
        conflict
          ? `Attenzione: ${binding.length} ${label}: ${titles}`
          : `${binding.length} ${label}: ${titles}`
      }
    >
      {conflict && (
        <span aria-hidden="true" data-testid="decision-badge-warning-icon">
          ⚠
        </span>
      )}
      {binding.length} {label}
    </span>
  );
}
