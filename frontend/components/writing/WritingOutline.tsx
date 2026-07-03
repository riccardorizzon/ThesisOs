"use client";

import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  CHAPTER_STATUS_LABELS,
  WRITING_OUTLINE_STUB,
  type WritingOutlineChapter,
} from "@/components/writing/writingStub";

export type WritingOutlineProps = {
  chapters?: WritingOutlineChapter[];
  activeChapterId?: string;
  className?: string;
};

/**
 * Outline tree stub — left panel of Writing workspace (Spec §5.3).
 * Layer: Business (Product Plane)
 */
export function WritingOutline({
  chapters = WRITING_OUTLINE_STUB,
  activeChapterId,
  className,
}: WritingOutlineProps) {
  return (
    <nav
      aria-label="Outline capitoli"
      className={cn("flex h-full flex-col", className)}
    >
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Outline</h2>
        <p className="mt-0.5 text-xs text-ink-muted">
          Struttura tesi — drag reorder in PX-2
        </p>
      </header>
      <ol className="flex-1 overflow-y-auto p-2">
        {chapters.map((chapter) => {
          const selected = chapter.id === activeChapterId;
          return (
            <li key={chapter.id}>
              <Link
                href={`/writing/${chapter.id}`}
                aria-current={selected ? "page" : undefined}
                className={cn(
                  "flex flex-col rounded-md px-3 py-2 transition-colors duration-200",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent cursor-pointer",
                  selected
                    ? "border border-accent bg-accent-subtle"
                    : "border border-transparent hover:bg-surface-muted"
                )}
              >
                <span className="text-sm font-medium text-ink">{chapter.title}</span>
                <span className="mt-0.5 text-xs text-ink-subtle">
                  {CHAPTER_STATUS_LABELS[chapter.status]}
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
