import type { ReactNode } from "react";
import type { ContextPacket } from "@/lib/contextClient";
import { formatScopeChipLabel } from "@/lib/contextClient";
import { cn } from "@/lib/cn";
import { DecisionInspectorSection } from "@/components/decisions/DecisionInspectorSection";

export type ContextInspectorProps = {
  packet: ContextPacket;
  selectionAnchor?: string | null;
  className?: string;
};

type InspectorSectionProps = {
  title: string;
  defaultOpen?: boolean;
  emptyMessage?: string;
  isEmpty?: boolean;
  children: ReactNode;
  testId: string;
};

function InspectorSection({
  title,
  defaultOpen = false,
  emptyMessage,
  isEmpty = false,
  children,
  testId,
}: InspectorSectionProps) {
  return (
    <details
      open={defaultOpen}
      className="group rounded-md border border-border bg-surface"
      data-testid={testId}
    >
      <summary className="cursor-pointer list-none px-4 py-3 text-sm font-medium text-ink [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between gap-2">
          {title}
          <span
            aria-hidden="true"
            className="text-ink-subtle transition-transform group-open:rotate-180"
          >
            ▾
          </span>
        </span>
      </summary>
      <div className="space-y-2 border-t border-border px-4 py-3 text-sm text-ink-muted">
        {isEmpty && emptyMessage ? (
          <p className="text-ink-subtle">{emptyMessage}</p>
        ) : (
          children
        )}
      </div>
    </details>
  );
}

/**
 * Context Inspector (Contesto tab) — human-readable packet sections.
 * Layer: Business (Product Plane)
 */
export function ContextInspector({
  packet,
  selectionAnchor,
  className,
}: ContextInspectorProps) {
  const scopeLabel = formatScopeChipLabel(packet, selectionAnchor);
  const hasConstraints = packet.corpus_constraints.length > 0;
  const hasDefinitions = packet.definitions.length > 0;
  const hasSources = packet.relevant_sources.length > 0;
  const hasWritingRules = packet.writing_rules.length > 0;

  return (
    <div
      className={cn("space-y-3", className)}
      aria-label="Ispezione contesto"
      data-testid="context-inspector"
    >
      <InspectorSection title="Ambito" defaultOpen testId="inspector-ambito">
        <p className="font-medium text-ink">{scopeLabel}</p>
        {packet.entity?.snippet && (
          <p className="text-ink-muted">{packet.entity.snippet}</p>
        )}
        {!packet.entity && (
          <p className="text-ink-subtle">
            Progetto: {packet.project.title} — {packet.project.phase}
          </p>
        )}
      </InspectorSection>

      <DecisionInspectorSection packet={packet} />

      <InspectorSection
        title="Concetti nel contesto"
        defaultOpen
        isEmpty={packet.concepts.length === 0}
        emptyMessage="Nessun concetto nel contesto attuale."
        testId="inspector-concetti"
      >
        {packet.concepts.length > 0 && (
          <ul className="space-y-2">
            {packet.concepts.map((concept) => (
              <li key={concept.id}>
                <a
                  href={`/knowledge/${concept.slug ?? concept.id}`}
                  className="font-medium text-accent underline-offset-2 hover:underline"
                >
                  {concept.title}
                </a>
              </li>
            ))}
          </ul>
        )}
      </InspectorSection>

      <InspectorSection
        title="Vincoli corpus"
        defaultOpen={hasConstraints}
        isEmpty={!hasConstraints}
        emptyMessage="Nessun vincolo corpus attivo."
        testId="inspector-vincoli"
      >
        {hasConstraints &&
          packet.corpus_constraints.map((constraint) => (
            <p key={constraint}>{constraint}</p>
          ))}
      </InspectorSection>

      <InspectorSection
        title="Definizioni"
        isEmpty={!hasDefinitions}
        emptyMessage="Nessuna definizione nel contesto attuale."
        testId="inspector-definizioni"
      >
        {hasDefinitions &&
          packet.definitions.map((def) => (
            <div key={def.term}>
              <p className="font-medium text-ink">{def.term}</p>
              <p>{def.definition}</p>
            </div>
          ))}
      </InspectorSection>

      <InspectorSection
        title="Fonti rilevanti"
        defaultOpen
        isEmpty={!hasSources}
        emptyMessage="Nessuna fonte nel contesto attuale."
        testId="inspector-fonti"
      >
        {hasSources &&
          packet.relevant_sources.map((source) => (
            <p key={source.id}>{source.title}</p>
          ))}
      </InspectorSection>

      <InspectorSection
        title="Regole di scrittura"
        isEmpty={!hasWritingRules}
        emptyMessage="Nessuna regola di scrittura nel contesto attuale."
        testId="inspector-regole"
      >
        {hasWritingRules &&
          packet.writing_rules.map((rule) => <p key={rule}>{rule}</p>)}
      </InspectorSection>
    </div>
  );
}
