import { cn } from "@/lib/cn";
import type { ConceptDefinitionEnvelope } from "@/lib/knowledgeTypes";

export type ExplainDefinitionBlockProps = {
  definition: ConceptDefinitionEnvelope;
  className?: string;
};

/** Explain Page region B — definition block (PX3-EWO-005/006). */
export function ExplainDefinitionBlock({
  definition,
  className,
}: ExplainDefinitionBlockProps) {
  const hasDefinition =
    definition.definition != null && definition.definition.trim() !== "";

  return (
    <section
      className={cn("rounded-lg border border-border bg-surface p-6 shadow-sm", className)}
      data-testid="explain-region-b"
      aria-labelledby="explain-definition-heading"
    >
      <h2
        id="explain-definition-heading"
        className="text-xs font-semibold uppercase tracking-wide text-ink-subtle"
      >
        Definizione
      </h2>
      {hasDefinition ? (
        <p className="mt-3 text-sm leading-relaxed text-ink-muted">
          {definition.definition}
        </p>
      ) : (
        <p className="mt-3 text-sm text-ink-muted">
          Definizione non ancora approvata
        </p>
      )}
      {definition.source_count > 0 && (
        <p className="mt-4 text-xs text-ink-subtle">
          Basata su: {definition.source_count} fonti
        </p>
      )}
    </section>
  );
}
