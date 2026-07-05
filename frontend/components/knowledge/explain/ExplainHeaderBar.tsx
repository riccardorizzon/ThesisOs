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
      <h1 className="mt-2 text-2xl font-semibold tracking-tight text-ink">
        {header.title}
      </h1>
      {header.subtitle != null && header.subtitle !== "" && (
        <p className="mt-1 text-sm text-ink-muted">{header.subtitle}</p>
      )}
    </header>
  );
}
