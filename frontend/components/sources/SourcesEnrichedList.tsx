"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { EmptyStatePanel } from "@/components/ui/EmptyStatePanel";
import { SourcesFilterRail } from "@/components/sources/SourcesFilterRail";
import { BibliographyExportBar } from "@/components/sources/BibliographyExportBar";
import { SourceKnowledgeCard } from "@/components/sources/SourceKnowledgeCard";
import { cn } from "@/lib/cn";
import type { SourceListItem, SourcesFilterState } from "@/lib/sourcesTypes";

export type SourcesEnrichedListProps = {
  initialSources: SourceListItem[];
  chapterContext?: string;
  className?: string;
};

const SEARCH_DEBOUNCE_MS = 200;

function SourcesPageHeader() {
  return (
    <header className="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">Sources</h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          La fonte come oggetto knowledge: metadati, lifecycle e collegamenti ai
          concetti del corpus.
        </p>
      </div>
      <Link
        href="/sources/upload"
        className={cn(
          "inline-flex shrink-0 items-center gap-1.5 rounded-md bg-accent px-4 py-2 text-sm font-medium text-ink-inverse",
          "transition-colors duration-200 hover:bg-accent-muted",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent cursor-pointer"
        )}
        data-testid="sources-add-source-cta"
      >
        <span aria-hidden="true">+</span>
        Aggiungi fonte
      </Link>
    </header>
  );
}

function ReturnToWritingPill({ chapterId }: { chapterId: string }) {
  return (
    <Link
      href={`/writing/${chapterId}`}
      className={cn(
        "fixed bottom-6 right-6 z-40 rounded-full border border-accent bg-accent px-4 py-2 text-sm font-medium text-ink-inverse shadow-md",
        "hover:bg-accent-muted cursor-pointer",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      )}
      data-testid="return-to-writing-pill"
    >
      Torna a Scrittura
    </Link>
  );
}

function applyClientFilters(
  sources: SourceListItem[],
  filter: {
    query: string;
    knowledgeState: string;
    confidence: string;
    includeDeprecated: boolean;
  }
): SourceListItem[] {
  let list = sources;
  if (!filter.includeDeprecated) {
    list = list.filter((s) => s.knowledge_state !== "deprecated");
  }
  if (filter.knowledgeState !== "all") {
    list = list.filter((s) => s.knowledge_state === filter.knowledgeState);
  }
  if (filter.confidence !== "all") {
    list = list.filter((s) => s.confidence === filter.confidence);
  }
  const q = filter.query.trim().toLowerCase();
  if (!q) return list;
  return list.filter((s) => {
    const haystack = [s.title, s.subtitle, s.summary]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
}

export function SourcesEnrichedList({
  initialSources,
  chapterContext,
  className,
}: SourcesEnrichedListProps) {
  const [filter, setFilter] = useState<SourcesFilterState>({
    query: "",
    knowledgeState: "all",
    confidence: "all",
    includeDeprecated: false,
  });
  const [debouncedQuery, setDebouncedQuery] = useState("");

  useEffect(() => {
    const t = window.setTimeout(
      () => setDebouncedQuery(filter.query),
      SEARCH_DEBOUNCE_MS
    );
    return () => window.clearTimeout(t);
  }, [filter.query]);

  const filtered = useMemo(
    () =>
      applyClientFilters(initialSources, {
        ...filter,
        query: debouncedQuery,
      }),
    [initialSources, filter.knowledgeState, filter.confidence, filter.includeDeprecated, debouncedQuery]
  );

  const hrefForSource = (slug: string) => {
    const base = `/sources/${slug}`;
    return chapterContext ? `${base}?chapter=${chapterContext}` : base;
  };

  if (initialSources.length === 0) {
    return (
      <div className={cn("mx-auto max-w-content", className)}>
        {chapterContext && <ReturnToWritingPill chapterId={chapterContext} />}
        <SourcesPageHeader />
        <EmptyStatePanel
          title="Nessuna fonte ancora"
          description="Aggiungi la tua prima fonte per iniziare a costruire la tua knowledge."
          actions={[
            { href: "/sources/upload", label: "Aggiungi fonte", variant: "primary" },
            { href: "/knowledge", label: "Vai a Knowledge", variant: "secondary" },
          ]}
          testId="sources-corpus-empty"
        />
      </div>
    );
  }

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      {chapterContext && <ReturnToWritingPill chapterId={chapterContext} />}

      <SourcesPageHeader />

      <BibliographyExportBar />

      <div className="mb-6">
        <label htmlFor="sources-unified-search" className="sr-only">
          Cerca nel corpus
        </label>
        <input
          id="sources-unified-search"
          type="search"
          value={filter.query}
          onChange={(e) => setFilter((f) => ({ ...f, query: e.target.value }))}
          placeholder="Titolo, autore, anno…"
          className="w-full max-w-xl rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          data-testid="sources-search-input"
        />
      </div>

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <SourcesFilterRail value={filter} onChange={setFilter} />

        <section className="min-w-0 flex-1" aria-labelledby="sources-grid-heading">
          <h2 id="sources-grid-heading" className="sr-only">
            Elenco fonti
          </h2>
          {filtered.length > 0 ? (
            <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-2">
              {filtered.map((source) => (
                <li key={source.id}>
                  <SourceKnowledgeCard
                    source={source}
                    href={hrefForSource(source.slug)}
                  />
                </li>
              ))}
            </ul>
          ) : (
            <div className="rounded-md border border-dashed border-border bg-surface-muted p-8 text-center">
              <p className="text-sm text-ink-muted">
                Nessuna fonte con questo criterio. Prova un altro filtro o ricerca.
              </p>
            </div>
          )}
        </section>
      </div>

      <nav
        aria-label="Collegamenti modulo"
        className="mt-10 rounded-lg border border-border bg-surface-muted p-4"
      >
        <p className="text-sm text-ink-muted">
          Esplora i concetti collegati in{" "}
          <Link
            href="/knowledge"
            className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
          >
            Knowledge
          </Link>
          .
        </p>
      </nav>
    </div>
  );
}
