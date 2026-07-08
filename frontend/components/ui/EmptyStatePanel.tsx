import Link from "next/link";

import { cn } from "@/lib/cn";

export type EmptyStateAction = {
  href: string;
  label: string;
  variant?: "primary" | "secondary";
};

export type EmptyStatePanelProps = {
  title: string;
  description: string;
  actions?: EmptyStateAction[];
  className?: string;
  testId?: string;
};

/**
 * Actionable empty state — M7.2 Empty states track.
 */
export function EmptyStatePanel({
  title,
  description,
  actions = [],
  className,
  testId = "empty-state-panel",
}: EmptyStatePanelProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-dashed border-border bg-surface-muted p-10 text-center",
        className
      )}
      data-testid={testId}
    >
      <p className="text-sm font-medium text-ink">{title}</p>
      <p className="mt-2 text-sm text-ink-muted">{description}</p>
      {actions.length > 0 ? (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          {actions.map((action) => (
            <Link
              key={action.href}
              href={action.href}
              className={cn(
                "inline-flex rounded-md px-4 py-2 text-sm font-medium cursor-pointer",
                action.variant === "primary"
                  ? "bg-accent text-white hover:bg-accent/90"
                  : "border border-border bg-surface text-ink hover:bg-surface-muted"
              )}
            >
              {action.label}
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
