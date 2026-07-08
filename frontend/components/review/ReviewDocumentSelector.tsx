"use client";

import type { ReviewChapter } from "./reviewTypes";
import { reviewStatusLabel } from "./reviewTypes";

export type ReviewDocumentSelectorProps = {
  chapters: ReviewChapter[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  className?: string;
};

/**
 * Document/chapter selector stub for revision workflow.
 * Layer: Business (Product Plane)
 */
export function ReviewDocumentSelector({
  chapters,
  selectedId,
  onSelect,
  className,
}: ReviewDocumentSelectorProps) {
  return (
    <section
      aria-labelledby="review-selector-heading"
      className={className}
    >
      <h2
        id="review-selector-heading"
        className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500"
      >
        Capitoli in revisione
      </h2>
      <ul className="space-y-2" role="listbox" aria-label="Seleziona capitolo">
        {chapters.map((chapter) => {
          const selected = chapter.id === selectedId;
          return (
            <li key={chapter.id}>
              <button
                type="button"
                role="option"
                aria-selected={selected}
                onClick={() => onSelect(chapter.id)}
                className={[
                  "w-full rounded-lg border px-4 py-3 text-left transition-colors cursor-pointer",
                  selected
                    ? "border-blue-800 bg-blue-50 ring-1 ring-blue-800"
                    : "border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50",
                ].join(" ")}
              >
                <span className="block text-sm font-medium text-gray-900">
                  {chapter.title}
                </span>
                <span className="mt-1 block text-xs text-gray-500">
                  {reviewStatusLabel(chapter.status)}
                  {chapter.pendingChanges > 0
                    ? ` · ${chapter.pendingChanges} modifiche in sospeso`
                    : ""}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
