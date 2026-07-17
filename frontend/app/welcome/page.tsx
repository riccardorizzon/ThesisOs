"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/cn";
import { createProject } from "@/lib/projectsClient";
import {
  saveProjectPrefs,
  setActiveProjectId,
} from "@/lib/projectPrefs";
import {
  markWelcomeComplete,
  setWorkspaceMode,
} from "@/lib/workspacePrefs";

const DEMO_THESIS_PROJECT_ID = "demo-thesis";

export default function WelcomePage() {
  const router = useRouter();
  const [busy, setBusy] = useState<"personal" | "demo" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startPersonal = async () => {
    setBusy("personal");
    setError(null);
    try {
      const stamp = new Date().toISOString().slice(0, 10);
      const created = await createProject(`Nuova tesi ${stamp}`);
      setActiveProjectId(created.id);
      saveProjectPrefs({
        displayName: created.display_name,
        citationStyle: "author-date",
        exportFormat: "bibtex",
      });
      setWorkspaceMode("personal");
      markWelcomeComplete();
      router.push("/");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Impossibile creare il nuovo progetto."
      );
      setBusy(null);
    }
  };

  const startDemo = () => {
    setBusy("demo");
    setError(null);
    setActiveProjectId(DEMO_THESIS_PROJECT_ID);
    saveProjectPrefs({
      displayName: "Progetto dimostrativo",
      citationStyle: "author-date",
      exportFormat: "bibtex",
    });
    setWorkspaceMode("demo");
    markWelcomeComplete();
    router.push("/");
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

        {error ? (
          <p
            className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900"
            data-testid="welcome-error"
            role="alert"
          >
            {error}
          </p>
        ) : null}

        <div className="mt-10 grid gap-4 text-left sm:grid-cols-2">
          <button
            type="button"
            onClick={() => void startPersonal()}
            disabled={busy !== null}
            className={cn(
              "rounded-lg border border-border bg-surface p-6 text-left shadow-sm transition-colors",
              "hover:border-border-strong hover:bg-surface-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
              "disabled:opacity-60"
            )}
            data-testid="welcome-new-thesis"
          >
            <h2 className="text-lg font-semibold">Nuova tesi</h2>
            <p className="mt-1 text-sm text-ink-muted">
              {busy === "personal"
                ? "Creazione progetto isolato…"
                : "Crea un nuovo project id — workspace vuoto, nessun testo precaricato."}
            </p>
          </button>

          <button
            type="button"
            onClick={startDemo}
            disabled={busy !== null}
            className={cn(
              "rounded-lg border border-dashed border-border bg-surface p-6 text-left shadow-sm transition-colors",
              "hover:border-border-strong hover:bg-surface-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
              "disabled:opacity-60"
            )}
            data-testid="welcome-explore-demo"
          >
            <h2 className="text-lg font-semibold">Esplora demo</h2>
            <p className="mt-1 text-sm text-ink-muted">
              Forza il progetto {DEMO_THESIS_PROJECT_ID} con contenuti di dimostrazione.
            </p>
          </button>
        </div>
      </div>
    </main>
  );
}
