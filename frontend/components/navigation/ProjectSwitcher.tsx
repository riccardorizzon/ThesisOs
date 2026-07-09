"use client";

import { useEffect, useState } from "react";
import { setActiveProjectId, getActiveProjectId } from "@/lib/projectPrefs";
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
    window.location.reload();
  };

  const handleCreate = async () => {
    const name = window.prompt("Nome nuovo progetto");
    if (!name?.trim()) return;
    const created = await createProject(name.trim());
    const items = await listProjects();
    setProjects(items);
    handleSelect(created.id);
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
                <span className="block font-mono text-xs text-ink-subtle">{p.id}</span>
              </button>
            </li>
          ))}
          <li className="border-t border-border">
            <button
              type="button"
              onClick={() => void handleCreate()}
              className="w-full px-3 py-2 text-left text-sm text-accent cursor-pointer"
            >
              + Nuovo progetto
            </button>
          </li>
        </ul>
      )}
    </div>
  );
}
