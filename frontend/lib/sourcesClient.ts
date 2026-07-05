import type { ConfidenceLevel, KnowledgeState } from "@/lib/knowledgeTypes";
import type { SourceListResponse } from "@/lib/sourcesTypes";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEFAULT_PROJECT = "thesis-agent";

export async function listSources(
  options: {
    projectId?: string;
    query?: string;
    state?: KnowledgeState;
    confidence?: ConfidenceLevel;
    includeDeprecated?: boolean;
  } = {}
): Promise<SourceListResponse> {
  const projectId = options.projectId ?? DEFAULT_PROJECT;
  const params = new URLSearchParams();
  if (options.query) params.set("q", options.query);
  if (options.state) params.set("state", options.state);
  if (options.confidence) params.set("confidence", options.confidence);
  if (options.includeDeprecated) params.set("include_deprecated", "true");

  const qs = params.toString();
  const url = `${BASE}/projects/${projectId}/sources${qs ? `?${qs}` : ""}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Sources list failed: ${res.status}`);
  }
  return res.json() as Promise<SourceListResponse>;
}
