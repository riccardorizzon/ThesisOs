"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import { KnowledgeConceptCard } from "@/components/knowledge/explorer/KnowledgeConceptCard";
import { KnowledgeExplorerFilters } from "@/components/knowledge/explorer/KnowledgeExplorerFilters";
import type { ExplorerFilterState } from "@/components/knowledge/explorer/explorerTypes";
import { cn } from "@/lib/cn";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

export type KnowledgeExplorerProps = {
  concepts: KnowledgeObjectEnvelope[];
  className?: string;
};

function applyExplorerFilters(
  concepts: KnowledgeObjectEnvelope[],
  filter: ExplorerFilterState
): KnowledgeObjectEnvelope[] {
  let list = concepts.filter((c) => c.knowledge_state !== "deprecated");

  if (!filter.showCandidates) {
    list = list.filter((c) => c.knowledge_state !== "candidate");
  }
  if (filter.coreOnly) {
    list = list.filter((c) => c.is_core);
  }
  if (filter.knowledgeState !== "all") {
    list = list.filter((c) => c.knowledge_state === filter.knowledgeState);
  }
  if (filter.confidence !== "all") {
    list = list.filter((c) => c.confidence === filter.confidence);
  }
  return list;
}

export function KnowledgeExplorer({
  concepts,
  className,
}: KnowledgeExplorerProps) {
  const [filter, setFilter] = useState<ExplorerFilterState>({
    knowledgeState: "all",
    coreOnly: false,
    confidence: "all",
    showCandidates: false,
  });

  const filtered = useMemo(
    () => applyExplorerFilters(concepts, filter),
    [concepts, filter]
  );

  const featured = concepts.find((c) => c.is_core && c.slug === "stigmata");
  const gridConcepts = useMemo(
    () =>
      featured != null
        ? filtered.filter((c) => c.slug !== featured.slug)
        : filtered,
    [filtered, featured]
  );

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Knowledge
        </h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          Cosa sa la tua ricerca — concetti, relazioni e ponti verso le fonti.
        </p>
      </header>

      {featured != null && (
        <section
          className="mb-8 rounded-lg border border-accent/20 bg-accent-subtle/30 p-4"
          aria-label="Concetto di ancoraggio"
        >
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">
            Concetto di ancoraggio
          </p>
          <KnowledgeConceptCard concept={featured} className="mt-3" />
        </section>
      )}

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <KnowledgeExplorerFilters value={filter} onChange={setFilter} />

        <section className="min-w-0 flex-1" aria-labelledby="knowledge-grid-heading">
          <h2
            id="knowledge-grid-heading"
            className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
          >
            Concetti del corpus
          </h2>
          {gridConcepts.length > 0 ? (
            <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {gridConcepts.map((concept) => (
                <li key={concept.id}>
                  <KnowledgeConceptCard concept={concept} />
                </li>
              ))}
            </ul>
          ) : (
            <div className="rounded-md border border-dashed border-border bg-surface-muted p-8 text-center">
              <p className="text-sm text-ink-muted">
                Nessun concetto con questo criterio. Modifica i filtri o mostra i
                candidati.
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
          Ogni concetto è ancorato alle fonti in{" "}
          <Link
            href="/sources"
            className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
          >
            Sources
          </Link>
          .
        </p>
      </nav>
    </div>
  );
}
