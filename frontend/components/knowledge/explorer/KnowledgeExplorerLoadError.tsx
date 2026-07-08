import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";
import { cn } from "@/lib/cn";

export type KnowledgeExplorerLoadErrorProps = {
  message: string;
  className?: string;
};

export function KnowledgeExplorerLoadError({
  message,
  className,
}: KnowledgeExplorerLoadErrorProps) {
  return (
    <div className={cn("mx-auto max-w-content", className)}>
      <header className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          Knowledge
        </h1>
        <p className="mt-1 max-w-prose text-sm text-ink-muted">
          Cosa sa la tua ricerca — concetti, relazioni e ponti verso le fonti.
        </p>
      </header>

      <ApiErrorBanner
        title="Impossibile caricare i concetti"
        message={message}
        backHref="/"
        backLabel="← Torna alla Home"
        testId="knowledge-load-error"
      />
    </div>
  );
}
