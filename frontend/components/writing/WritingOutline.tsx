"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/cn";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { MarkdownSection } from "@/components/writing/MarkdownEditor";
import {
  WRITING_OUTLINE_STUB,
  type WritingOutlineChapter,
} from "@/components/writing/writingStub";
import { chapterClient } from "@/lib/chapterClient";

export type OutlineFilter = "all" | "in_progress" | "needs_review";

export type WritingOutlineProps = {
  chapters?: WritingOutlineChapter[];
  activeChapterId?: string;
  activeSectionId?: string;
  sections?: MarkdownSection[];
  className?: string;
};

const ORDER_KEY = "thesisos:outline-order";

const FILTER_OPTIONS: { id: OutlineFilter; label: string }[] = [
  { id: "all", label: "Tutti" },
  { id: "in_progress", label: "In corso" },
  { id: "needs_review", label: "Da revisionare" },
];

function filterChapters(
  chapters: WritingOutlineChapter[],
  filter: OutlineFilter
): WritingOutlineChapter[] {
  switch (filter) {
    case "in_progress":
      return chapters.filter((ch) => ch.status === "draft" || ch.status === "review");
    case "needs_review":
      return chapters.filter((ch) => ch.status === "review");
    default:
      return chapters;
  }
}

function applyStoredOrder(chapters: WritingOutlineChapter[]): WritingOutlineChapter[] {
  if (typeof window === "undefined") return chapters;
  try {
    const raw = localStorage.getItem(ORDER_KEY);
    if (!raw) return chapters;
    const order: string[] = JSON.parse(raw);
    const byId = new Map(chapters.map((c) => [c.id, c]));
    const sorted = order.map((id) => byId.get(id)).filter(Boolean) as WritingOutlineChapter[];
    const rest = chapters.filter((c) => !order.includes(c.id));
    return [...sorted, ...rest];
  } catch {
    return chapters;
  }
}

function chapterHref(chapterId: string, sectionId?: string): string {
  const base = `/writing/${chapterId}`;
  if (!sectionId) return base;
  return `${base}?section=${encodeURIComponent(sectionId)}`;
}

/**
 * Outline tree — left panel with status badges, section nav, drag reorder (PX-6).
 */
export function WritingOutline({
  chapters = WRITING_OUTLINE_STUB,
  activeChapterId,
  activeSectionId,
  sections = [],
  className,
}: WritingOutlineProps) {
  const [filter, setFilter] = useState<OutlineFilter>("all");
  const [ordered, setOrdered] = useState(chapters);
  const [dragId, setDragId] = useState<string | null>(null);

  useEffect(() => {
    setOrdered(applyStoredOrder(chapters));
  }, [chapters]);

  const persistOrder = useCallback(async (next: WritingOutlineChapter[]) => {
    const ids = next.map((c) => c.id);
    localStorage.setItem(ORDER_KEY, JSON.stringify(ids));
    setOrdered(next);
    try {
      await chapterClient.reorder(ids);
    } catch {
      // Stub chapters may not exist in API — local order still persisted
    }
  }, []);

  const handleDrop = (targetId: string) => {
    if (!dragId || dragId === targetId) return;
    const from = ordered.findIndex((c) => c.id === dragId);
    const to = ordered.findIndex((c) => c.id === targetId);
    if (from < 0 || to < 0) return;
    const next = [...ordered];
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    void persistOrder(next);
    setDragId(null);
  };

  const visible = useMemo(
    () => filterChapters(ordered, filter),
    [ordered, filter]
  );

  return (
    <nav
      aria-label="Outline capitoli"
      className={cn("flex h-full flex-col", className)}
      data-testid="writing-outline"
    >
      <header className="border-b border-border px-3 py-2">
        <h2 className="text-sm font-semibold text-ink">Outline</h2>
        <p className="mt-0.5 text-xs text-ink-subtle">Trascina per riordinare</p>
        <div
          className="mt-2 flex rounded-md border border-border bg-surface-muted p-0.5"
          role="group"
          aria-label="Filtra capitoli"
        >
          {FILTER_OPTIONS.map((opt) => (
            <button
              key={opt.id}
              type="button"
              aria-pressed={filter === opt.id}
              onClick={() => setFilter(opt.id)}
              className={cn(
                "flex-1 rounded px-2 py-1 text-xs font-medium transition-colors",
                filter === opt.id
                  ? "bg-surface text-ink shadow-sm"
                  : "text-ink-muted hover:text-ink"
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </header>

      <ol className="flex-1 overflow-y-auto p-1">
        {visible.map((chapter) => {
          const selected = chapter.id === activeChapterId;
          return (
            <li
              key={chapter.id}
              draggable
              onDragStart={() => setDragId(chapter.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(chapter.id)}
            >
              <Link
                href={chapterHref(chapter.id)}
                aria-current={selected ? "page" : undefined}
                className={cn(
                  "flex h-row-dense items-center gap-2 rounded-md px-3 transition-colors duration-200",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent cursor-pointer",
                  selected
                    ? "bg-accent-subtle font-medium text-accent"
                    : "text-ink hover:bg-surface-muted"
                )}
              >
                <span
                  className="cursor-grab text-ink-subtle"
                  aria-hidden
                  title="Trascina per riordinare"
                >
                  ⠿
                </span>
                <span className="min-w-0 flex-1 truncate text-sm">{chapter.title}</span>
                <StatusBadge status={chapter.status} />
              </Link>

              {selected && sections.length > 0 && (
                <ul className="mb-1 ml-3 border-l border-border pl-3">
                  {sections.map((section) => {
                    const sectionActive = section.id === activeSectionId;
                    return (
                      <li key={section.id}>
                        <Link
                          href={chapterHref(chapter.id, section.id)}
                          className={cn(
                            "flex h-row-dense items-center truncate pl-2 text-xs transition-colors",
                            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                            "focus-visible:outline-accent",
                            sectionActive
                              ? "border-l-2 border-accent font-medium text-accent"
                              : "border-l-2 border-transparent text-ink-muted hover:text-ink"
                          )}
                          style={{ paddingLeft: `${(section.level - 1) * 12 + 8}px` }}
                        >
                          {section.label}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
