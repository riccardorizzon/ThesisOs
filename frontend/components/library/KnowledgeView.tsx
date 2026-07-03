"use client";

import Link from "next/link";
import { EntityCard } from "@/components/EntityCard";
import type { LibraryConcept } from "@/lib/libraryStub";
import { cn } from "@/lib/cn";

export type KnowledgeViewProps = {
  concepts: LibraryConcept[];
  className?: string;
};

/**
 * Knowledge explorer — concept cards stub (PX-4 graph deferred).
 * Layer: Business (Product Plane)
 */
export function KnowledgeView({ concepts, className }: KnowledgeViewProps) {
  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Knowledge
        </h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          Spiega questa tesi — definizioni, sostenitori, critici e decisioni
          collegate alle fonti del corpus.
        </p>
      </header>

      <section aria-labelledby="knowledge-explorer-heading">
        <h2
          id="knowledge-explorer-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Concetti del corpus
        </h2>
        {concepts.length > 0 ? (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {concepts.map((concept) => (
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
          <div className="rounded-md border border-dashed border-border bg-surface-muted p-8 text-center">
            <p className="text-sm text-ink-muted">
              Nessun concetto ancora definito.
            </p>
          </div>
        )}
      </section>

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
          . Mappa interattiva in{" "}
          <Link
            href="/research"
            className="font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
          >
            Research
          </Link>{" "}
          (PX-5).
        </p>
      </nav>
    </div>
  );
}
