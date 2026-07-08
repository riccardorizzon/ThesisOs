import Link from "next/link";
import { EntityCard } from "@/components/EntityCard";
import {
  sourceStatusMeta,
  type LibraryConcept,
  type LibrarySource,
} from "@/lib/libraryTypes";
import { cn } from "@/lib/cn";

export type KnowledgeDetailViewProps = {
  concept: LibraryConcept;
  relatedSources?: LibrarySource[];
  className?: string;
};

/**
 * Concept detail — definition + related sources.
 * Layer: Business (Product Plane)
 */
export function KnowledgeDetailView({
  concept,
  relatedSources: relatedSourcesProp,
  className,
}: KnowledgeDetailViewProps) {
  const relatedSources: LibrarySource[] =
    relatedSourcesProp ??
    concept.relatedSourceIds.map((id) => ({
      id,
      title: id,
      status: "candidata" as const,
      relatedConceptIds: [],
    }));

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <nav aria-label="Breadcrumb" className="mb-6">
        <Link
          href="/knowledge"
          className="text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Knowledge
        </Link>
      </nav>

      <header className="mb-8 rounded-lg border border-border bg-surface p-6 shadow-sm">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          Concetto
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">
          {concept.title}
        </h1>
        {concept.subtitle != null && (
          <p className="mt-1 text-sm text-ink-muted">{concept.subtitle}</p>
        )}
        {concept.definition != null && (
          <p className="mt-4 text-sm leading-relaxed text-ink-muted">
            {concept.definition}
          </p>
        )}
      </header>

      <section aria-labelledby="concept-sources-heading">
        <h2
          id="concept-sources-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide text-ink-subtle"
        >
          Fonti collegate
        </h2>
        {relatedSources.length > 0 ? (
          <ul className="space-y-3">
            {relatedSources.map((source) => (
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
          <p className="text-sm text-ink-muted">
            Nessuna fonte collegata a questo concetto.
          </p>
        )}
      </section>

      <nav
        aria-label="Collegamenti modulo"
        className="mt-10 rounded-lg border border-border bg-surface-muted p-4"
      >
        <p className="text-sm text-ink-muted">
          Consulta l&apos;intero corpus in{" "}
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
