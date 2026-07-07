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

      <div
        className="rounded-lg border border-red-200 bg-red-50 px-4 py-6 text-center"
        role="alert"
        data-testid="knowledge-load-error"
      >
        <p className="text-sm font-medium text-red-800">
          Impossibile caricare i concetti
        </p>
        <p className="mt-2 text-sm text-red-700">{message}</p>
        <p className="mt-3 text-xs text-red-600">
          Verifica che il backend sia in esecuzione e riprova.
        </p>
      </div>
    </div>
  );
}
