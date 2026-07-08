import { cn } from "@/lib/cn";

export type PageSkeletonProps = {
  className?: string;
  /** Accessible label for the loading region */
  label?: string;
  testId?: string;
  /** Number of content block placeholders */
  blocks?: number;
};

/**
 * Generic module page loading skeleton — M7.2 Loading track.
 */
export function PageSkeleton({
  className,
  label = "Caricamento pagina",
  testId = "page-skeleton",
  blocks = 3,
}: PageSkeletonProps) {
  return (
    <div
      className={cn("mx-auto max-w-content animate-pulse space-y-6", className)}
      data-testid={testId}
      aria-busy="true"
      aria-label={label}
    >
      <div className="h-8 w-48 rounded bg-surface-muted" />
      <div className="h-4 w-72 max-w-full rounded bg-surface-muted" />
      {Array.from({ length: blocks }, (_, index) => (
        <div
          key={index}
          className={cn(
            "rounded-lg bg-surface-muted",
            index === 0 ? "h-32" : index === 1 ? "h-48" : "h-24"
          )}
        />
      ))}
    </div>
  );
}

/**
 * Three-panel Writing workspace skeleton.
 */
export function WritingWorkspaceSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse space-y-3", className)}
      data-testid="writing-workspace-skeleton"
      aria-busy="true"
      aria-label="Caricamento workspace di scrittura"
    >
      <div className="h-10 rounded-md bg-surface-muted" />
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)_minmax(0,1fr)]">
        <div className="hidden h-96 rounded-lg bg-surface-muted lg:block" />
        <div className="h-96 rounded-lg bg-surface-muted" />
        <div className="hidden h-96 rounded-lg bg-surface-muted lg:block" />
      </div>
    </div>
  );
}
