"use client";

import { resolveProjectContext } from "@/lib/projectContext";

type WorkspaceNavProps = {
  workspaceId?: string | null;
};

/**
 * Workspace scope hint — PX-1 stub for future workspace-level sub-navigation.
 * Layer: Business (Product Plane)
 */
export function WorkspaceNav({ workspaceId }: WorkspaceNavProps) {
  const ctx = resolveProjectContext({ workspaceId });
  if (ctx.workspace_id == null) {
    return null;
  }

  return (
    <p className="px-4 pb-3 text-xs text-ink-subtle">
      Workspace:{" "}
      <span className="font-mono text-ink-muted">{ctx.workspace_id}</span>
    </p>
  );
}
