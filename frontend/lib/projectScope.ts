/**
 * Frontend project-scope injection (ADR-0047).
 * Layer: Business (Product Plane)
 *
 * Single place where API clients resolve "which thesis": explicit value wins,
 * otherwise the active project from localStorage (SSR-safe: Default Thesis on
 * the server — SSR pages pass the cookie-derived id explicitly).
 */

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
