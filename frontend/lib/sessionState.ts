/**
 * Session persistence + URL state — PX-2.5 (PX2-EWO-006)
 * Layer: Business (Product Plane)
 */

export const SESSION_STATE_STORAGE_KEY = "thesisos:session-state"; // legacy literal (docs/tests)
const SESSION_STATE_NAME = "session-state";
/** Integration B / PX2-EWO-003 — shared proposal queue key when proposalQueue.ts absent */
export const PROPOSALS_STORAGE_KEY = "thesisos:proposals"; // legacy literal (docs/tests)
const PROPOSALS_NAME = "proposals";

import {
  getProjectStorageItem,
  removeProjectStorageItem,
  setProjectStorageItem,
} from "@/lib/projectScope";

export type PanelTab = "ai" | "contesto" | "fonte" | "revisione";

export type SessionPersistedState = {
  chapterId?: string;
  chapterTitle?: string;
  section?: string;
  source?: string;
  panel?: PanelTab;
  scrollY?: number;
  route?: string;
  startedAt?: string;
  selection?: { anchor: string; savedAt: string };
  panelCollapsed?: boolean;
  updatedAt: string;
};

export type UrlWritingState = {
  section?: string;
  source?: string;
  panel?: PanelTab;
};

export type PendingProposal = {
  id: string;
  title: string;
  summary?: string;
  kind?: "memory" | "source" | "chapter";
  createdAt?: string;
};

const PANEL_TABS = new Set<PanelTab>(["ai", "contesto", "fonte", "revisione"]);

function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof localStorage !== "undefined";
}

/** Parse writing workspace query params from a search string (with or without leading ?). */
export function parseWritingUrlState(search: string): UrlWritingState {
  const raw = search.startsWith("?") ? search.slice(1) : search;
  if (!raw) return {};
  const params = new URLSearchParams(raw);
  const state: UrlWritingState = {};

  const section = params.get("section");
  if (section) state.section = section;

  const source = params.get("source");
  if (source) state.source = source;

  const panel = params.get("panel");
  if (panel && PANEL_TABS.has(panel as PanelTab)) {
    state.panel = panel as PanelTab;
  }

  return state;
}

/** Serialize writing workspace state into a path + query (+ optional hash anchor). */
export function serializeWritingUrlState(
  chapterId: string,
  state: UrlWritingState,
  options?: { scrollAnchor?: string }
): string {
  const params = new URLSearchParams();
  if (state.section) params.set("section", state.section);
  if (state.source) params.set("source", state.source);
  if (state.panel) params.set("panel", state.panel);
  const query = params.toString();
  const base = `/writing/${encodeURIComponent(chapterId)}`;
  const path = query ? `${base}?${query}` : base;
  if (options?.scrollAnchor) {
    return `${path}#${options.scrollAnchor}`;
  }
  return path;
}

export function loadSessionState(): SessionPersistedState | null {
  if (!isBrowser()) return null;
  try {
    const raw = getProjectStorageItem(SESSION_STATE_NAME);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as SessionPersistedState;
    if (!parsed.updatedAt) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveSessionState(
  partial: Partial<Omit<SessionPersistedState, "updatedAt">>
): SessionPersistedState {
  const now = new Date().toISOString();
  const existing = loadSessionState();
  const next: SessionPersistedState = {
    ...existing,
    ...partial,
    updatedAt: now,
    startedAt: partial.startedAt ?? existing?.startedAt ?? now,
  };
  if (isBrowser()) {
    setProjectStorageItem(SESSION_STATE_NAME, JSON.stringify(next));
  }
  return next;
}

export function touchSessionActivity(fields: Partial<SessionPersistedState>): SessionPersistedState {
  return saveSessionState(fields);
}

export function clearSessionState(): void {
  if (isBrowser()) {
    removeProjectStorageItem(SESSION_STATE_NAME);
  }
}

/** Format elapsed session duration — e.g. "2h 14m", "45m", "0m". */
export function formatSessionDuration(
  startedAt: string | null | undefined,
  now: Date = new Date()
): string {
  if (!startedAt) return "0m";
  const start = new Date(startedAt);
  if (Number.isNaN(start.getTime())) return "0m";
  const diffMs = Math.max(0, now.getTime() - start.getTime());
  const totalMinutes = Math.floor(diffMs / 60_000);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function readProposalsFromStorage(): PendingProposal[] {
  if (!isBrowser()) return [];
  try {
    const raw = getProjectStorageItem(PROPOSALS_NAME);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as PendingProposal[] | { items?: PendingProposal[] };
    if (Array.isArray(parsed)) return parsed;
    if (parsed && Array.isArray(parsed.items)) return parsed.items;
    return [];
  } catch {
    return [];
  }
}

function writeProposalsToStorage(proposals: PendingProposal[]): void {
  if (!isBrowser()) return;
  setProjectStorageItem(PROPOSALS_NAME, JSON.stringify(proposals));
}

/**
 * Read pending proposals — prefers @/lib/proposalQueue when Integration B wires it.
 * Falls back to localStorage key `thesisos:proposals`.
 */
export function readPendingProposals(): PendingProposal[] {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const mod = require("@/lib/proposalQueue") as {
      listPendingProposals?: () => PendingProposal[];
      getPendingProposals?: () => PendingProposal[];
    };
    if (typeof mod.listPendingProposals === "function") {
      return mod.listPendingProposals();
    }
    if (typeof mod.getPendingProposals === "function") {
      return mod.getPendingProposals();
    }
  } catch {
    // proposalQueue not yet shipped (PX2-EWO-003)
  }
  return readProposalsFromStorage();
}

export function getPendingProposalCount(): number {
  return readPendingProposals().length;
}

/** OR-7 — atomic clear after approve/reject all. */
export function resolveProposalBundle(action: "approve" | "reject"): PendingProposal[] {
  const pending = readPendingProposals();
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const mod = require("@/lib/proposalQueue") as { clearPendingProposals?: () => void };
    mod.clearPendingProposals?.();
  } catch {
    writeProposalsToStorage([]);
  }
  if (action === "approve" && isBrowser()) {
    window.dispatchEvent(
      new CustomEvent("thesisos:proposal-bundle-resolved", {
        detail: { action, count: pending.length, proposals: pending },
      })
    );
  }
  return pending;
}

export function sessionStateToUrlState(
  state: SessionPersistedState
): UrlWritingState {
  return {
    section: state.section,
    source: state.source,
    panel: state.panel,
  };
}
