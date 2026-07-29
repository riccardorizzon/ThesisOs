"use client";

import Link from "next/link";
import { getProjectStorageItem, setProjectStorageItem } from "@/lib/projectScope";
import { useCallback, useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/cn";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { MarkdownSection } from "@/components/writing/MarkdownEditor";
import {
  type WritingOutlineChapter,
} from "@/components/writing/writingTypes";
import { ChapterApiError, chapterClient, type Chapter } from "@/lib/chapterClient";
import { CreateChapterButton } from "@/components/writing/CreateChapterButton";
import { persistChapterMetadata } from "@/lib/chapterMetadata";

export type OutlineFilter = "all" | "in_progress" | "needs_review";

export type WritingOutlineProps = {
  chapters?: WritingOutlineChapter[];
  activeChapterId?: string;
  activeSectionId?: string;
  sections?: MarkdownSection[];
  onChapterCreated?: (chapter: Chapter) => void;
  onChapterUpdated?: (chapter: Chapter) => void;
  className?: string;
};

const ORDER_KEY = "outline-order";

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
    const raw = getProjectStorageItem(ORDER_KEY);
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
  chapters = [],
  activeChapterId,
  activeSectionId,
  sections = [],
  onChapterCreated,
  onChapterUpdated,
  className,
}: WritingOutlineProps) {
  const [filter, setFilter] = useState<OutlineFilter>("all");
  const [ordered, setOrdered] = useState(chapters);
  const [dragId, setDragId] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameTitle, setRenameTitle] = useState("");
  const [renameBusy, setRenameBusy] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);
  const [reorderError, setReorderError] = useState<string | null>(null);

  useEffect(() => {
    setOrdered(applyStoredOrder(chapters));
  }, [chapters]);

  const persistOrder = useCallback(
    async (next: WritingOutlineChapter[], previous: WritingOutlineChapter[]) => {
      const ids = next.map((c) => c.id);
      setProjectStorageItem(ORDER_KEY, JSON.stringify(ids));
      setOrdered(next);
      setReorderError(null);
      try {
        await chapterClient.reorder(ids);
      } catch (err) {
        setOrdered(previous);
        setProjectStorageItem(
          ORDER_KEY,
          JSON.stringify(previous.map((c) => c.id))
        );
        setReorderError(
          err instanceof Error ? err.message : "Riordino non riuscito. Riprova."
        );
      }
    },
    []
  );

  const handleDrop = (targetId: string) => {
    if (!dragId || dragId === targetId) return;
    const from = ordered.findIndex((c) => c.id === dragId);
    const to = ordered.findIndex((c) => c.id === targetId);
    if (from < 0 || to < 0) return;
    const previous = ordered;
    const next = [...ordered];
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    void persistOrder(next, previous);
    setDragId(null);
  };

  const cancelRename = useCallback(() => {
    setRenamingId(null);
    setRenameTitle("");
    setRenameError(null);
  }, []);

  const handleRename = useCallback(
    async (chapter: WritingOutlineChapter) => {
      const title = renameTitle.trim();
      if (!title || renameBusy) return;
      setRenameBusy(true);
      setRenameError(null);
      try {
        const updated = await persistChapterMetadata(
          { id: chapter.id, version: chapter.version },
          { title }
        );
        onChapterUpdated?.(updated);
        setRenamingId(null);
        setRenameTitle("");
        setActionId(null);
      } catch (err) {
        if (err instanceof ChapterApiError && err.status === 409) {
          try {
            const fresh = await chapterClient.get(chapter.id);
            onChapterUpdated?.(fresh);
            setRenameTitle(fresh.title);
            setRenameError(
              "Capitolo modificato altrove. Titolo aggiornato — riprova."
            );
          } catch {
            setRenameError("Conflitto di versione. Ricarica e riprova.");
          }
        } else {
          setRenameError(err instanceof Error ? err.message : "Rinomina non riuscita.");
        }
      } finally {
        setRenameBusy(false);
      }
    },
    [onChapterUpdated, renameBusy, renameTitle]
  );

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
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-ink">Outline</h2>
            <p className="mt-0.5 text-xs text-ink-subtle">Trascina per riordinare</p>
          </div>
          {onChapterCreated ? (
            <CreateChapterButton
              variant="icon"
              chapters={ordered}
              onCreated={onChapterCreated}
              testId="writing-outline-add-chapter"
            />
          ) : null}
        </div>
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

      {renameError ? (
        <p className="px-3 py-1 text-xs text-danger" data-testid="outline-rename-error">
          {renameError}
        </p>
      ) : null}
      {reorderError ? (
        <p className="px-3 py-1 text-xs text-danger" data-testid="outline-reorder-error" role="alert">
          {reorderError}
        </p>
      ) : null}

      <ol className="flex-1 overflow-y-auto p-1">
        {visible.map((chapter) => {
          const selected = chapter.id === activeChapterId;
          return (
            <li
              key={chapter.id}
              draggable={renamingId !== chapter.id}
              onDragStart={() => setDragId(chapter.id)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={() => handleDrop(chapter.id)}
              className="relative"
            >
              <div
                className={cn(
                  "flex h-row-dense items-center gap-1 rounded-md px-1 transition-colors duration-200",
                  selected
                    ? "bg-accent-subtle font-medium text-accent"
                    : "text-ink hover:bg-surface-muted"
                )}
              >
                <Link
                  href={chapterHref(chapter.id)}
                  prefetch={false}
                  aria-current={selected ? "page" : undefined}
                  className={cn(
                    "flex min-w-0 flex-1 items-center gap-2 rounded-md px-2",
                    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                    "focus-visible:outline-accent cursor-pointer"
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
                {onChapterUpdated ? (
                  <button
                    type="button"
                    aria-label={`Azioni ${chapter.title}`}
                    data-testid={`outline-chapter-menu-${chapter.id}`}
                    onClick={() =>
                      setActionId((current) =>
                        current === chapter.id ? null : chapter.id
                      )
                    }
                    className="shrink-0 rounded px-1.5 py-1 text-xs text-ink-subtle hover:bg-surface"
                  >
                    <span aria-hidden="true">•••</span>
                  </button>
                ) : null}
              </div>

              {actionId === chapter.id && onChapterUpdated ? (
                <div className="absolute right-1 z-20 mt-1 w-28 rounded-md border border-border bg-surface p-1 shadow-md">
                  <button
                    type="button"
                    className="w-full rounded px-2 py-1 text-left text-xs hover:bg-surface-muted"
                    onClick={() => {
                      setRenamingId(chapter.id);
                      setRenameTitle(chapter.title);
                      setActionId(null);
                      setRenameError(null);
                    }}
                  >
                    Rinomina
                  </button>
                </div>
              ) : null}

              {renamingId === chapter.id ? (
                <form
                  className="mt-1 space-y-1 rounded-md border border-border bg-surface p-2"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void handleRename(chapter);
                  }}
                >
                  <label className="block text-xs text-ink-muted">
                    Nuovo titolo
                    <input
                      value={renameTitle}
                      maxLength={200}
                      disabled={renameBusy}
                      onChange={(event) => setRenameTitle(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === "Escape") {
                          event.preventDefault();
                          cancelRename();
                        }
                      }}
                      className="mt-1 w-full rounded border border-border px-2 py-1 text-xs text-ink"
                      autoFocus
                      data-testid={`outline-rename-input-${chapter.id}`}
                    />
                  </label>
                  <div className="flex justify-end gap-1">
                    <button
                      type="button"
                      className="rounded px-2 py-1 text-xs text-ink-muted"
                      onClick={cancelRename}
                    >
                      Annulla
                    </button>
                    <button
                      type="submit"
                      disabled={!renameTitle.trim() || renameBusy}
                      className="rounded bg-accent px-2 py-1 text-xs text-ink-inverse disabled:opacity-50"
                    >
                      Salva
                    </button>
                  </div>
                </form>
              ) : null}

              {selected && sections.length > 0 && (
                <ul className="mb-1 ml-3 border-l border-border pl-3">
                  {sections.map((section) => {
                    const sectionActive = section.id === activeSectionId;
                    return (
                      <li key={section.id}>
                        <Link
                          href={chapterHref(chapter.id, section.id)}
                          prefetch={false}
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
