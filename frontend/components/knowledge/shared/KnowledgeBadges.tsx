import { cn } from "@/lib/cn";
import {
  CONFIDENCE_LABELS,
  KNOWLEDGE_STATE_LABELS,
  type ConfidenceLevel,
  type KnowledgeState,
} from "@/lib/knowledgeTypes";

const STATE_STYLES: Record<KnowledgeState, string> = {
  candidate: "bg-surface-muted text-ink-muted border-border",
  validated: "bg-success/10 text-success border-success/20",
  linked: "bg-accent-subtle text-accent border-accent/20",
  referenced: "bg-accent-subtle text-accent border-accent/30",
  deprecated: "bg-warning/10 text-warning border-warning/20",
};

const CONFIDENCE_STYLES: Record<ConfidenceLevel, string> = {
  alta: "bg-success/10 text-success",
  media: "bg-surface-muted text-ink-muted",
  bassa: "bg-warning/10 text-warning",
  non_valutata: "bg-surface-muted text-ink-subtle",
};

export type KnowledgeLifecycleBadgeProps = {
  state: KnowledgeState;
  className?: string;
};

export function KnowledgeLifecycleBadge({
  state,
  className,
}: KnowledgeLifecycleBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium",
        STATE_STYLES[state],
        className
      )}
      data-testid={`knowledge-state-${state}`}
    >
      {KNOWLEDGE_STATE_LABELS[state]}
    </span>
  );
}

export type KnowledgeConfidenceChipProps = {
  level: ConfidenceLevel;
  className?: string;
};

export function KnowledgeConfidenceChip({
  level,
  className,
}: KnowledgeConfidenceChipProps) {
  if (level === "non_valutata") return null;
  return (
    <span
      className={cn(
        "inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
        CONFIDENCE_STYLES[level],
        className
      )}
      data-testid={`confidence-${level}`}
    >
      {CONFIDENCE_LABELS[level]}
    </span>
  );
}
