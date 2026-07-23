"use client";

import { useCallback, useState } from "react";
import Link from "next/link";

import { EntityCard } from "@/components/EntityCard";
import { SourceDeleteButton } from "@/components/sources/SourceDeleteButton";
import {
  KnowledgeConfidenceChip,
  KnowledgeLifecycleBadge,
} from "@/components/knowledge/shared/KnowledgeBadges";
import { corpusClient } from "@/lib/corpusClient";
import { isUserUploadedSource } from "@/lib/isUserUploadedSource";
import { KNOWLEDGE_TYPE_LABELS } from "@/lib/knowledgeTypes";
import { cn } from "@/lib/cn";
import type { SourceListItem } from "@/lib/sourcesTypes";

export type SourceApiDetailViewProps = {
  source: SourceListItem;
  chapterContext?: string;
  className?: string;
};

export function SourceApiDetailView({
  source,
  chapterContext,
  className,
}: SourceApiDetailViewProps) {
  const [linked, setLinked] = useState(
    chapterContext
      ? corpusClient.isLinkedToChapter(chapterContext, source.slug)
      : false
  );
  const [linkMessage, setLinkMessage] = useState<string | null>(null);

  const handleLinkToChapter = useCallback(() => {
    if (!chapterContext) return;
    corpusClient.linkToChapter(chapterContext, source.slug);
    setLinked(true);
    setLinkMessage("Fonte collegata al capitolo attivo.");
  }, [chapterContext, source.slug]);

  const backHref = chapterContext
    ? `/sources?chapter=${chapterContext}`
    : "/sources";

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
              className="mt-3 rounded-md bg-accent px-4 py-2 text-sm font-medium text-ink-inverse hover:bg-accent-muted cursor-pointer"
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

      <article className="rounded-lg border border-border bg-surface p-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
            {KNOWLEDGE_TYPE_LABELS.source}
          </span>
          {source.is_core && (
            <span className="rounded-full bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent">
              Core
            </span>
          )}
          <KnowledgeLifecycleBadge state={source.knowledge_state} />
          <KnowledgeConfidenceChip level={source.confidence} />
          {source.corpus_status === "esclusa" && (
            <span className="inline-flex rounded-full bg-warning/10 px-2 py-0.5 text-xs font-medium text-warning">
              Esclusa
            </span>
          )}
        </div>
        <h1 className="mt-3 text-2xl font-semibold text-ink">{source.title}</h1>
        {source.subtitle != null && source.subtitle !== "" && (
          <p className="mt-1 text-sm text-ink-muted">{source.subtitle}</p>
        )}
        {source.summary != null && source.summary !== "" && (
          <p className="mt-4 text-sm leading-relaxed text-ink">{source.summary}</p>
        )}
      </article>

      {isUserUploadedSource(source) && (
        <section className="mt-6" aria-label="Azioni fonte">
          <SourceDeleteButton
            slug={source.slug}
            title={source.title}
            redirectTo={backHref}
          />
        </section>
      )}

      <section aria-labelledby="source-concepts-heading" className="mt-10">
        <h2
          id="source-concepts-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Concetti collegati
        </h2>
        {source.related_concepts.length > 0 ? (
          <ul className="space-y-3">
            {source.related_concepts.map((concept) => (
              <li key={concept.id}>
                <EntityCard
                  entityType="concept"
                  title={concept.title}
                  href={`/knowledge/${concept.slug}`}
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
