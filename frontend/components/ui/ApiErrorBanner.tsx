"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { cn } from "@/lib/cn";

export type ApiErrorBannerProps = {
  title: string;
  message: string;
  onRetry?: () => void;
  backHref?: string;
  backLabel?: string;
  className?: string;
  testId?: string;
};

/**
 * Consistent API/load error surface with retry — M7.2 Error UX track.
 */
export function ApiErrorBanner({
  title,
  message,
  onRetry,
  backHref,
  backLabel = "← Indietro",
  className,
  testId = "api-error-banner",
}: ApiErrorBannerProps) {
  const router = useRouter();

  function handleRetry() {
    if (onRetry) {
      onRetry();
    } else {
      router.refresh();
    }
  }

  return (
    <div
      className={cn(
        "rounded-lg border border-danger/30 bg-danger/10 px-4 py-6",
        className
      )}
      role="alert"
      data-testid={testId}
    >
      <p className="text-sm font-medium text-danger">{title}</p>
      <p className="mt-2 text-sm text-danger" data-testid={`${testId}-message`}>
        {message}
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleRetry}
          className="rounded-md bg-danger px-3 py-1.5 text-sm font-medium text-ink-inverse hover:bg-danger/90 cursor-pointer"
          data-testid={`${testId}-retry`}
        >
          Riprova
        </button>
        {backHref ? (
          <Link
            href={backHref}
            className="text-sm font-medium text-danger underline-offset-2 hover:underline cursor-pointer"
          >
            {backLabel}
          </Link>
        ) : null}
      </div>
    </div>
  );
}
