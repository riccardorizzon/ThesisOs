const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type DocumentSourceType = "pdf" | "epub" | "docx";
export type DocumentStatus = "uploaded" | "processing" | "parsed" | "failed";

export type Document = {
  id: string;
  title: string;
  author: string | null;
  source_type: DocumentSourceType;
  original_filename: string | null;
  gcs_uri: string | null;
  status: DocumentStatus;
  page_count: number | null;
  language: string | null;
  version: number;
  parser: string | null;
  parsed_at: string | null;
  chunk_count: number | null;
  error_message: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type DocumentChunk = {
  id: string;
  document_id: string;
  chunk_index: number;
  chunk_hash: string;
  content: string;
  page_from: number | null;
  page_to: number | null;
  section_path: string | null;
  token_count: number | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type DocumentVersion = {
  document_id: string;
  version: number;
  title: string;
  author: string | null;
  source_type: DocumentSourceType;
  page_count: number | null;
  chunk_count: number | null;
  parser: string | null;
  metadata: Record<string, unknown>;
  change_reason: string;
  changed_at: string;
};

export type DocumentUploadInput = {
  file: File;
  title?: string | null;
  author?: string | null;
  language?: string | null;
};

export type DocumentUpdateInput = {
  title?: string | null;
  author?: string | null;
  language?: string | null;
  metadata?: Record<string, unknown> | null;
  expected_version: number;
};

export type DocumentListParams = {
  q?: string;
  status?: DocumentStatus;
  source_type?: DocumentSourceType;
};

export class DocumentApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "DocumentApiError";
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, { ...init, cache: "no-store" });
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as { code?: string; message?: string } | null;
    throw new DocumentApiError(
      r.status,
      body?.code ?? "unknown",
      body?.message ?? r.statusText,
    );
  }
  if (r.status === 204) return undefined as T;
  return r.json() as Promise<T>;
}

function queryString(params?: DocumentListParams): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  if (params.q) sp.set("q", params.q);
  if (params.status) sp.set("status", params.status);
  if (params.source_type) sp.set("source_type", params.source_type);
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export const documentClient = {
  list(params?: DocumentListParams) {
    return request<Document[]>(`/documents${queryString(params)}`);
  },
  get(id: string) {
    return request<Document>(`/documents/${id}`);
  },
  upload(input: DocumentUploadInput) {
    const form = new FormData();
    form.append("file", input.file);
    if (input.title) form.append("title", input.title);
    if (input.author) form.append("author", input.author);
    if (input.language) form.append("language", input.language);
    // No Content-Type header: the browser sets the multipart boundary.
    return request<Document>("/upload", { method: "POST", body: form });
  },
  update(id: string, body: DocumentUpdateInput) {
    return request<Document>(`/documents/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  },
  delete(id: string) {
    return request<void>(`/documents/${id}`, { method: "DELETE" });
  },
  listChunks(id: string) {
    return request<DocumentChunk[]>(`/documents/${id}/chunks`);
  },
  listVersions(id: string) {
    return request<DocumentVersion[]>(`/documents/${id}/versions`);
  },
  reparse(id: string) {
    return request<{ document_id: string; status: string }>(`/documents/${id}/reparse`, {
      method: "POST",
    });
  },
};

export function documentDisplayTitle(d: Pick<Document, "title" | "original_filename">): string {
  if (d.title?.trim()) return d.title;
  if (d.original_filename?.trim()) return d.original_filename;
  return "(untitled)";
}
