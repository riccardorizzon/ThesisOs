"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import { EntityCard } from "@/components/EntityCard";
import { SourceReader } from "@/components/sources/SourceReader";
import { corpusClient } from "@/lib/corpusClient";
import {
  getConceptById,
  sourceStatusMeta,
  type LibraryConcept,
  type LibrarySource,
} from "@/lib/libraryStub";
import type { RelatedConceptRef, SourceListItem } from "@/lib/sourcesTypes";
import { cn } from "@/lib/cn";

export type SourceDetailViewProps = {
  source?: LibrarySource;
  sourceItem?: SourceListItem;
  chapterContext?: string;
  className?: string;
};

/**
 * Source detail — metadata, reader body, link-to-chapter.
 * Layer: Business (Product Plane)
 */
export function SourceDetailView({
  source,
  sourceItem,
  chapterContext,
  className,
}: SourceDetailViewProps) {
  const sourceId = sourceItem?.id ?? source?.id ?? "";
  const corpusSource = corpusClient.getById(sourceId);

  const relatedFromApi: RelatedConceptRef[] | undefined = sourceItem?.related_concepts;
  const relatedConcepts: Array<{ id: string; title: string; subtitle?: string; meta?: string }> =
    relatedFromApi && relatedFromApi.length > 0
      ? relatedFromApi.map((c) => ({
          id: c.slug,
          title: c.title,
          subtitle: undefined,
          meta: undefined,
        }))
      : (source?.relatedConceptIds ?? [])
          .map((id) => getConceptById(id))
          .filter((c): c is LibraryConcept => c != null);

  const displaySource = source ?? {
    id: sourceId,
    title: sourceItem?.title ?? sourceId,
    subtitle: sourceItem?.subtitle ?? "",
    meta: sourceItem?.summary ?? "",
    status: (sourceItem?.corpus_status as LibrarySource["status"]) ?? "approvata",
    relatedConceptIds: relatedFromApi?.map((c) => c.slug) ?? [],
  };

  const [linked, setLinked] = useState(
    chapterContext
      ? corpusClient.isLinkedToChapter(chapterContext, sourceId)
      : false
  );
  const [linkMessage, setLinkMessage] = useState<string | null>(null);

  const handleLinkToChapter = useCallback(() => {
    if (!chapterContext) return;
    corpusClient.linkToChapter(chapterContext, sourceId);
    setLinked(true);
    setLinkMessage("Fonte collegata al capitolo attivo.");
  }, [chapterContext, sourceId]);

  const backHref = chapterContext
    ? `/sources?chapter=${chapterContext}`
    : "/sources";

  if (!corpusSource) {
    return (
      <p className="text-sm text-ink-muted">Fonte non trovata o esclusa.</p>
    );
  }

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <nav aria-label="Breadcrumb" className="mb-6 flex flex-wrap items-center gap-3">
        <Link
          href={backHref}
          className="text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Sources
        </Link>
        {chapterContext && (
          <Link
            href={`/writing/${chapterContext}`}
            className="rounded-full border border-accent bg-accent-subtle px-3 py-1 text-xs font-medium text-accent hover:bg-accent/10 cursor-pointer"
            data-testid="return-to-writing-inline"
          >
            Torna a Scrittura
          </Link>
        )}
      </nav>

      {chapterContext && (
        <section
          aria-labelledby="link-chapter-heading"
          className="mb-6 rounded-lg border border-border bg-surface-muted p-4"
        >
          <h2
            id="link-chapter-heading"
            className="text-sm font-semibold text-ink"
          >
            Collegamento capitolo
          </h2>
          <p className="mt-1 text-xs text-ink-muted">
            Capitolo attivo: {chapterContext}
          </p>
          {linked ? (
            <p className="mt-2 text-sm text-success" data-testid="link-success">
              Fonte già collegata a questo capitolo.
            </p>
          ) : (
            <button
              type="button"
              onClick={handleLinkToChapter}
              className="mt-3 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-muted cursor-pointer"
              data-testid="link-to-chapter-btn"
            >
              Collega al capitolo
            </button>
          )}
          {linkMessage && !linked && (
            <p className="mt-2 text-sm text-success">{linkMessage}</p>
          )}
        </section>
      )}

      <SourceReader source={corpusSource} variant="full" chapterId={chapterContext} />

      <section aria-labelledby="source-concepts-heading" className="mt-10">
        <h2
          id="source-concepts-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Concetti collegati
        </h2>
        {relatedConcepts.length > 0 ? (
          <ul className="space-y-3">
            {relatedConcepts.map((concept) => (
              <li key={concept.id}>
                <EntityCard
                  entityType="concept"
                  title={concept.title}
                  subtitle={concept.subtitle}
                  meta={concept.meta}
                  href={`/knowledge/${concept.id}`}
                />
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-muted">
            Nessun concetto collegato a questa fonte.
          </p>
        )}
      </section>

      <nav
        aria-label="Collegamenti modulo"
        className="mt-10 rounded-lg border border-border bg-surface-muted p-4"
      >
        <p className="text-sm text-ink-muted">
          Stato bibliografico: {sourceStatusMeta(displaySource.status)}.
          Esplora tutti i concetti in{" "}
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
