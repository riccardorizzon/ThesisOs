import Link from "next/link";

import { KnowledgeObjectCard } from "@/components/knowledge/shared";
import { cn } from "@/lib/cn";
import type { SourceListItem } from "@/lib/sourcesTypes";

export type SourceKnowledgeCardProps = {
  source: SourceListItem;
  href: string;
  className?: string;
};

export function SourceKnowledgeCard({
  source,
  href,
  className,
}: SourceKnowledgeCardProps) {
  return (
    <div className={cn("space-y-3", className)}>
      <KnowledgeObjectCard object={source} href={href} />
      {source.corpus_status === "esclusa" && (
        <span
          className="inline-flex rounded-full bg-warning/10 px-2 py-0.5 text-xs font-medium text-warning"
          data-testid="corpus-esclusa-badge"
        >
          Esclusa
        </span>
      )}
      {source.related_concepts.length > 0 && (
        <div className="flex flex-wrap gap-1.5 px-1" data-testid="concept-chips">
          {source.related_concepts.map((concept) => (
            <Link
              key={concept.id}
              href={`/knowledge/${concept.slug}`}
              className="rounded-full border border-border bg-surface-muted px-2 py-0.5 text-xs text-ink-muted hover:border-accent hover:text-accent"
            >
              {concept.title}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
