import { apiBaseUrl } from "@/lib/apiBase";

export type MemoryKind =
  | "user"
  | "thesis"
  | "concept"
  | "citation"
  | "decision"
  | "editable";

export type Memory = {
  id: string;
  kind: MemoryKind;
  title: string | null;
  content: string;
  metadata: Record<string, unknown>;
  key: string | null;
  pinned: boolean;
  source: string;
  version: number;
  created_at: string;
  updated_at: string;
};

export type MemoryVersion = {
  memory_id: string;
  version: number;
  title: string | null;
  content: string;
  metadata: Record<string, unknown>;
  source: string;
  changed_at: string;
};

export type MemoryCreateInput = {
  kind: MemoryKind;
  content: string;
  title?: string | null;
  key?: string | null;
  pinned?: boolean;
  metadata?: Record<string, unknown>;
};

export type MemoryUpdateInput = {
  title?: string | null;
  content?: string;
  pinned?: boolean;
  metadata?: Record<string, unknown>;
  expected_version: number;
};

export type MemoryListParams = {
  q?: string;
  kind?: MemoryKind;
};

export class MemoryApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "MemoryApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${apiBaseUrl()}${path}`, { ...init, cache: "no-store" });
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as { code?: string; message?: string } | null;
    throw new MemoryApiError(
      r.status,
      body?.code ?? "unknown",
      body?.message ?? r.statusText,
    );
  }
  if (r.status === 204) return undefined as T;
  return r.json() as Promise<T>;
}

function queryString(params?: MemoryListParams): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  if (params.q) sp.set("q", params.q);
  if (params.kind) sp.set("kind", params.kind);
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export const memoryClient = {
  list(params?: MemoryListParams) {
    return request<Memory[]>(`/memory${queryString(params)}`);
  },
  get(id: string) {
    return request<Memory>(`/memory/${id}`);
  },
  create(body: MemoryCreateInput) {
    return request<Memory>("/memory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
  update(id: string, body: MemoryUpdateInput) {
    return request<Memory>(`/memory/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
  delete(id: string) {
    return request<void>(`/memory/${id}`, { method: "DELETE" });
  },
  listVersions(id: string) {
    return request<MemoryVersion[]>(`/memory/${id}/versions`);
  },
};

export function memoryDisplayTitle(m: Pick<Memory, "title" | "key" | "content">): string {
  if (m.title?.trim()) return m.title;
  if (m.key?.trim()) return m.key;
  const line = m.content.split("\n")[0]?.trim();
  return line ? (line.length > 60 ? `${line.slice(0, 60)}…` : line) : "(untitled)";
}
