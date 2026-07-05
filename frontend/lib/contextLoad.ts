import {
  CONTEXT_STUB,
  contextClient,
  type ContextPacket,
  type ContextQuery,
} from "@/lib/contextClient";
import {
  projectContextToQuery,
  resolveProjectContextForSurface,
} from "@/lib/projectContext";

export async function loadContext(
  params?: ContextQuery
): Promise<ContextPacket> {
  const surface = params?.surface;
  const resolved = resolveProjectContextForSurface(
    surface === "home" ? "home" : "writing",
    {
      productId: params?.productId,
      workspaceId: params?.workspaceId,
      sessionId: params?.sessionId,
    }
  );
  const query = projectContextToQuery(resolved, {
    surface: resolved.surface,
    entityType: params?.entityType,
    entityId: params?.entityId,
    selectionAnchor: params?.selectionAnchor,
    userIntent: params?.userIntent,
  });

  try {
    return await contextClient.get(resolved.project_id, query);
  } catch {
    return {
      ...CONTEXT_STUB,
      project_context: {
        project_id: resolved.project_id,
        product_id: resolved.product_id,
        workspace_id: resolved.workspace_id,
        session_id: resolved.session_id,
      },
      presentation: { surface: resolved.surface },
      selection_anchor: params?.selectionAnchor ?? null,
      entity:
        params?.entityType === "chapter" && params.entityId
          ? {
              type: "chapter",
              id: params.entityId,
              title: `Capitolo ${params.entityId}`,
            }
          : CONTEXT_STUB.entity,
    };
  }
}
