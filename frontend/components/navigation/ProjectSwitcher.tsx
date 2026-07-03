"use client";

import { defaultProjectContext } from "@/lib/projectContext";

/**
 * PX-1 project switcher stub — displays active project_id from ProjectContext.
 * Multi-project selection deferred to PX-2+.
 * Layer: Business (Product Plane)
 */
export function ProjectSwitcher() {
  const { project_id } = defaultProjectContext();

  return (
    <div className="space-y-1">
      <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
        Progetto
      </span>
      <button
        type="button"
        disabled
        aria-label={`Progetto attivo: ${project_id}`}
        title="Selezione multi-progetto in arrivo"
        className="flex w-full items-center justify-between rounded-md border border-border bg-surface px-3 py-2 text-left text-sm font-medium text-ink shadow-sm"
      >
        <span className="truncate font-mono text-xs">{project_id}</span>
        <span className="ml-2 shrink-0 text-xs text-ink-subtle" aria-hidden>
          PX-2
        </span>
      </button>
    </div>
  );
}
