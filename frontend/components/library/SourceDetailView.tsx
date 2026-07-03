import Link from "next/link";
import { EntityCard } from "@/components/EntityCard";
import {
  getConceptById,
  sourceStatusMeta,
  type LibraryConcept,
  type LibrarySource,
} from "@/lib/libraryStub";
import { cn } from "@/lib/cn";

export type SourceDetailViewProps = {
  source: LibrarySource;
  className?: string;
};

/**
 * Source detail stub — metadata + related concepts.
 * Layer: Business (Product Plane)
 */
export function SourceDetailView({ source, className }: SourceDetailViewProps) {
  const relatedConcepts = source.relatedConceptIds
    .map((id) => getConceptById(id))
    .filter((c): c is LibraryConcept => c != null);

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <nav aria-label="Breadcrumb" className="mb-6">
        <Link
          href="/sources"
          className="text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Sources
        </Link>
      </nav>

      <header className="mb-8 rounded-lg border border-border bg-surface p-6 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          Fonte · {sourceStatusMeta(source.status)}
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">
          {source.title}
        </h1>
        {source.subtitle != null && (
          <p className="mt-1 text-sm text-ink-muted">{source.subtitle}</p>
        )}
        {source.meta != null && (
          <p className="mt-2 text-xs text-ink-subtle">{source.meta}</p>
        )}
        <p className="mt-4 text-sm leading-relaxed text-ink-muted">
          Scheda fonte PX-1 — metadati completi, estratti e annotazioni arrivano
          con PX-3.
        </p>
      </header>

      <section aria-labelledby="source-concepts-heading">
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
