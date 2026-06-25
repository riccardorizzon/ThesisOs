import { create } from "zustand";

import {
  Document,
  DocumentApiError,
  DocumentChunk,
  DocumentListParams,
  DocumentSourceType,
  DocumentStatus,
  DocumentUpdateInput,
  DocumentUploadInput,
  DocumentVersion,
  documentClient,
} from "@/lib/documentClient";

type DocumentAdminState = {
  items: Document[];
  selected: Document | null;
  chunks: DocumentChunk[];
  versions: DocumentVersion[];
  loading: boolean;
  error: string | null;
  errorCode: string | null;
  errorStatus: number | null;
  listQuery: string;
  statusFilter: DocumentStatus | "";
  sourceTypeFilter: DocumentSourceType | "";
  fetchList: (params?: DocumentListParams) => Promise<void>;
  fetchOne: (id: string) => Promise<void>;
  fetchChunks: (id: string) => Promise<void>;
  fetchVersions: (id: string) => Promise<void>;
  upload: (input: DocumentUploadInput) => Promise<Document>;
  update: (id: string, input: DocumentUpdateInput) => Promise<Document>;
  remove: (id: string) => Promise<void>;
  reparse: (id: string) => Promise<void>;
  setListQuery: (q: string) => void;
  setStatusFilter: (s: DocumentStatus | "") => void;
  setSourceTypeFilter: (s: DocumentSourceType | "") => void;
  clearError: () => void;
  clearSelected: () => void;
};

function mapError(err: unknown): { message: string; code: string | null; status: number | null } {
  if (err instanceof DocumentApiError) {
    return { message: err.message, code: err.code, status: err.status };
  }
  return { message: err instanceof Error ? err.message : String(err), code: null, status: null };
}

export const useDocumentStore = create<DocumentAdminState>((set, get) => ({
  items: [],
  selected: null,
  chunks: [],
  versions: [],
  loading: false,
  error: null,
  errorCode: null,
  errorStatus: null,
  listQuery: "",
  statusFilter: "",
  sourceTypeFilter: "",

  setListQuery: (q) => set({ listQuery: q }),
  setStatusFilter: (s) => set({ statusFilter: s }),
  setSourceTypeFilter: (s) => set({ sourceTypeFilter: s }),

  clearError: () => set({ error: null, errorCode: null, errorStatus: null }),

  clearSelected: () => set({ selected: null, chunks: [], versions: [] }),

  fetchList: async (params) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const { listQuery, statusFilter, sourceTypeFilter } = get();
      const items = await documentClient.list({
        q: (params?.q ?? listQuery) || undefined,
        status: params?.status ?? (statusFilter || undefined),
        source_type: params?.source_type ?? (sourceTypeFilter || undefined),
      });
      set({ items, loading: false });
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
    }
  },

  fetchOne: async (id) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const selected = await documentClient.get(id);
      set({ selected, loading: false });
    } catch (err) {
      const e = mapError(err);
      set({
        loading: false,
        error: e.message,
        errorCode: e.code,
        errorStatus: e.status,
        selected: null,
      });
    }
  },

  fetchChunks: async (id) => {
    try {
      const chunks = await documentClient.listChunks(id);
      set({ chunks });
    } catch (err) {
      const e = mapError(err);
      set({ error: e.message, errorCode: e.code, errorStatus: e.status, chunks: [] });
    }
  },

  fetchVersions: async (id) => {
    try {
      const versions = await documentClient.listVersions(id);
      set({ versions });
    } catch (err) {
      const e = mapError(err);
      set({ error: e.message, errorCode: e.code, errorStatus: e.status, versions: [] });
    }
  },

  upload: async (input) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const created = await documentClient.upload(input);
      set({ loading: false });
      return created;
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
      throw err;
    }
  },

  update: async (id, input) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const updated = await documentClient.update(id, input);
      set({ selected: updated, loading: false });
      return updated;
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
      throw err;
    }
  },

  remove: async (id) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      await documentClient.delete(id);
      set((s) => ({
        items: s.items.filter((d) => d.id !== id),
        selected: s.selected?.id === id ? null : s.selected,
        loading: false,
      }));
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
      throw err;
    }
  },

  reparse: async (id) => {
    set({ error: null, errorCode: null, errorStatus: null });
    try {
      await documentClient.reparse(id);
      const selected = await documentClient.get(id);
      set({ selected });
    } catch (err) {
      const e = mapError(err);
      set({ error: e.message, errorCode: e.code, errorStatus: e.status });
      throw err;
    }
  },
}));

export const DOCUMENT_SOURCE_TYPES: DocumentSourceType[] = ["pdf", "epub", "docx"];
export const DOCUMENT_STATUSES: DocumentStatus[] = ["uploaded", "processing", "parsed", "failed"];
