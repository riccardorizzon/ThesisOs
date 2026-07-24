import Link from "next/link";

import {
  KnowledgeConfidenceChip,
  KnowledgeLifecycleBadge,
} from "@/components/knowledge/shared/KnowledgeBadges";
import { cn } from "@/lib/cn";
import {
  KNOWLEDGE_TYPE_LABELS,
  type KnowledgeObjectEnvelope,
} from "@/lib/knowledgeTypes";

export type KnowledgeObjectCardProps = {
  object: KnowledgeObjectEnvelope;
  href?: string;
  className?: string;
};

function formatLinkCounts(object: KnowledgeObjectEnvelope): string | null {
  const { linked_counts: c } = object;
  const parts: string[] = [];
  if (c.sources > 0) parts.push(`${c.sources} fonti`);
  if (c.concepts > 0) parts.push(`${c.concepts} concetti`);
  if (c.chapters > 0) parts.push(`${c.chapters} capitoli`);
  return parts.length > 0 ? parts.join(" · ") : null;
}

/**
 * Shared Knowledge Object card — PP-4 envelope (PX3-EWO-001).
 */
export function KnowledgeObjectCard({
  object,
  href,
  className,
}: KnowledgeObjectCardProps) {
  const linkCounts = formatLinkCounts(object);
  const body = (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
          {KNOWLEDGE_TYPE_LABELS[object.type]}
        </span>
        {object.is_core && (
          <span className="rounded-full bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent">
            Core
          </span>
        )}
        <KnowledgeLifecycleBadge state={object.knowledge_state} />
        <KnowledgeConfidenceChip level={object.confidence} />
      </div>
      <h3 className="mt-2 text-sm font-semibold text-ink">{object.title}</h3>
      {object.subtitle != null && object.subtitle !== "" && (
        <p className="mt-0.5 text-sm text-ink-muted">{object.subtitle}</p>
      )}
      {object.summary != null && object.summary !== "" && (
        <p className="mt-2 line-clamp-2 text-xs text-ink-subtle">{object.summary}</p>
      )}
      {linkCounts != null && (
        <p className="mt-2 text-xs text-ink-subtle">{linkCounts}</p>
      )}
    </>
  );

  const classes = cn(
    "block rounded-md border border-border bg-surface p-4 shadow-sm transition-colors",
    href != null && "hover:border-border-strong hover:bg-surface-muted",
    className
  );

  if (href != null) {
    return (
      <Link
        href={href}
        prefetch={false}
        className={classes}
        data-testid={`knowledge-card-${object.slug}`}
      >
        {body}
      </Link>
    );
  }

  return (
    <article className={classes} data-testid={`knowledge-card-${object.slug}`}>
      {body}
    </article>
  );
}
