/**
 * Frontend project-scope injection (ADR-0047).
 * Layer: Business (Product Plane)
 *
 * Single place where API clients resolve "which thesis": explicit value wins,
 * otherwise the active project from localStorage (SSR-safe: Default Thesis on
 * the server — SSR pages pass the cookie-derived id explicitly).
 */

import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { getActiveProjectId } from "@/lib/projectPrefs";

export function activeProjectScope(explicit?: string | null): string {
  const value = explicit?.trim();
  if (value) return value;
  return getActiveProjectId();
}

/** Append `project_id` to a request path (handles existing query strings). */
export function withProject(path: string, explicit?: string | null): string {
  const param = `project_id=${encodeURIComponent(activeProjectScope(explicit))}`;
  return path.includes("?") ? `${path}&${param}` : `${path}?${param}`;
}

// ---------------------------------------------------------------------------
// Project-namespaced browser storage (ADR-0047 §8).
// Keys become `thesisos:{project_id}:{name}`. Pre-multi-thesis keys
// (`thesisos:{name}`) belong to the Default Thesis and are migrated once.
// ---------------------------------------------------------------------------

type StorageOptions = { session?: boolean; projectId?: string | null };

function storageArea(opts?: StorageOptions): Storage | null {
  if (typeof window === "undefined") return null;
  try {
    return opts?.session ? window.sessionStorage : window.localStorage;
  } catch {
    return null;
  }
}

export function projectStorageKey(name: string, explicit?: string | null): string {
  return `thesisos:${activeProjectScope(explicit)}:${name}`;
}

export function getProjectStorageItem(name: string, opts?: StorageOptions): string | null {
  const store = storageArea(opts);
  if (!store) return null;
  const pid = activeProjectScope(opts?.projectId);
  const key = `thesisos:${pid}:${name}`;
  const value = store.getItem(key);
  if (value !== null) return value;
  if (pid === DEFAULT_PROJECT_ID) {
    const legacyKey = `thesisos:${name}`;
    const legacy = store.getItem(legacyKey);
    if (legacy !== null) {
      store.setItem(key, legacy);
      store.removeItem(legacyKey);
      return legacy;
    }
  }
  return null;
}

export function setProjectStorageItem(
  name: string,
  value: string,
  opts?: StorageOptions
): void {
  const store = storageArea(opts);
  if (!store) return;
  store.setItem(projectStorageKey(name, opts?.projectId), value);
}

export function removeProjectStorageItem(name: string, opts?: StorageOptions): void {
  const store = storageArea(opts);
  if (!store) return;
  store.removeItem(projectStorageKey(name, opts?.projectId));
  if (activeProjectScope(opts?.projectId) === DEFAULT_PROJECT_ID) {
    store.removeItem(`thesisos:${name}`);
  }
}
