"use client";

import { useState } from "react";

import { cn } from "@/lib/cn";
import type { CanvasFilterOptions } from "@/lib/canvasLenses";
import type { KnowledgeGraphEdge, KnowledgeState } from "@/lib/knowledgeTypes";

const STATE_OPTIONS: KnowledgeState[] = [
  "candidate",
  "validated",
  "linked",
  "referenced",
  "deprecated",
];

const RELATION_OPTIONS: KnowledgeGraphEdge["relation"][] = [
  "supports",
  "contradicts",
  "extends",
  "related",
];

export type CanvasFilterPopoverProps = {
  filters: CanvasFilterOptions;
  onChange: (filters: CanvasFilterOptions) => void;
  className?: string;
};

/**
 * Canvas filter popover — composes with active lens (PX5-EWO-006).
 */
export function CanvasFilterPopover({ filters, onChange, className }: CanvasFilterPopoverProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className={cn("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="rounded-md border border-border px-2 py-1 text-xs text-ink cursor-pointer"
        data-testid="canvas-filters-button"
        aria-expanded={open}
      >
        Filtri
      </button>
      {open && (
        <div
          className="absolute right-0 z-20 mt-1 w-56 rounded-md border border-border bg-surface p-3 shadow-lg"
          data-testid="canvas-filters-popover"
        >
          <label className="flex items-center gap-2 text-xs text-ink">
            <input
              type="checkbox"
              checked={filters.hideDeprecated}
              onChange={(event) =>
                onChange({ ...filters, hideDeprecated: event.target.checked })
              }
            />
            Nascondi deprecati
          </label>
          <label className="mt-2 flex items-center gap-2 text-xs text-ink">
            <input
              type="checkbox"
              checked={filters.coreOnly}
              onChange={(event) => onChange({ ...filters, coreOnly: event.target.checked })}
            />
            Solo core
          </label>
          <fieldset className="mt-3">
            <legend className="text-xs font-medium text-ink-subtle">Relazioni</legend>
            {RELATION_OPTIONS.map((relation) => (
              <label key={relation} className="mt-1 flex items-center gap-2 text-xs text-ink">
                <input
                  type="checkbox"
                  checked={
                    filters.relationTypes === "all" ||
                    filters.relationTypes.includes(relation)
                  }
                  onChange={(event) => {
                    const current =
                      filters.relationTypes === "all" ? [...RELATION_OPTIONS] : [...filters.relationTypes];
                    const next = event.target.checked
                      ? [...new Set([...current, relation])]
                      : current.filter((item) => item !== relation);
                    onChange({
                      ...filters,
                      relationTypes: next.length === RELATION_OPTIONS.length ? "all" : next,
                    });
                  }}
                />
                {relation}
              </label>
            ))}
          </fieldset>
          <fieldset className="mt-3">
            <legend className="text-xs font-medium text-ink-subtle">Stato</legend>
            {STATE_OPTIONS.map((state) => (
              <label key={state} className="mt-1 flex items-center gap-2 text-xs text-ink">
                <input
                  type="checkbox"
                  checked={
                    filters.knowledgeStates === "all" ||
                    filters.knowledgeStates.includes(state)
                  }
                  onChange={(event) => {
                    const current =
                      filters.knowledgeStates === "all" ? [...STATE_OPTIONS] : [...filters.knowledgeStates];
                    const next = event.target.checked
                      ? [...new Set([...current, state])]
                      : current.filter((item) => item !== state);
                    onChange({
                      ...filters,
                      knowledgeStates: next.length === STATE_OPTIONS.length ? "all" : next,
                    });
                  }}
                />
                {state}
              </label>
            ))}
          </fieldset>
        </div>
      )}
    </div>
  );
}
