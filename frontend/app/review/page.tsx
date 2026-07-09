import { Suspense } from "react";

import { ReviewMode } from "@/components/review/ReviewMode";
import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";
import { ContextApiError } from "@/lib/contextClient";
import { loadContext } from "@/lib/contextLoad";

function contextErrorMessage(err: unknown): string {
  if (err instanceof ContextApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Contesto revisione non disponibile";
}

export default async function ReviewPage() {
  try {
    const context = await loadContext({ surface: "writing" });

    return (
      <Suspense
        fallback={
          <p className="p-6 text-sm text-ink-muted">Caricamento workspace revisione…</p>
        }
      >
        <ReviewMode contextPacket={context} />
      </Suspense>
    );
  } catch (err) {
    return (
      <div className="space-y-4 p-6" data-testid="review-context-error">
        <h1 className="text-xl font-semibold text-ink">Revisione</h1>
        <ApiErrorBanner
          title="Contesto non disponibile"
          message={contextErrorMessage(err)}
          backHref="/"
          backLabel="← Torna alla Home"
          testId="review-context-error-banner"
        />
      </div>
    );
  }
}
