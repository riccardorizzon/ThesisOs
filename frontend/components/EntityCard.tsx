import Link from "next/link";
import { cn } from "@/lib/cn";

export type EntityType = "chapter" | "source" | "concept" | "decision";

const ENTITY_LABELS: Record<EntityType, string> = {
  chapter: "Capitolo",
  source: "Fonte",
  concept: "Concetto",
  decision: "Decisione",
};

export type EntityCardProps = {
  entityType: EntityType;
  title: string;
  subtitle?: string;
  meta?: string;
  href?: string;
  className?: string;
};

/**
 * Entity summary card — stub for Home feed, Knowledge, Sources lists.
 * Layer: Business (Product Plane)
 */
export function EntityCard({
  entityType,
  title,
  subtitle,
  meta,
  href,
  className,
}: EntityCardProps) {
  const body = (
    <>
      <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
        {ENTITY_LABELS[entityType]}
      </span>
      <span className="mt-1 block text-sm font-semibold text-ink">{title}</span>
      {subtitle != null && (
        <span className="mt-0.5 block text-sm text-ink-muted">{subtitle}</span>
      )}
      {meta != null && (
        <span className="mt-2 block text-xs text-ink-subtle">{meta}</span>
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
      <Link href={href} className={classes}>
        {body}
      </Link>
    );
  }

  return <article className={classes}>{body}</article>;
}
