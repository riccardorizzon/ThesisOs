import {
  DEFAULT_PRODUCT_ID,
  DEFAULT_PROJECT_ID,
  defaultProjectContext,
  resolveProjectContext,
  resolveProjectContextForSurface,
  type ProjectContext,
} from "@/lib/projectContext";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export {
  DEFAULT_PRODUCT_ID,
  DEFAULT_PROJECT_ID,
  defaultProjectContext,
  resolveProjectContext,
  resolveProjectContextForSurface,
  type ProjectContext,
};

export type PresentationHint = {
  surface: string;
};

export type ProjectSummary = {
  title: string;
  phase: string;
  progress_pct: number;
};

export type EntityScope = {
  type: string;
  id: string;
  title: string;
  snippet?: string | null;
};

export type DecisionRef = {
  id: string;
  title?: string | null;
  summary: string;
  binding: boolean;
};

export type ContextPacket = {
  schema_version: string;
  project_context: ProjectContext;
  presentation: PresentationHint;
  project: ProjectSummary;
  entity?: EntityScope | null;
  selection_anchor?: string | null;
  relevant_sources: { id: string; title: string; kind?: string | null }[];
  concepts: { id: string; title: string; slug?: string | null }[];
  decisions: DecisionRef[];
  definitions: { term: string; definition: string }[];
  citations_available: { id: string; label: string; source_id?: string | null }[];
  corpus_constraints: string[];
  writing_rules: string[];
  memory_proposals_pending: number;
  recent_activity: { entity_type: string; title: string; href?: string | null }[];
  token_budget: number;
};

export type ContextQuery = {
  surface?: string;
  entityType?: string;
  entityId?: string;
  selectionAnchor?: string;
  productId?: string;
  workspaceId?: string;
  sessionId?: string;
  userIntent?: string;
};

export class ContextApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ContextApiError";
    this.status = status;
    this.code = code;
  }
}

function queryString(projectId: string, params?: ContextQuery): string {
  const sp = new URLSearchParams();
  if (params?.surface) sp.set("surface", params.surface);
  if (params?.entityType) sp.set("entity_type", params.entityType);
  if (params?.entityId) sp.set("entity_id", params.entityId);
  if (params?.selectionAnchor) sp.set("selection_anchor", params.selectionAnchor);
  if (params?.productId) sp.set("product_id", params.productId);
  if (params?.workspaceId) sp.set("workspace_id", params.workspaceId);
  if (params?.sessionId) sp.set("session_id", params.sessionId);
  if (params?.userIntent) sp.set("user_intent", params.userIntent);
  const qs = sp.toString();
  return `/projects/${encodeURIComponent(projectId)}/context${qs ? `?${qs}` : ""}`;
}

async function request<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!r.ok) {
    const body = (await r.json().catch(() => null)) as {
      code?: string;
      message?: string;
    } | null;
    throw new ContextApiError(
      r.status,
      body?.code ?? "unknown",
      body?.message ?? r.statusText
    );
  }
  return r.json() as Promise<T>;
}

export const contextClient = {
  get(projectId: string = DEFAULT_PROJECT_ID, params?: ContextQuery) {
    return request<ContextPacket>(queryString(projectId, params));
  },
};

/** Fallback when context API unavailable — PX-1 stub */
export const CONTEXT_STUB: ContextPacket = {
  schema_version: "0.2",
  project_context: {
    project_id: DEFAULT_PROJECT_ID,
    product_id: DEFAULT_PRODUCT_ID,
  },
  presentation: { surface: "writing" },
  project: {
    title: "Tesi STIGMATA",
    phase: "Sviluppo argomentativo",
    progress_pct: 42,
  },
  entity: null,
  selection_anchor: null,
  relevant_sources: [],
  concepts: [],
  decisions: [
    {
      id: "stub-corpus-02",
      title: "CORPUS-02",
      summary: "Barthes Mythologies — escluso dal corpus attivo",
      binding: true,
    },
    {
      id: "stub-corpus-03",
      title: "CORPUS-03",
      summary: "Bourriaud / estetica relazionale — escluso",
      binding: true,
    },
  ],
  definitions: [],
  citations_available: [],
  corpus_constraints: [
    "CORPUS-02: Barthes Mythologies — escluso dal corpus attivo",
    "CORPUS-03: Bourriaud / estetica relazionale — escluso",
  ],
  writing_rules: [
    "Italiano accademico; termini da Terminology.md",
    "Corpus approvato only (Bibliography-Master)",
  ],
  memory_proposals_pending: 0,
  recent_activity: [],
  token_budget: 8000,
};

export type ContextBarCounts = {
  sources: number;
  concepts: number;
  decisions: number;
  citations: number;
};

export function contextBarCounts(packet: ContextPacket): ContextBarCounts {
  return {
    sources: packet.relevant_sources.length,
    concepts: packet.concepts.length,
    decisions: packet.decisions.length,
    citations: packet.citations_available.length,
  };
}

export function formatContextBarLabel(counts: ContextBarCounts): string {
  return `${counts.sources} fonti · ${counts.decisions} decisioni · ${counts.concepts} voci · ${counts.citations} citazioni`;
}

export function formatScopeChipLabel(
  packet: ContextPacket,
  selectionAnchor?: string | null
): string {
  const anchor = selectionAnchor ?? packet.selection_anchor ?? null;
  if (packet.entity) {
    const chapterLabel = packet.entity.title;
    return anchor ? `${chapterLabel} · ${anchor}` : chapterLabel;
  }
  return anchor ?? packet.project.phase;
}

export const CONTEXT_OPEN_CONTESTO_EVENT = "thesisos:open-contesto-tab";

export function dispatchOpenContestoTab(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(CONTEXT_OPEN_CONTESTO_EVENT));
  }
}
