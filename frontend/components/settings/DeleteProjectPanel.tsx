"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { deleteProject } from "@/lib/projectsClient";
import {
  clearProjectBrowserState,
  setActiveProjectId,
} from "@/lib/projectPrefs";
import { setWorkspaceMode } from "@/lib/workspacePrefs";

type DeleteProjectPanelProps = {
  projectId: string;
  displayName: string;
};

const PROTECTED_PROJECTS = new Set(["thesis-agent", "demo-thesis"]);

export function DeleteProjectPanel({
  projectId,
  displayName,
}: DeleteProjectPanelProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (PROTECTED_PROJECTS.has(projectId)) return null;

  const close = () => {
    if (busy) return;
    setOpen(false);
    setConfirmation("");
    setError(null);
  };

  const handleDelete = async () => {
    if (confirmation !== projectId || busy) return;
    setBusy(true);
    setError(null);
    try {
      await deleteProject(projectId, confirmation);
      clearProjectBrowserState(projectId);
      setActiveProjectId("thesis-agent");
      setWorkspaceMode("personal");
      setOpen(false);
      router.replace("/");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Eliminazione non riuscita. Riprova."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="space-y-3 rounded-lg border border-danger/30 bg-danger/5 p-4">
      <div>
        <h2 className="text-sm font-semibold text-danger">Zona pericolosa</h2>
        <p className="mt-1 text-sm text-ink-muted">
          L’eliminazione rimuove definitivamente capitoli, fonti, note e conversazioni
          di <strong className="font-medium text-ink">{displayName}</strong>.
        </p>
      </div>
      <button
        type="button"
        className="rounded-md border border-danger px-3 py-2 text-sm font-medium text-danger hover:bg-danger/10"
        onClick={() => setOpen(true)}
      >
        Elimina definitivamente questa tesi
      </button>

      {open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-project-title"
        >
          <div className="w-full max-w-md rounded-lg border border-border bg-surface p-6 shadow-lg">
            <h2 id="delete-project-title" className="text-lg font-semibold text-ink">
              Eliminare definitivamente {displayName}?
            </h2>
            <p className="mt-2 text-sm text-ink-muted">
              Questa operazione non può essere annullata. Digita l’ID esatto per
              confermare.
            </p>
            <label className="mt-4 block text-sm font-medium text-ink">
              <span>{`Digita ${projectId} per confermare`}</span>
              <input
                type="text"
                value={confirmation}
                disabled={busy}
                onChange={(event) => setConfirmation(event.target.value)}
                className="mt-1 w-full rounded-md border border-border bg-bg px-3 py-2 font-mono text-sm"
                autoComplete="off"
              />
            </label>
            {error ? (
              <p className="mt-3 text-sm text-danger" role="alert">
                {error}
              </p>
            ) : null}
            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={close}
                className="rounded-md border border-border px-3 py-2 text-sm text-ink-muted"
              >
                Annulla
              </button>
              <button
                type="button"
                disabled={busy || confirmation !== projectId}
                onClick={() => void handleDelete()}
                className="rounded-md bg-danger px-3 py-2 text-sm font-medium text-ink-inverse disabled:opacity-50"
              >
                {busy ? "Eliminazione…" : "Conferma eliminazione definitiva"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
