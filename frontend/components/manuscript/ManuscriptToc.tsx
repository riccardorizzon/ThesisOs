"use client";

import { cn } from "@/lib/cn";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ManuscriptTocChapter } from "@/lib/manuscriptToc";

export type ManuscriptTocProps = {
  chapters: ManuscriptTocChapter[];
  activeChapterId: string | null;
  activeSectionId?: string | null;
  onSelectChapter: (chapterId: string) => void;
  onSelectSection: (chapterId: string, sectionId: string) => void;
  className?: string;
};

/** Left panel — ordered thesis structure with status, words, and heading sections. */
export function ManuscriptToc({
  chapters,
  activeChapterId,
  activeSectionId,
  onSelectChapter,
  onSelectSection,
  className,
}: ManuscriptTocProps) {
  const words = chapters.reduce((sum, ch) => sum + ch.word_count, 0);

  return (
    <nav
      aria-label="Indice manoscritto"
      data-testid="manuscript-toc"
      className={cn("flex h-full flex-col border-r border-border bg-surface", className)}
    >
      <header className="border-b border-border px-3 py-3">
        <h2 className="text-sm font-semibold text-ink">Manoscritto</h2>
        <p className="mt-1 text-xs text-ink-muted">
          {chapters.length} {chapters.length === 1 ? "capitolo" : "capitoli"} · {words} parole
        </p>
      </header>

      <ol className="flex-1 overflow-y-auto p-2">
        {chapters.map((chapter) => {
          const selected = chapter.id === activeChapterId;
          return (
            <li key={chapter.id} className="mb-1">
              <button
                type="button"
                aria-current={selected ? "page" : undefined}
                onClick={() => onSelectChapter(chapter.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-sm transition-colors",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                  selected
                    ? "bg-accent-subtle font-medium text-accent"
                    : "text-ink hover:bg-surface-muted"
                )}
              >
                <span className="min-w-0 flex-1 truncate">{chapter.title}</span>
                <span className="shrink-0 text-xs tabular-nums text-ink-muted">
                  {chapter.word_count}
                </span>
                <StatusBadge status={chapter.status} />
              </button>

              {chapter.sections.length > 0 ? (
                <ul className="mb-1 ml-2 border-l border-border pl-2">
                  {chapter.sections.map((section) => {
                    const sectionActive =
                      selected && section.id === activeSectionId;
                    return (
                      <li key={`${chapter.id}-${section.id}`}>
                        <button
                          type="button"
                          onClick={() => onSelectSection(chapter.id, section.id)}
                          className={cn(
                            "flex w-full truncate py-1 text-left text-xs transition-colors",
                            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
                            sectionActive
                              ? "border-l-2 border-accent pl-2 font-medium text-accent"
                              : "border-l-2 border-transparent pl-2 text-ink-muted hover:text-ink"
                          )}
                          style={{ paddingLeft: `${(section.level - 1) * 8 + 8}px` }}
                        >
                          {section.label}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
