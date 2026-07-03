import type { DecisionRef } from "@/lib/contextClient";
import { cn } from "@/lib/cn";

export type DecisionBadgeProps = {
  decisions: DecisionRef[];
  className?: string;
};

export function bindingDecisions(decisions: DecisionRef[]): DecisionRef[] {
  return decisions.filter((d) => d.binding);
}

/**
 * Binding decision count/summary from ContextPacket.
 * Layer: Business (Product Plane)
 */
export function DecisionBadge({ decisions, className }: DecisionBadgeProps) {
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
        "inline-flex items-center rounded-full bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent tabular-nums",
        className
      )}
      title={summaries}
      data-testid="decision-badge"
      aria-label={`${binding.length} ${label}: ${titles}`}
    >
      {binding.length} {label}
    </span>
  );
}
