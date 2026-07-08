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
        "rounded-lg border border-red-200 bg-red-50 px-4 py-6",
        className
      )}
      role="alert"
      data-testid={testId}
    >
      <p className="text-sm font-medium text-red-800">{title}</p>
      <p className="mt-2 text-sm text-red-700" data-testid={`${testId}-message`}>
        {message}
      </p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleRetry}
          className="rounded-md bg-red-800 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-900 cursor-pointer"
          data-testid={`${testId}-retry`}
        >
          Riprova
        </button>
        {backHref ? (
          <Link
            href={backHref}
            className="text-sm font-medium text-red-800 underline-offset-2 hover:underline cursor-pointer"
          >
            {backLabel}
          </Link>
        ) : null}
      </div>
    </div>
  );
}
