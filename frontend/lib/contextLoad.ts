import { contextClient, type ContextPacket, type ContextQuery } from "@/lib/contextClient";
import {
  projectContextToQuery,
  resolveProjectContextForSurface,
} from "@/lib/projectContext";

export async function loadContext(params?: ContextQuery): Promise<ContextPacket> {
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

  return contextClient.get(resolved.project_id, query);
}
