"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { EntityCard } from "@/components/EntityCard";
import {
  LibraryFilterBar,
  type LibraryFilterValue,
} from "@/components/library/LibraryFilterBar";
import {
  sourceStatusMeta,
  type LibrarySource,
} from "@/lib/libraryStub";
import { cn } from "@/lib/cn";

export type SourcesViewProps = {
  sources: LibrarySource[];
  className?: string;
};

/**
 * Sources list — EntityCard grid with status filter stub.
 * Layer: Business (Product Plane)
 */
export function SourcesView({ sources, className }: SourcesViewProps) {
  const [filter, setFilter] = useState<LibraryFilterValue>("all");

  const filtered = useMemo(() => {
    if (filter === "all") return sources;
    return sources.filter((s) => s.status === filter);
  }, [sources, filter]);

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Sources
        </h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          La fonte come oggetto: metadati, annotazioni, estratti e collegamenti
          ai concetti del corpus.
        </p>
      </header>

      <section aria-labelledby="sources-filter-heading" className="mb-6">
        <h2
          id="sources-filter-heading"
          className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Filtra per stato
        </h2>
        <LibraryFilterBar value={filter} onChange={setFilter} />
      </section>

      <section aria-labelledby="sources-grid-heading">
        <h2 id="sources-grid-heading" className="sr-only">
          Elenco fonti
        </h2>
        {filtered.length > 0 ? (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((source) => (
              <li key={source.id}>
                <EntityCard
                  entityType="source"
                  title={source.title}
                  subtitle={source.subtitle}
                  meta={[source.meta, sourceStatusMeta(source.status)]
                    .filter(Boolean)
                    .join(" · ")}
                  href={`/sources/${source.id}`}
                />
              </li>
            ))}
          </ul>
        ) : (
          <div className="rounded-md border border-dashed border-border bg-surface-muted p-8 text-center">
            <p className="text-sm text-ink-muted">
              Nessuna fonte con questo stato. Prova un altro filtro.
            </p>
          </div>
        )}
      </section>

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
          . Import legacy:{" "}
          <Link
            href="/documents/upload"
            className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
          >
            upload documenti
          </Link>
          .
        </p>
      </nav>
    </div>
  );
}
