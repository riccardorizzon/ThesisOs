import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";
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
      <ApiErrorBanner
        className="mt-4"
        title="Impossibile caricare le fonti"
        message={message}
        backHref={backHref}
        backLabel="← Torna a Sources"
        testId="sources-error-banner"
      />
    </div>
  );
}
