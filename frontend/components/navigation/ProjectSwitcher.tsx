"use client";

import { useEffect, useState } from "react";
import { setActiveProjectId, getActiveProjectId, saveProjectPrefs } from "@/lib/projectPrefs";
import { createProject, listProjects, type ProjectEntry } from "@/lib/projectsClient";
import { ApiDegradedBanner } from "@/components/ui/ApiDegradedBanner";

/**
 * PX-6 project switcher — multi-project selection with persistence.
 * Layer: Business (Product Plane)
 */
export function ProjectSwitcher() {
  const [projects, setProjects] = useState<ProjectEntry[]>([]);
  const [activeId, setActiveId] = useState("thesis-agent");
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);
  const [projectsLoadError, setProjectsLoadError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const items = await listProjects();
        if (!active) return;
        setProjects(items);
        setActiveId(getActiveProjectId());
        setProjectsLoadError(null);
      } catch (err) {
        if (!active) return;
        setProjects([]);
        setProjectsLoadError(
          err instanceof Error ? err.message : "Impossibile caricare i progetti."
        );
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const active = projects.find((p) => p.id === activeId) ?? projects[0];

  const handleSelect = (id: string) => {
    setActiveProjectId(id);
    setActiveId(id);
    setOpen(false);
    setCreating(false);
    window.location.reload();
  };

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name) {
      setCreateError("Inserisci un nome per il progetto.");
      return;
    }
    setCreateError(null);
    try {
      const created = await createProject(name);
      saveProjectPrefs({
        displayName: created.display_name,
        citationStyle: "author-date",
        exportFormat: "bibtex",
      });
      const items = await listProjects();
      setProjects(items);
      setNewName("");
      setCreating(false);
      handleSelect(created.id);
    } catch (err) {
      setCreateError(
        err instanceof Error ? err.message : "Creazione progetto fallita."
      );
    }
  };

  return (
    <div className="relative space-y-1">
      {projectsLoadError ? (
        <ApiDegradedBanner
          title="Progetti non disponibili"
          message={projectsLoadError}
          testId="project-switcher-degraded"
        />
      ) : null}
      <span className="text-xs font-medium uppercase tracking-wide text-ink-subtle">
        Progetto
      </span>
      <button
        type="button"
        aria-expanded={open}
        aria-haspopup="listbox"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between rounded-md border border-border bg-surface px-3 py-2 text-left text-sm font-medium text-ink shadow-sm cursor-pointer"
      >
        <span className="truncate">{active?.display_name ?? activeId}</span>
        <span className="ml-2 shrink-0 text-xs text-ink-subtle" aria-hidden>
          ▾
        </span>
      </button>
      {open && (
        <ul
          role="listbox"
          className="absolute z-20 mt-1 w-full rounded-md border border-border bg-surface py-1 shadow-lg"
        >
          {projects.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                role="option"
                aria-selected={p.id === activeId}
                onClick={() => handleSelect(p.id)}
                className="w-full px-3 py-2 text-left text-sm hover:bg-accent-subtle/30 cursor-pointer"
              >
                {p.display_name}
                {p.kind === "demo" ? (
                  <span className="ml-1 text-xs text-warning">(demo)</span>
                ) : null}
                <span className="block font-mono text-xs text-ink-subtle">{p.id}</span>
              </button>
            </li>
          ))}
          <li className="border-t border-border px-3 py-2">
            {creating ? (
              <div className="space-y-2" data-testid="project-create-form">
                <label className="block text-xs font-medium text-ink-muted" htmlFor="new-project-name">
                  Nome nuovo progetto
                </label>
                <input
                  id="new-project-name"
                  data-testid="project-create-input"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      void handleCreate();
                    }
                    if (e.key === "Escape") {
                      setCreating(false);
                      setCreateError(null);
                    }
                  }}
                  className="w-full rounded-md border border-border bg-bg px-2 py-1.5 text-sm text-ink"
                  placeholder="Es. Tesi STEM"
                  autoFocus
                />
                {createError ? (
                  <p className="text-xs text-warning" role="alert">
                    {createError}
                  </p>
                ) : null}
                <div className="flex gap-2">
                  <button
                    type="button"
                    data-testid="project-create-submit"
                    onClick={() => void handleCreate()}
                    className="rounded-md bg-accent px-2 py-1 text-xs font-medium text-ink-inverse"
                  >
                    Crea
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setCreating(false);
                      setCreateError(null);
                    }}
                    className="rounded-md border border-border px-2 py-1 text-xs text-ink-muted"
                  >
                    Annulla
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                data-testid="project-create-open"
                onClick={() => {
                  setCreating(true);
                  setCreateError(null);
                }}
                className="w-full text-left text-sm text-accent cursor-pointer"
              >
                + Nuovo progetto
              </button>
            )}
          </li>
        </ul>
      )}
    </div>
  );
}
