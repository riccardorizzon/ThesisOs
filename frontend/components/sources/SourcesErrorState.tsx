import Link from "next/link";

import { cn } from "@/lib/cn";

export type SourcesErrorStateProps = {
  title: string;
  message: string;
  chapterContext?: string;
  className?: string;
};

export function SourcesErrorState({
  title,
  message,
  chapterContext,
  className,
}: SourcesErrorStateProps) {
  const backHref = chapterContext
    ? `/sources?chapter=${chapterContext}`
    : "/sources";

  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <h1 className="text-2xl font-semibold text-ink">{title}</h1>
      <p className="mt-2 text-sm text-ink-muted" data-testid="sources-error-message">
        {message}
      </p>
      <Link
        href={backHref}
        className="mt-4 inline-block text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
      >
        ← Torna a Sources
      </Link>
    </div>
  );
}
