import { cn } from "@/lib/cn";

export type ExplainRegionWaitProps = {
  message?: string | null;
  className?: string;
};

/** Region B WAIT — halts autonomous progression (INV-R-16 observation, PX3-EWO-006). */
export function ExplainRegionWait({ message, className }: ExplainRegionWaitProps) {
  return (
    <section
      className={cn(
        "rounded-lg border border-dashed border-border bg-surface-muted p-6",
        className
      )}
      data-testid="explain-region-b-wait"
      aria-busy="true"
      aria-label="Definizione in attesa"
    >
      <p className="text-xs font-semibold uppercase tracking-wide text-ink-subtle">
        Definizione
      </p>
      <p className="mt-3 text-sm text-ink-muted">
        {message ?? "Caricamento in attesa di autorizzazione supervisor…"}
      </p>
      <div className="mt-4 h-16 animate-pulse rounded-md bg-surface" />
    </section>
  );
}
