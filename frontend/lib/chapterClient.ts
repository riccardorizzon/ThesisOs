import { apiBaseUrl } from "@/lib/apiBase";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { getActiveProjectId } from "@/lib/projectPrefs";
import { withProject } from "@/lib/projectScope";
import type { ChapterListScope } from "@/lib/workspacePrefs";

export type ChapterStatus = "draft" | "review" | "approved" | "published";
export type ChapterChangeKind = "WRITE" | "EDIT" | "PROMOTE" | "MERGE" | "RESTORE";

export type Chapter = {
  id: string;
  project_id?: string;
  parent_id: string | null;
  order_index: number;
  title: string;
  status: ChapterStatus;
  content_md: string | null;
  summary: string | null;
  word_count: number;
  version: number;
  created_at: string;
  updated_at: string;
  deletable?: boolean;
};

export type ChapterVersion = {
  chapter_id: string;
  version: number;
  change_kind: ChapterChangeKind;
  title: string;
  status: string;
  content_md: string | null;
  summary: string | null;
  word_count: number;
  metadata: Record<string, unknown>;
  changed_at: string;
};

export type ChapterCreateInput = {
  title: string;
  project_id?: string;
  parent_id?: string | null;
  order_index?: number;
  status?: ChapterStatus;
  content_md?: string | null;
  summary?: string | null;
};

export type ChapterUpdateInput = {
  content_md?: string;
  title?: string | null;
  summary?: string | null;
  status?: ChapterStatus | null;
  expected_version: number;
};

export type ChapterListParams = {
  project_id?: string;
  parent_id?: string;
  q?: string;
  scope?: ChapterListScope;
};

export class ChapterApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ChapterApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${apiBaseUrl()}${path}`, { ...init, cache: "no-store" });
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as { code?: string; message?: string } | null;
    throw new ChapterApiError(r.status, body?.code ?? "unknown", body?.message ?? r.statusText);
  }
  if (r.status === 204) return undefined as T;
  return r.json() as Promise<T>;
}

function resolveListProjectId(projectId?: string): string {
  if (projectId && projectId.trim()) return projectId.trim();
  if (typeof window !== "undefined") return getActiveProjectId();
  return DEFAULT_PROJECT_ID;
}

function queryString(params?: ChapterListParams): string {
  const sp = new URLSearchParams();
  sp.set("project_id", resolveListProjectId(params?.project_id));
  if (params?.parent_id) sp.set("parent_id", params.parent_id);
  if (params?.q) sp.set("q", params.q);
  if (params?.scope) sp.set("scope", params.scope);
  return `?${sp.toString()}`;
}

export const chapterClient = {
  list(params?: ChapterListParams) {
    return request<Chapter[]>(`/chapters${queryString(params)}`);
  },
  get(id: string) {
    return request<Chapter>(withProject(`/chapters/${id}`));
  },
  create(input: ChapterCreateInput) {
    return request<Chapter>("/chapters", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
  },
  update(id: string, body: ChapterUpdateInput) {
    return request<Chapter>(withProject(`/chapters/${id}`), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
  listVersions(id: string) {
    return request<ChapterVersion[]>(withProject(`/chapters/${id}/versions`));
  },
  async exportMarkdown(id: string): Promise<Blob> {
    const r = await fetch(`${apiBaseUrl()}/export/chapters/${id}.md`, { cache: "no-store" });
    if (!r.ok) {
      const body = (await r.json().catch(() => null)) as { code?: string; message?: string } | null;
      throw new ChapterApiError(r.status, body?.code ?? "unknown", body?.message ?? r.statusText);
    }
    return r.blob();
  },
  reorder(orderedIds: string[]) {
    return request<Chapter[]>("/chapters/reorder", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ordered_ids: orderedIds }),
    });
  },
  delete(id: string) {
    return request<void>(withProject(`/chapters/${id}`), { method: "DELETE" });
  },
  copyDemoStructure(projectId?: string) {
    return request<{ created: Chapter[]; skipped_titles: string[] }>(
      withProject("/chapters/copy-demo-structure", projectId),
      { method: "POST" }
    );
  },
};
