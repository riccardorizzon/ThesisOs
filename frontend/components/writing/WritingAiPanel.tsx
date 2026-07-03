"use client";

import { cn } from "@/lib/cn";
import {
  WRITING_AI_ACTIONS,
  type WritingAiAction,
} from "@/components/writing/writingStub";

export type WritingAiPanelProps = {
  actions?: WritingAiAction[];
  className?: string;
};

/**
 * AI action panel stub — right panel (Spec §5.3, §5.6).
 * Buttons are non-executing placeholders until PX-2.
 * Layer: Business (Product Plane)
 */
export function WritingAiPanel({
  actions = WRITING_AI_ACTIONS,
  className,
}: WritingAiPanelProps) {
  return (
    <aside
      aria-label="Azioni AI contestuali"
      className={cn("flex h-full flex-col", className)}
    >
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Azioni AI</h2>
        <p className="mt-0.5 text-xs text-ink-muted">
          Runner con Context Packet — esecuzione in PX-2
        </p>
      </header>
      <ul className="flex-1 space-y-2 overflow-y-auto p-3">
        {actions.map((action) => (
          <li key={action.id}>
            <button
              type="button"
              disabled
              aria-disabled="true"
              title="Disponibile in PX-2"
              className={cn(
                "w-full rounded-md border border-border bg-surface px-3 py-2 text-left",
                "cursor-not-allowed opacity-70"
              )}
            >
              <span className="block text-sm font-medium text-ink">{action.label}</span>
              <span className="mt-0.5 block text-xs text-ink-muted">
                {action.description}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
