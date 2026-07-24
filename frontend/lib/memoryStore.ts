import { create } from "zustand";

import {
  memoryClient,
  Memory,
  MemoryApiError,
  MemoryCreateInput,
  MemoryKind,
  MemoryListParams,
  MemoryUpdateInput,
  MemoryVersion,
} from "@/lib/memoryClient";

type MemoryAdminState = {
  items: Memory[];
  selected: Memory | null;
  versions: MemoryVersion[];
  loading: boolean;
  error: string | null;
  errorCode: string | null;
  errorStatus: number | null;
  listQuery: string;
  fetchList: (params?: MemoryListParams) => Promise<void>;
  fetchOne: (id: string) => Promise<void>;
  fetchVersions: (id: string) => Promise<void>;
  create: (input: MemoryCreateInput) => Promise<Memory>;
  update: (id: string, input: MemoryUpdateInput) => Promise<Memory>;
  remove: (id: string) => Promise<void>;
  setListQuery: (q: string) => void;
  clearError: () => void;
  clearSelected: () => void;
};

function mapError(err: unknown): { message: string; code: string | null; status: number | null } {
  if (err instanceof MemoryApiError) {
    return { message: err.message, code: err.code, status: err.status };
  }
  return { message: err instanceof Error ? err.message : String(err), code: null, status: null };
}

export const useMemoryStore = create<MemoryAdminState>((set, get) => ({
  items: [],
  selected: null,
  versions: [],
  loading: false,
  error: null,
  errorCode: null,
  errorStatus: null,
  listQuery: "",

  setListQuery: (q) => set({ listQuery: q }),

  clearError: () => set({ error: null, errorCode: null, errorStatus: null }),

  clearSelected: () => set({ selected: null, versions: [] }),

  fetchList: async (params) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const q = params?.q ?? get().listQuery;
      const items = await memoryClient.list({ ...params, q: q || undefined });
      set({ items, loading: false });
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
    }
  },

  fetchOne: async (id) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const selected = await memoryClient.get(id);
      set({ selected, loading: false });
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status, selected: null });
    }
  },

  fetchVersions: async (id) => {
    try {
      const versions = await memoryClient.listVersions(id);
      set({ versions });
    } catch (err) {
      const e = mapError(err);
      set({ error: e.message, errorCode: e.code, errorStatus: e.status, versions: [] });
    }
  },

  create: async (input) => {
    set({ loading: true, error: null, errorCode: null, errorStatus: null });
    try {
      const created = await memoryClient.create(input);
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
      const updated = await memoryClient.update(id, input);
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
      await memoryClient.delete(id);
      set((s) => ({
        items: s.items.filter((m) => m.id !== id),
        selected: s.selected?.id === id ? null : s.selected,
        loading: false,
      }));
    } catch (err) {
      const e = mapError(err);
      set({ loading: false, error: e.message, errorCode: e.code, errorStatus: e.status });
      throw err;
    }
  },
}));

export const MEMORY_KINDS: MemoryKind[] = [
  "user",
  "thesis",
  "editable",
  "decision",
  "concept",
  "citation",
  "note",
];
