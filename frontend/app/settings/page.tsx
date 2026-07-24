"use client";

import { useEffect, useState } from "react";
import {
  getActiveProjectId,
  loadProjectPrefs,
  saveProjectPrefs,
  type ProjectPrefs,
} from "@/lib/projectPrefs";
import { renameProject } from "@/lib/projectsClient";
import { DeleteProjectPanel } from "@/components/settings/DeleteProjectPanel";

/** PX-6 settings depth — replaces M0 stub. */
export default function SettingsPage() {
  const [prefs, setPrefs] = useState<ProjectPrefs | null>(null);
  const [renameStatus, setRenameStatus] = useState<"idle" | "saved" | "error">(
    "idle"
  );

  useEffect(() => {
    setPrefs(loadProjectPrefs());
  }, []);

  const syncDisplayName = async () => {
    if (!prefs?.displayName.trim()) return;
    try {
      await renameProject(getActiveProjectId(), prefs.displayName.trim());
      setRenameStatus("saved");
    } catch {
      setRenameStatus("error");
    }
  };

  if (!prefs) {
    return (
      <section className="mx-auto max-w-2xl p-6">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="mt-2 text-sm text-ink-muted">Caricamento…</p>
      </section>
    );
  }

  const update = (patch: Partial<ProjectPrefs>) => {
    const next = { ...prefs, ...patch };
    setPrefs(next);
    saveProjectPrefs(next);
  };

  return (
    <section className="mx-auto max-w-2xl space-y-8 p-6" data-testid="settings-page">
      <header>
        <h1 className="text-2xl font-semibold text-ink">Settings</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Preferenze progetto e export (PX-6).
        </p>
      </header>

      <div className="space-y-4 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-ink">Progetto</h2>
        <label className="block text-xs text-ink-muted">
          Nome visualizzato
          <input
            type="text"
            value={prefs.displayName}
            onChange={(e) => {
              setRenameStatus("idle");
              update({ displayName: e.target.value });
            }}
            onBlur={() => void syncDisplayName()}
            className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
          />
        </label>
        {renameStatus === "saved" ? (
          <p className="text-xs text-success" role="status">
            Nome sincronizzato con il registro tesi.
          </p>
        ) : null}
        {renameStatus === "error" ? (
          <p className="text-xs text-warning" role="alert">
            Nome salvato solo in locale — registro non raggiungibile.
          </p>
        ) : null}
        <p className="text-xs text-ink-subtle">
          ID attivo: <span className="font-mono">{getActiveProjectId()}</span>
        </p>
      </div>

      <div className="space-y-4 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-ink">Citazioni</h2>
        <fieldset className="space-y-2 text-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="citationStyle"
              checked={prefs.citationStyle === "author-date"}
              onChange={() => update({ citationStyle: "author-date" })}
            />
            Autore-data (default)
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="citationStyle"
              checked={prefs.citationStyle === "apa"}
              onChange={() => update({ citationStyle: "apa" })}
            />
            APA (informativo)
          </label>
        </fieldset>
      </div>

      <div className="space-y-4 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-ink">Export</h2>
        <label className="block text-xs text-ink-muted">
          Formato bibliografia predefinito
          <select
            value={prefs.exportFormat}
            onChange={(e) =>
              update({ exportFormat: e.target.value as ProjectPrefs["exportFormat"] })
            }
            className="mt-1 w-full rounded-md border border-border px-3 py-2 text-sm"
          >
            <option value="bibtex">BibTeX</option>
            <option value="ris">RIS (futuro)</option>
          </select>
        </label>
      </div>

      <DeleteProjectPanel
        projectId={getActiveProjectId()}
        displayName={prefs.displayName}
      />
    </section>
  );
}
