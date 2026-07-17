import { contextClient, type ContextPacket, type ContextQuery } from "@/lib/contextClient";
import {
  projectContextToQuery,
  resolveProjectContextForSurface,
} from "@/lib/projectContext";
import { getActiveProjectId } from "@/lib/projectPrefs";

/** Browser-side context load scoped to the active project id. */
export async function loadContextClient(
  params?: ContextQuery,
): Promise<ContextPacket> {
  const surface = params?.surface;
  const resolved = resolveProjectContextForSurface(
    surface === "home" ? "home" : "writing",
    {
      projectId: getActiveProjectId(),
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
