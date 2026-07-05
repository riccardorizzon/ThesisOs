import { cn } from "@/lib/cn";
import type { ChapterStatus } from "@/lib/chapterClient";
import { CHAPTER_STATUS_LABELS } from "@/components/writing/writingStub";

const STATUS_STYLES: Record<ChapterStatus, string> = {
  draft: "bg-surface-muted text-ink-muted",
  review: "bg-warning/10 text-warning",
  approved: "bg-success/10 text-success",
  published: "bg-accent-subtle text-accent",
};

export type StatusBadgeProps = {
  status: ChapterStatus;
  className?: string;
};

/**
 * Chapter lifecycle pill — Bozza / In revisione / Approvato (UI spec §5.2).
 */
export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
        STATUS_STYLES[status],
        className
      )}
      data-testid={`status-badge-${status}`}
    >
      {CHAPTER_STATUS_LABELS[status]}
    </span>
  );
}
