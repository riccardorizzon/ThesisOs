"use client";

import { useRouter } from "next/navigation";
import { cn } from "@/lib/cn";
import {
  markWelcomeComplete,
  setWorkspaceMode,
} from "@/lib/workspacePrefs";

export default function WelcomePage() {
  const router = useRouter();

  const startPersonal = () => {
    setWorkspaceMode("personal");
    markWelcomeComplete();
    router.push("/writing");
  };

  const startDemo = () => {
    setWorkspaceMode("demo");
    markWelcomeComplete();
    router.push("/writing");
  };

  return (
    <main
      className="flex min-h-screen flex-col items-center justify-center bg-bg px-4 py-12 text-ink"
      data-testid="welcome-page"
    >
      <div className="mx-auto w-full max-w-2xl text-center">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent">
          ThesisOS
        </p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">
          Inizia la tua tesi
        </h1>
        <p className="mt-2 text-sm text-ink-muted">
          Scegli come entrare — il tuo workspace personale è separato dalla demo.
        </p>

        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          <button
            type="button"
            onClick={startPersonal}
            className={cn(
              "rounded-lg border-2 border-accent bg-surface p-6 text-left shadow-sm transition-colors",
              "hover:bg-accent-subtle/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            )}
            data-testid="welcome-new-thesis"
          >
            <span className="inline-block rounded-full bg-accent px-2 py-0.5 text-xs font-medium text-white">
              Consigliato
            </span>
            <h2 className="mt-3 text-lg font-semibold">Nuova tesi</h2>
            <p className="mt-1 text-sm text-ink-muted">
              Inizia da zero con il tuo workspace personale — 0%, nessun testo
              precaricato.
            </p>
          </button>

          <button
            type="button"
            onClick={startDemo}
            className={cn(
              "rounded-lg border border-dashed border-border bg-surface p-6 text-left shadow-sm transition-colors",
              "hover:border-border-strong hover:bg-surface-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            )}
            data-testid="welcome-explore-demo"
          >
            <h2 className="text-lg font-semibold">Esplora demo</h2>
            <p className="mt-1 text-sm text-ink-muted">
              Vedi un esempio completo di tesi con contenuti di dimostrazione.
            </p>
          </button>
        </div>

        <p className="mt-8 text-xs text-ink-subtle">
          Questo è il tuo spazio — non un esempio altrui.
        </p>
      </div>
    </main>
  );
}
