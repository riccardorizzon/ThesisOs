"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { chapterClient } from "@/lib/chapterClient";
import { createProject } from "@/lib/projectsClient";
import {
  getLastPersonalProjectId,
  saveProjectPrefs,
  setActiveProjectId,
} from "@/lib/projectPrefs";
import { setWorkspaceMode } from "@/lib/workspacePrefs";

export function DemoWorkspaceBanner() {
  const router = useRouter();
  const [copyOpen, setCopyOpen] = useState(false);
  const [copying, setCopying] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);

  const handleCreateEmpty = async () => {
    setCopying(true);
    setCopyError(null);
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
      router.push("/writing");
      router.refresh();
    } catch (err) {
      setCopyError(
        err instanceof Error
          ? err.message
          : "Impossibile creare il nuovo progetto."
      );
    } finally {
      setCopying(false);
    }
  };

  const handleCopy = async () => {
    setCopying(true);
    setCopyError(null);
    try {
      const targetProjectId = getLastPersonalProjectId();
      await chapterClient.copyDemoStructure(targetProjectId);
      setActiveProjectId(targetProjectId);
      setWorkspaceMode("personal");
      setCopyOpen(false);
      router.push("/writing");
      router.refresh();
    } catch (err) {
      setCopyError(
        err instanceof Error ? err.message : "Copia non riuscita. Riprova."
      );
    } finally {
      setCopying(false);
    }
  };

  return (
    <>
      <div
        className="mb-6 flex flex-wrap items-center gap-3 rounded-lg border border-warning/30 bg-warning/10 px-4 py-3"
        role="status"
        data-testid="demo-workspace-banner"
      >
        <p className="min-w-[12rem] flex-1 text-sm text-ink">
          <strong className="font-semibold">Workspace demo</strong>
          <span className="text-ink-muted">
            {" "}
            — stai esplorando un esempio, non la tua tesi.
          </span>
        </p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void handleCreateEmpty()}
            className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-ink hover:border-accent hover:text-accent cursor-pointer"
            data-testid="demo-create-empty-thesis"
          >
            Crea la tua tesi vuota
          </button>
          <button
            type="button"
            onClick={() => setCopyOpen(true)}
            className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-ink-inverse hover:opacity-90 cursor-pointer"
            data-testid="demo-copy-structure"
          >
            Copia struttura nel mio progetto
          </button>
        </div>
      </div>

      {copyOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="copy-structure-title"
          data-testid="copy-structure-dialog"
        >
          <div className="w-full max-w-md rounded-lg border border-border bg-surface p-6 shadow-lg">
            <h2
              id="copy-structure-title"
              className="text-lg font-semibold text-ink"
            >
              Copia struttura nel mio progetto
            </h2>
            <p className="mt-2 text-sm text-ink-muted">
              Copieremo solo i titoli dei capitoli della demo, senza il testo
              precaricato.
            </p>
            {copyError ? (
              <p className="mt-3 text-sm text-danger" role="alert">
                {copyError}
              </p>
            ) : null}
            <div className="mt-6 flex flex-wrap justify-end gap-2">
              <button
                type="button"
                onClick={() => setCopyOpen(false)}
                className="rounded-md border border-border px-3 py-1.5 text-sm font-medium text-ink-muted hover:bg-surface-muted cursor-pointer"
                disabled={copying}
              >
                Annulla
              </button>
              <button
                type="button"
                onClick={() => void handleCopy()}
                className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-ink-inverse hover:opacity-90 cursor-pointer disabled:opacity-60"
                disabled={copying}
                data-testid="copy-structure-confirm"
              >
                {copying ? "Copia in corso…" : "Copia e vai al mio workspace"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
