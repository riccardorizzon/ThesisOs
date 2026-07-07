import Link from "next/link";
import { Suspense } from "react";
import { WritingContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
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
        <p className="text-sm text-ink-muted" role="alert">
          {contextErrorMessage(err)}
        </p>
        <Link href="/" className="text-sm font-medium text-accent underline-offset-2 hover:underline">
          ← Torna alla Home
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <WritingContextBar packet={context} />
      <Suspense fallback={<p className="text-sm text-ink-muted">Caricamento workspace…</p>}>
        <WritingWorkspace contextPacket={context} />
      </Suspense>
    </div>
  );
}
