import type { ContextPacket } from "@/lib/contextClient";
import { cn } from "@/lib/cn";
import { ConstraintChip } from "@/components/context/ConstraintChip";
import { ContextSummary } from "@/components/context/ContextSummary";
import { bindingDecisions, DecisionBadge } from "@/components/context/DecisionBadge";

export type ContextBarProps = {
  packet: ContextPacket;
  className?: string;
};

/**
 * Context Engine summary bar — Spec §6.4, ADR-0038.
 * Displays packet state only; no assembly logic.
 * Layer: Business (Product Plane)
 */
export function ContextBar({ packet, className }: ContextBarProps) {
  const entityLabel = packet.entity
    ? `${packet.entity.title}`
    : packet.project.phase;
  const showIndicators =
    packet.corpus_constraints.length > 0 || bindingDecisions(packet.decisions).length > 0;

  return (
    <div
      className={cn(
        "flex flex-col gap-2 rounded-lg border border-border bg-surface px-4 py-3 shadow-sm sm:flex-row sm:items-center sm:justify-between",
        className
      )}
      aria-label="Contesto attivo per le azioni AI"
    >
      <div className="min-w-0 flex-1 space-y-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
            Contesto
          </p>
          <p className="truncate text-sm font-medium text-ink">{entityLabel}</p>
        </div>
        {showIndicators && (
          <div
            className="flex flex-wrap items-center gap-2"
            data-testid="context-indicators"
          >
            {packet.corpus_constraints.map((constraint) => (
              <ConstraintChip key={constraint} constraint={constraint} />
            ))}
            <DecisionBadge decisions={packet.decisions} />
          </div>
        )}
      </div>
      <ContextSummary packet={packet} className="shrink-0" />
    </div>
  );
}
