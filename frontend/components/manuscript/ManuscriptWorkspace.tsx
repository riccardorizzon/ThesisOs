"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/cn";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import {
  buildManuscriptOutline,
  flattenManuscriptOutline,
  neighborChapterIds,
  sortChaptersByOrder,
} from "@/lib/manuscriptToc";
import { ManuscriptToc } from "@/components/manuscript/ManuscriptToc";
import { ManuscriptReader } from "@/components/manuscript/ManuscriptReader";
import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";

export type ManuscriptWorkspaceProps = {
  chapterId?: string | null;
  className?: string;
};

async function hydrateChapters(list: Chapter[]): Promise<Chapter[]> {
  return Promise.all(
    list.map(async (chapter) => {
      if (chapter.content_md != null && chapter.content_md !== "") {
        return chapter;
      }
      try {
        return await chapterClient.get(chapter.id);
      } catch {
        return chapter;
      }
    })
  );
}

/** Two-panel Manoscritto — hierarchical TOC + read-only chapter reader. */
export function ManuscriptWorkspace({ chapterId, className }: ManuscriptWorkspaceProps) {
  const router = useRouter();
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTocMobile, setShowTocMobile] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await chapterClient.list();
      const ordered = sortChaptersByOrder(list);
      const hydrated = await hydrateChapters(ordered);
      setChapters(hydrated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossibile caricare il manoscritto");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, reloadToken]);

  const outline = useMemo(() => buildManuscriptOutline(chapters), [chapters]);
  const orderedIds = useMemo(() => flattenManuscriptOutline(outline), [outline]);

  const activeChapterId = useMemo(() => {
    if (orderedIds.length === 0) return null;
    if (chapterId && orderedIds.includes(chapterId)) return chapterId;
    return orderedIds[0]!;
  }, [chapterId, orderedIds]);

  useEffect(() => {
    if (loading || orderedIds.length === 0) return;
    if (chapterId && !orderedIds.includes(chapterId)) {
      router.replace(`/manuscript/${orderedIds[0]!}`);
      return;
    }
    if (!chapterId && activeChapterId) {
      router.replace(`/manuscript/${activeChapterId}`);
    }
  }, [loading, chapterId, orderedIds, activeChapterId, router]);

  const activeChapter = chapters.find((ch) => ch.id === activeChapterId) ?? null;
  const { prevId, nextId } = neighborChapterIds(orderedIds, activeChapterId ?? "");

  const navigateChapter = (id: string) => {
    router.push(`/manuscript/${id}`);
    setShowTocMobile(false);
  };

  if (loading) {
    return (
      <p className="p-6 text-sm text-ink-muted" data-testid="manuscript-loading">
        Caricamento manoscritto…
      </p>
    );
  }

  if (error) {
    return (
      <div className="p-6" data-testid="manuscript-error">
        <ApiErrorBanner
          title="Manoscritto non disponibile"
          message={error}
          onRetry={() => setReloadToken((n) => n + 1)}
          testId="manuscript-error-banner"
        />
      </div>
    );
  }

  return (
    <div
      data-testid="manuscript-workspace"
      className={cn("flex h-[calc(100vh-8rem)] min-h-[480px] flex-col md:flex-row", className)}
    >
      <div className="flex items-center gap-2 border-b border-border px-3 py-2 md:hidden">
        <button
          type="button"
          onClick={() => setShowTocMobile((open) => !open)}
          className="rounded-md border border-border px-3 py-1.5 text-sm font-medium text-ink"
        >
          Indice
        </button>
      </div>

      <div
        className={cn(
          "w-full shrink-0 md:block md:w-[300px]",
          showTocMobile ? "block" : "hidden"
        )}
      >
        <ManuscriptToc
          outline={outline}
          activeChapterId={activeChapterId}
          onSelectChapter={navigateChapter}
          className="h-full max-h-[40vh] md:max-h-none"
        />
      </div>

      <ManuscriptReader
        chapter={activeChapter}
        prevId={prevId}
        nextId={nextId}
        emptyThesis={orderedIds.length === 0}
        emptyMessage="Nessun capitolo strutturato"
        emptyHint="Aggiungi capitoli con titoli Cap. N o §N.x in Writing."
        onNavigate={navigateChapter}
        className="min-w-0 flex-1"
      />
    </div>
  );
}
