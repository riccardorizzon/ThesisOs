"use client";

export type ReviewWorkflowStep = "select" | "compare" | "accept";

export type ReviewWorkflowStepsProps = {
  current: ReviewWorkflowStep;
  className?: string;
};

const STEPS: { id: ReviewWorkflowStep; label: string }[] = [
  { id: "select", label: "Seleziona" },
  { id: "compare", label: "Confronta" },
  { id: "accept", label: "Accetta" },
];

const STEP_INDEX: Record<ReviewWorkflowStep, number> = {
  select: 0,
  compare: 1,
  accept: 2,
};

/**
 * Revision workflow step indicator — select → compare → accept.
 * Layer: Business (Product Plane)
 */
export function ReviewWorkflowSteps({
  current,
  className,
}: ReviewWorkflowStepsProps) {
  const activeIndex = STEP_INDEX[current];

  return (
    <nav
      aria-label="Passi revisione"
      className={className}
    >
      <ol className="flex flex-wrap items-center gap-2 sm:gap-4">
        {STEPS.map((step, index) => {
          const isComplete = index < activeIndex;
          const isActive = index === activeIndex;

          return (
            <li key={step.id} className="flex items-center gap-2 sm:gap-4">
              <span
                className={[
                  "inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-medium",
                  isActive
                    ? "border-accent bg-accent-subtle text-accent"
                    : isComplete
                      ? "border-success bg-success/10 text-success"
                      : "border-border-strong bg-surface-muted text-ink-muted",
                ].join(" ")}
                aria-current={isActive ? "step" : undefined}
              >
                <span
                  className={[
                    "flex h-5 w-5 items-center justify-center rounded-full text-xs",
                    isActive
                      ? "bg-accent text-ink-inverse"
                      : isComplete
                        ? "bg-success text-ink-inverse"
                        : "bg-border-strong text-ink",
                  ].join(" ")}
                  aria-hidden
                >
                  {isComplete ? "✓" : index + 1}
                </span>
                {step.label}
              </span>
              {index < STEPS.length - 1 ? (
                <span
                  className="hidden text-ink-subtle sm:inline"
                  aria-hidden
                >
                  →
                </span>
              ) : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
