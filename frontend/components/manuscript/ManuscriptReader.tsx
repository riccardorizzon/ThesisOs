"use client";

import Link from "next/link";
import { useEffect } from "react";
import { cn } from "@/lib/cn";
import type { Chapter } from "@/lib/chapterClient";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ManuscriptMarkdown } from "@/components/manuscript/ManuscriptMarkdown";

export type ManuscriptReaderProps = {
  chapter: Chapter | null;
  prevId: string | null;
  nextId: string | null;
  emptyThesis?: boolean;
  onNavigate: (chapterId: string) => void;
  scrollToSectionId?: string | null;
  className?: string;
};

/** Right panel — read-only chapter body with prev/next and Modifica → Writing. */
export function ManuscriptReader({
  chapter,
  prevId,
  nextId,
  emptyThesis = false,
  onNavigate,
  scrollToSectionId,
  className,
}: ManuscriptReaderProps) {
  useEffect(() => {
    if (!scrollToSectionId) return;
    const target = document.getElementById(scrollToSectionId);
    target?.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [scrollToSectionId, chapter?.id]);

  if (emptyThesis) {
    return (
      <section
        data-testid="manuscript-reader"
        className={cn("flex flex-1 flex-col items-start justify-center gap-3 p-8", className)}
      >
        <h2 className="text-lg font-semibold text-ink">Nessun capitolo</h2>
        <p className="text-sm text-ink-muted">
          Aggiungi capitoli in Writing per iniziare a comporre la tesi.
        </p>
        <Link
          href="/writing"
          className="text-sm font-medium text-accent underline-offset-2 hover:underline"
        >
          Vai a Writing
        </Link>
      </section>
    );
  }

  if (!chapter) {
    return (
      <section
        data-testid="manuscript-reader"
        className={cn("flex flex-1 items-center justify-center p-8", className)}
      >
        <p className="text-sm text-ink-muted">Seleziona un capitolo dall&apos;indice.</p>
      </section>
    );
  }

  const hasContent = Boolean(chapter.content_md?.trim());

  return (
    <section
      data-testid="manuscript-reader"
      aria-label="Lettura capitolo"
      className={cn("flex min-h-0 flex-1 flex-col", className)}
    >
      <header className="flex flex-wrap items-center gap-3 border-b border-border px-6 py-4">
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-xl font-semibold text-ink">{chapter.title}</h1>
          <p className="mt-0.5 text-xs text-ink-muted">{chapter.word_count} parole</p>
        </div>
        <StatusBadge status={chapter.status} />
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            aria-label="Precedente"
            disabled={!prevId}
            onClick={() => prevId && onNavigate(prevId)}
            className={cn(
              "rounded-md border border-border px-3 py-1.5 text-sm font-medium transition-colors",
              prevId
                ? "text-ink hover:bg-surface-muted"
                : "cursor-not-allowed text-ink-subtle opacity-50"
            )}
          >
            Precedente
          </button>
          <button
            type="button"
            aria-label="Successivo"
            disabled={!nextId}
            onClick={() => nextId && onNavigate(nextId)}
            className={cn(
              "rounded-md border border-border px-3 py-1.5 text-sm font-medium transition-colors",
              nextId
                ? "text-ink hover:bg-surface-muted"
                : "cursor-not-allowed text-ink-subtle opacity-50"
            )}
          >
            Successivo
          </button>
          <Link
            href={`/writing/${chapter.id}`}
            data-testid="manuscript-edit"
            className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-ink-inverse hover:bg-accent/90"
          >
            Modifica
          </Link>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-6">
        {!hasContent ? (
          <div className="space-y-3">
            <p className="text-sm text-ink-muted">Ancora vuoto.</p>
            <Link
              href={`/writing/${chapter.id}`}
              className="text-sm font-medium text-accent underline-offset-2 hover:underline"
            >
              Modifica in Writing
            </Link>
          </div>
        ) : (
          <ManuscriptMarkdown content={chapter.content_md ?? ""} />
        )}
      </div>
    </section>
  );
}
