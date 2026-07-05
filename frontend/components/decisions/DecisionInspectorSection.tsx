import type { ContextPacket } from "@/lib/contextClient";
import { cn } from "@/lib/cn";
import {
  parseDecisionsFromPacket,
  topRelevantDecisions,
} from "@/lib/decisionClient";
import { DecisionCard } from "@/components/decisions/DecisionCard";

export type DecisionInspectorSectionProps = {
  packet: ContextPacket;
  className?: string;
  defaultOpen?: boolean;
};

/**
 * Standalone accordion section for Context Inspector — Integration A wires into ContextInspector.
 * Layer: Business (Product Plane)
 */
export function DecisionInspectorSection({
  packet,
  className,
  defaultOpen,
}: DecisionInspectorSectionProps) {
  const decisions = parseDecisionsFromPacket(packet);
  const relevant = topRelevantDecisions(decisions, packet.entity ?? null);
  const hasBinding = relevant.length > 0;
  const open = defaultOpen ?? hasBinding;

  if (!hasBinding) {
    return (
      <section
        className={cn("rounded-lg border border-border bg-surface p-4", className)}
        data-testid="decision-inspector-section"
      >
        <h3 className="text-sm font-semibold text-ink">Decisioni vincolanti</h3>
        <p className="mt-2 text-sm text-ink-muted">
          Nessuna decisione vincolante rilevante per l&apos;ambito attivo.
        </p>
      </section>
    );
  }

  return (
    <details
      open={open}
      className={cn("group rounded-lg border border-border bg-surface", className)}
      data-testid="decision-inspector-section"
    >
      <summary className="cursor-pointer list-none px-4 py-3 text-sm font-semibold text-ink marker:content-none [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-2">
          Decisioni vincolanti
          <span className="text-xs font-normal text-ink-muted">
            {relevant.length}
          </span>
        </span>
      </summary>
      <div className="space-y-3 border-t border-border px-4 pb-4 pt-3">
        {relevant.map((decision) => (
          <DecisionCard key={decision.id} decision={decision} />
        ))}
      </div>
    </details>
  );
}
