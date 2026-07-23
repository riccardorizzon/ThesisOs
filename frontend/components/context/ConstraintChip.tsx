import { cn } from "@/lib/cn";

export type ConstraintChipProps = {
  constraint: string;
  className?: string;
};

export function parseCorpusConstraint(constraint: string): {
  code: string;
  label: string;
} {
  const sep = constraint.indexOf(": ");
  if (sep === -1) {
    return { code: constraint, label: constraint };
  }
  return {
    code: constraint.slice(0, sep),
    label: constraint.slice(sep + 2),
  };
}

/**
 * Corpus exclusion indicator — CORPUS-02/03 from ContextPacket.
 * Layer: Business (Product Plane)
 */
export function ConstraintChip({ constraint, className }: ConstraintChipProps) {
  const { code, label } = parseCorpusConstraint(constraint);

  return (
    <span
      className={cn(
        "inline-flex max-w-full items-center gap-1 rounded-full border border-warning/30 bg-warning/10 px-2 py-0.5 text-xs font-medium text-warning",
        className
      )}
      title={label}
      data-testid={`constraint-chip-${code}`}
    >
      <span className="shrink-0 font-semibold">{code}</span>
      <span className="truncate text-ink-muted">{label}</span>
    </span>
  );
}
