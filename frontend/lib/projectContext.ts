/**
 * Project scope — ADR-0040 INV-PS-5
 * Layer: Business (Product Plane)
 *
 * Shared defaults and resolution stub for Home + Writing routes.
 * Full auth/workspace binding deferred to PX-2+.
 */

export const DEFAULT_PROJECT_ID = "thesis-agent";
export const DEFAULT_PRODUCT_ID = "thesisos";

export type ProjectContext = {
  project_id: string;
  product_id: string;
  workspace_id?: string | null;
  session_id?: string | null;
};

/** localStorage key for PX-2 session continuity (PX2-EWO-006). */
export const SESSION_STATE_STORAGE_KEY = "thesisos:session-state";

export type ProjectSurface = "home" | "writing";

export type ResolveProjectContextOptions = {
  projectId?: string;
  productId?: string;
  workspaceId?: string | null;
  sessionId?: string | null;
  surface?: ProjectSurface;
};

export type ContextQueryExtras = {
  surface?: string;
  entityType?: string;
  entityId?: string;
  selectionAnchor?: string;
  userIntent?: string;
};

/** Canonical PX-1 single-tenant defaults; PX-6 reads active project from storage. */
export function defaultProjectContext(): ProjectContext {
  const project_id =
    typeof window !== "undefined"
      ? (localStorage.getItem("thesisos:active-project-id") ?? DEFAULT_PROJECT_ID)
      : DEFAULT_PROJECT_ID;
  return {
    project_id,
    product_id: DEFAULT_PRODUCT_ID,
  };
}

/**
 * Resolve project scope for a route surface.
 * PX-1 stub — always thesis-agent/thesisos unless overridden.
 */
export function resolveProjectContext(
  options: ResolveProjectContextOptions = {}
): ProjectContext {
  return {
    project_id: options.projectId ?? DEFAULT_PROJECT_ID,
    product_id: options.productId ?? DEFAULT_PRODUCT_ID,
    workspace_id: options.workspaceId ?? null,
    session_id: options.sessionId ?? null,
  };
}

/** Surface-specific defaults for Home vs Writing context assembly. */
export function resolveProjectContextForSurface(
  surface: ProjectSurface,
  options: Omit<ResolveProjectContextOptions, "surface"> = {}
): ProjectContext & { surface: ProjectSurface } {
  return { ...resolveProjectContext(options), surface };
}

/** Map ProjectContext + optional entity scope to context API query fields. */
export function projectContextToQuery(
  ctx: ProjectContext,
  extra?: ContextQueryExtras
): ContextQueryExtras & {
  productId: string;
  workspaceId?: string;
  sessionId?: string;
} {
  return {
    ...extra,
    productId: ctx.product_id,
    workspaceId: ctx.workspace_id ?? undefined,
    sessionId: ctx.session_id ?? undefined,
  };
}
