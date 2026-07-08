import type { ConfidenceLevel, KnowledgeState } from "@/lib/knowledgeTypes";
import type { SourceListItem, SourceListResponse } from "@/lib/sourcesTypes";

import { getActiveProjectId } from "@/lib/projectPrefs";
import { apiBaseUrl } from "@/lib/apiBase";

const DEFAULT_PROJECT = "thesis-agent";

function resolveProjectId(projectId?: string): string {
  if (projectId) return projectId;
  if (typeof window !== "undefined") return getActiveProjectId();
  return DEFAULT_PROJECT;
}

export async function listSources(
  options: {
    projectId?: string;
    query?: string;
    state?: KnowledgeState;
    confidence?: ConfidenceLevel;
    includeDeprecated?: boolean;
  } = {}
): Promise<SourceListResponse> {
  const projectId = resolveProjectId(options.projectId);
  const params = new URLSearchParams();
  if (options.query) params.set("q", options.query);
  if (options.state) params.set("state", options.state);
  if (options.confidence) params.set("confidence", options.confidence);
  if (options.includeDeprecated) params.set("include_deprecated", "true");

  const qs = params.toString();
  const base = apiBaseUrl();
  const url = `${base}/projects/${projectId}/sources${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(
      detail
        ? `Sources list failed (${res.status}): ${detail}`
        : `Sources list failed (${res.status})`
    );
  }
  return res.json() as Promise<SourceListResponse>;
}

export async function getSource(
  slug: string,
  projectId?: string
): Promise<SourceListItem> {
  const pid = resolveProjectId(projectId);
  const res = await fetch(
    `${apiBaseUrl()}/projects/${pid}/sources/${encodeURIComponent(slug)}`,
    { cache: "no-store" }
  );
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(
      detail
        ? `Source not found (${res.status}): ${detail}`
        : `Source not found: ${slug} (${res.status})`
    );
  }
  return res.json() as Promise<SourceListItem>;
}

export async function exportBibliography(
  projectId?: string
): Promise<Blob> {
  const pid = resolveProjectId(projectId);
  const res = await fetch(
    `${apiBaseUrl()}/projects/${pid}/sources/bibliography/export?format=bibtex`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error(`Bibliography export failed: ${res.status}`);
  return res.blob();
}
