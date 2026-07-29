import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { getActiveProjectId } from "@/lib/projectPrefs";
import { withProject } from "@/lib/projectScope";
import type { Chapter } from "@/lib/chapterClient";
import { apiAuthHeaders } from "@/lib/apiAuth";
import { apiBaseUrl } from "@/lib/apiBase";

export type ProposalApiStatus = "pending" | "accepted" | "rejected";

export type ProposalApiRecord = {
  id: string;
  project_id: string;
  chapter_id: string;
  status: ProposalApiStatus;
  original: string;
  proposed: string;
  action: string;
  created_at: string;
};

export type ProposalCreateBody = {
  project_id: string;
  chapter_id: string;
  original: string;
  proposed: string;
  action: string;
  metadata?: Record<string, unknown>;
};

export type ProposalAcceptBody = {
  expected_chapter_version?: number;
};

export type ProposalRejectBody = {
  reason?: string;
};

export class ProposalApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ProposalApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: apiAuthHeaders(init?.headers),
  });
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as { code?: string; message?: string } | null;
    throw new ProposalApiError(r.status, body?.code ?? "unknown", body?.message ?? r.statusText);
  }
  if (r.status === 204) return undefined as T;
  return r.json() as Promise<T>;
}

function queryString(params: Record<string, string | undefined>): string {
  const sp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value != null && value !== "") sp.set(key, value);
  }
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export const proposalClient = {
  list(params: { project_id?: string; chapter_id?: string } = {}) {
    const project_id = params.project_id ?? (typeof window !== "undefined" ? getActiveProjectId() : DEFAULT_PROJECT_ID);
    return request<{ items: ProposalApiRecord[] }>(
      `/proposals${queryString({ project_id, chapter_id: params.chapter_id })}`
    );
  },

  create(body: ProposalCreateBody) {
    return request<ProposalApiRecord>("/proposals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },

  accept(proposalId: string, body: ProposalAcceptBody = {}, projectId?: string) {
    return request<{ chapter: Chapter }>(
      withProject(`/proposals/${encodeURIComponent(proposalId)}/accept`, projectId),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }
    );
  },

  reject(proposalId: string, body: ProposalRejectBody = {}, projectId?: string) {
    return request<{ proposal: ProposalApiRecord }>(
      withProject(`/proposals/${encodeURIComponent(proposalId)}/reject`, projectId),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }
    );
  },
};
