import Link from "next/link";

import { KnowledgeObjectCard } from "@/components/knowledge/shared";
import { cn } from "@/lib/cn";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

export type KnowledgeConceptCardProps = {
  concept: KnowledgeObjectEnvelope;
  className?: string;
};

export function KnowledgeConceptCard({
  concept,
  className,
}: KnowledgeConceptCardProps) {
  const sourceCount = concept.linked_counts.sources;

  return (
    <article className={cn("space-y-3", className)} data-testid={`concept-card-${concept.slug}`}>
      <KnowledgeObjectCard
        object={concept}
        href={`/knowledge/${concept.slug}`}
      />
      <div className="flex flex-wrap items-center gap-2 px-1">
        <Link
          href={`/knowledge/${concept.slug}`}
          className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:border-accent hover:text-accent"
        >
          Apri
        </Link>
        <span
          className="rounded-md border border-dashed border-border px-3 py-1.5 text-xs text-ink-subtle"
          title="Grafo completo — wave successiva"
        >
          Grafo (PX-3+)
        </span>
        {sourceCount > 0 && (
          <Link
            href="/sources"
            className="text-xs text-accent hover:underline"
            data-testid={`concept-sources-link-${concept.slug}`}
          >
            {sourceCount} fonti in Sources
          </Link>
        )}
      </div>
    </article>
  );
}
