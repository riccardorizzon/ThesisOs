"use client";

import type { SerendipitySuggestion } from "@/lib/canvasSerendipity";
import { cn } from "@/lib/cn";

export type SerendipityStripProps = {
  suggestions: SerendipitySuggestion[];
  onSuggestionActivate: (suggestion: SerendipitySuggestion) => void;
  className?: string;
};

/**
 * PX-5 serendipity strip — deterministic suggestion cards (PX5-EWO-007).
 * Layer: Business (Product Plane)
 */
export function SerendipityStrip({
  suggestions,
  onSuggestionActivate,
  className,
}: SerendipityStripProps) {
  if (suggestions.length === 0) {
    return null;
  }

  return (
    <section
      className={cn("space-y-2", className)}
      data-testid="canvas-serendipity-strip"
      aria-label="Suggerimenti serendipità"
    >
      <h2 className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
        Percorsi suggeriti
      </h2>
      <div className="flex gap-3 overflow-x-auto pb-1">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion.id}
            type="button"
            onClick={() => onSuggestionActivate(suggestion)}
            className={cn(
              "flex min-w-[200px] max-w-[240px] shrink-0 flex-col rounded-lg border border-border",
              "bg-surface px-3 py-2.5 text-left transition-colors",
              "hover:border-accent/40 hover:bg-surface-muted cursor-pointer"
            )}
            data-testid={`serendipity-card-${suggestion.type}`}
          >
            <span className="text-xs font-medium text-accent">{suggestion.title}</span>
            <span className="mt-1 line-clamp-2 text-sm text-ink">{suggestion.subtitle}</span>
            <span className="mt-2 text-xs font-medium text-accent">{suggestion.actionLabel}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
