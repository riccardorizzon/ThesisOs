import Link from "next/link";

import {
  KnowledgeConfidenceChip,
  KnowledgeLifecycleBadge,
} from "@/components/knowledge/shared/KnowledgeBadges";
import { cn } from "@/lib/cn";
import type { ConceptHeaderEnvelope } from "@/lib/knowledgeTypes";

export type ExplainHeaderBarProps = {
  header: ConceptHeaderEnvelope;
  className?: string;
};

/** Explain Page region A — header bar (PX3-EWO-005/006). */
export function ExplainHeaderBar({ header, className }: ExplainHeaderBarProps) {
  const graphHref = `/knowledge/graph?focus=${encodeURIComponent(header.slug)}&depth=1`;

  return (
    <header
      className={cn(
        "sticky top-0 z-10 border-b border-border bg-surface/95 backdrop-blur-sm px-1 py-4",
        className
      )}
      data-testid="explain-region-a"
    >
      <div className="flex flex-wrap items-center gap-2">
        {header.is_core && (
          <span className="rounded-full bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent">
            Core
          </span>
        )}
        <KnowledgeLifecycleBadge state={header.knowledge_state} />
        <KnowledgeConfidenceChip level={header.confidence} />
      </div>
      <div className="mt-3 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">
            {header.title}
          </h1>
          {header.subtitle != null && header.subtitle !== "" && (
            <p className="mt-1 text-sm text-ink-muted">{header.subtitle}</p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            href={graphHref}
            className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:border-accent hover:text-accent"
            data-testid="explain-grafo-link"
          >
            Grafo
          </Link>
        </div>
      </div>
    </header>
  );
}
