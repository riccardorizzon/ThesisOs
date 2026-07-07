const STORAGE_KEY = "thesisos:active-project-id";
const PREFS_KEY = "thesisos:project-prefs";

export type ProjectPrefs = {
  displayName: string;
  citationStyle: "author-date" | "apa";
  exportFormat: "bibtex" | "ris";
};

const DEFAULT_PREFS: ProjectPrefs = {
  displayName: "Tesi di laurea",
  citationStyle: "author-date",
  exportFormat: "bibtex",
};

export function getActiveProjectId(): string {
  if (typeof window === "undefined") return "thesis-agent";
  return localStorage.getItem(STORAGE_KEY) ?? "thesis-agent";
}

export function setActiveProjectId(projectId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, projectId);
}

export function loadProjectPrefs(): ProjectPrefs {
  if (typeof window === "undefined") return DEFAULT_PREFS;
  try {
    const raw = localStorage.getItem(PREFS_KEY);
    if (!raw) return DEFAULT_PREFS;
    return { ...DEFAULT_PREFS, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_PREFS;
  }
}

export function saveProjectPrefs(prefs: ProjectPrefs): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}
