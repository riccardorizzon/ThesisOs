import { Suspense } from "react";
import { WritingPageClient } from "@/components/writing/WritingPageClient";
import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";
import { WritingWorkspaceSkeleton } from "@/components/ui/PageSkeleton";
import { ContextApiError } from "@/lib/contextClient";
import { loadContext } from "@/lib/contextLoad";

function contextErrorMessage(err: unknown): string {
  if (err instanceof ContextApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Contesto di scrittura non disponibile";
}

export default async function WritingPage() {
  let context;
  try {
    context = await loadContext();
  } catch (err) {
    return (
      <div className="space-y-4" data-testid="writing-context-error">
        <h1 className="text-xl font-semibold text-ink">Scrittura</h1>
        <ApiErrorBanner
          title="Contesto non disponibile"
          message={contextErrorMessage(err)}
          backHref="/"
          backLabel="← Torna alla Home"
          testId="writing-context-error-banner"
        />
      </div>
    );
  }

  return (
    <Suspense fallback={<WritingWorkspaceSkeleton />}>
      <WritingPageClient context={context} />
    </Suspense>
  );
}
