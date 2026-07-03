"use client";

import { cn } from "@/lib/cn";
import {
  SOURCE_STATUS_LABELS,
  SOURCE_STATUS_OPTIONS,
  type SourceStatus,
} from "@/lib/libraryStub";

export type LibraryFilterValue = SourceStatus | "all";

export type LibraryFilterBarProps = {
  value: LibraryFilterValue;
  onChange: (value: LibraryFilterValue) => void;
  className?: string;
};

const FILTER_OPTIONS: { value: LibraryFilterValue; label: string }[] = [
  { value: "all", label: "Tutte" },
  ...SOURCE_STATUS_OPTIONS.map((status) => ({
    value: status,
    label: SOURCE_STATUS_LABELS[status],
  })),
];

/**
 * Source status filter — PX-1 placeholder (client-side stub only).
 * Layer: Business (Product Plane)
 */
export function LibraryFilterBar({
  value,
  onChange,
  className,
}: LibraryFilterBarProps) {
  return (
    <div
      role="group"
      aria-label="Filtra per stato fonte"
      className={cn("flex flex-wrap gap-2", className)}
    >
      {FILTER_OPTIONS.map((option) => {
        const selected = value === option.value;
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors duration-200",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
              "focus-visible:outline-accent cursor-pointer",
              selected
                ? "border-accent bg-accent-subtle text-accent"
                : "border-border bg-surface text-ink-muted hover:border-border-strong hover:bg-surface-muted"
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
