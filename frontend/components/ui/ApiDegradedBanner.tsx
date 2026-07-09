"use client";

import { cn } from "@/lib/cn";

export type ApiDegradedBannerProps = {
  message: string;
  title?: string;
  className?: string;
  testId?: string;
};

/**
 * Non-blocking load degradation — Error Contract v1 (Important / Level 2).
 * Distinguishes "API unavailable" from valid empty data.
 */
export function ApiDegradedBanner({
  message,
  title = "Alcuni dati non sono disponibili",
  className,
  testId = "api-degraded-banner",
}: ApiDegradedBannerProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-warning/40 bg-warning/10 px-4 py-3",
        className
      )}
      role="status"
      data-testid={testId}
    >
      <p className="text-sm font-medium text-warning">{title}</p>
      <p className="mt-1 text-sm text-ink-muted" data-testid={`${testId}-message`}>
        {message}
      </p>
    </div>
  );
}
