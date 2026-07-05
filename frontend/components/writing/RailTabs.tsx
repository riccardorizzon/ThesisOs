"use client";

import { cn } from "@/lib/cn";

export type RailTabId = "ai" | "contesto" | "fonte" | "revisione";

export type RailTabDef = {
  id: RailTabId;
  label: string;
  shortcut: number;
};

export const RAIL_TABS: RailTabDef[] = [
  { id: "ai", label: "AI", shortcut: 1 },
  { id: "contesto", label: "Contesto", shortcut: 2 },
  { id: "fonte", label: "Fonte", shortcut: 3 },
  { id: "revisione", label: "Revisione", shortcut: 4 },
];

export type RailTabsProps = {
  activeTab: RailTabId;
  onTabChange: (tab: RailTabId) => void;
  className?: string;
};

/**
 * Right rail tab bar — single slot switcher (UI spec §5.4).
 * Layer: Business (Product Plane)
 */
export function RailTabs({ activeTab, onTabChange, className }: RailTabsProps) {
  return (
    <div
      role="tablist"
      aria-label="Pannello laterale scrittura"
      className={cn("flex h-10 shrink-0 border-b border-border", className)}
    >
      {RAIL_TABS.map((tab) => {
        const selected = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`rail-tab-${tab.id}`}
            aria-selected={selected}
            aria-controls={`rail-panel-${tab.id}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "relative flex-1 px-2 text-xs font-medium transition-colors duration-200",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px]",
              "focus-visible:outline-accent cursor-pointer",
              selected ? "text-ink" : "text-ink-muted hover:text-ink"
            )}
          >
            {tab.label}
            {selected && (
              <span
                aria-hidden="true"
                className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-accent"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

export function railTabFromShortcut(shortcut: number): RailTabId | null {
  const match = RAIL_TABS.find((t) => t.shortcut === shortcut);
  return match?.id ?? null;
}
