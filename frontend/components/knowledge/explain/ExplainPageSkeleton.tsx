import { cn } from "@/lib/cn";

export type ExplainPageSkeletonProps = {
  className?: string;
};

/** Explain Page loading state — region skeletons top→bottom (spec §9.16). */
export function ExplainPageSkeleton({ className }: ExplainPageSkeletonProps) {
  return (
    <div
      className={cn("mx-auto max-w-content animate-pulse space-y-6", className)}
      data-testid="explain-loading"
      aria-busy="true"
      aria-label="Caricamento concetto"
    >
      <div className="h-24 rounded-lg bg-surface-muted" />
      <div className="h-40 rounded-lg bg-surface-muted" />
    </div>
  );
}
