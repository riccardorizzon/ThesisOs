import Link from "next/link";

import { cn } from "@/lib/cn";
import {
  CONFIDENCE_FILTER_OPTIONS,
  KNOWLEDGE_STATE_FILTER_OPTIONS,
  type SourcesFilterState,
} from "@/lib/sourcesTypes";

export type SourcesFilterRailProps = {
  value: SourcesFilterState;
  onChange: (next: SourcesFilterState) => void;
  className?: string;
};

export function SourcesFilterRail({
  value,
  onChange,
  className,
}: SourcesFilterRailProps) {
  return (
    <aside
      className={cn(
        "w-full shrink-0 space-y-6 lg:w-[15rem]",
        className
      )}
      aria-label="Filtri fonti"
      data-testid="sources-filter-rail"
    >
      <div>
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-subtle">
          Stato knowledge
        </h2>
        <select
          value={value.knowledgeState}
          onChange={(e) =>
            onChange({
              ...value,
              knowledgeState: e.target.value as SourcesFilterState["knowledgeState"],
            })
          }
          className="w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-ink"
          aria-label="Filtra per stato knowledge"
        >
          {KNOWLEDGE_STATE_FILTER_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-subtle">
          Confidenza
        </h2>
        <select
          value={value.confidence}
          onChange={(e) =>
            onChange({
              ...value,
              confidence: e.target.value as SourcesFilterState["confidence"],
            })
          }
          className="w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-ink"
          aria-label="Filtra per confidenza"
        >
          {CONFIDENCE_FILTER_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="flex items-center gap-2 text-sm text-ink-muted">
          <input
            type="checkbox"
            checked={value.includeDeprecated}
            onChange={(e) =>
              onChange({ ...value, includeDeprecated: e.target.checked })
            }
            className="rounded border-border"
          />
          Mostra deprecate
        </label>
      </div>

      <div className="rounded-md border border-border bg-surface-muted p-3 text-xs text-ink-subtle">
        <p className="font-medium text-ink-muted">Concetti</p>
        <p className="mt-1">
          I chip sui card collegano a{" "}
          <Link href="/knowledge" className="text-accent hover:underline">
            Knowledge
          </Link>
          .
        </p>
      </div>
    </aside>
  );
}
