import { cn } from "@/lib/cn";
import {
  EXPLORER_CONFIDENCE_OPTIONS,
  EXPLORER_STATE_OPTIONS,
  type ExplorerFilterState,
} from "./explorerTypes";

export type KnowledgeExplorerFiltersProps = {
  value: ExplorerFilterState;
  onChange: (next: ExplorerFilterState) => void;
  className?: string;
};

export function KnowledgeExplorerFilters({
  value,
  onChange,
  className,
}: KnowledgeExplorerFiltersProps) {
  return (
    <aside
      className={cn("w-full shrink-0 space-y-6 lg:w-[15rem]", className)}
      aria-label="Filtri knowledge"
      data-testid="knowledge-filter-rail"
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
              knowledgeState: e.target.value as ExplorerFilterState["knowledgeState"],
            })
          }
          className="w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
          aria-label="Filtra per stato"
        >
          {EXPLORER_STATE_OPTIONS.map((opt) => (
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
              confidence: e.target.value as ExplorerFilterState["confidence"],
            })
          }
          className="w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm"
          aria-label="Filtra per confidenza"
        >
          {EXPLORER_CONFIDENCE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm text-ink-muted">
          <input
            type="checkbox"
            checked={value.coreOnly}
            onChange={(e) => onChange({ ...value, coreOnly: e.target.checked })}
          />
          Solo core
        </label>
        <label className="flex items-center gap-2 text-sm text-ink-muted">
          <input
            type="checkbox"
            checked={value.showCandidates}
            onChange={(e) =>
              onChange({ ...value, showCandidates: e.target.checked })
            }
            data-testid="show-candidates-toggle"
          />
          Mostra candidati
        </label>
      </div>
    </aside>
  );
}
