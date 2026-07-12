"use client";

import { useMemo } from "react";
import { WritingContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
import { DemoWorkspaceBanner } from "@/components/workspace/DemoWorkspaceBanner";
import { PersonalWorkspaceHint } from "@/components/workspace/PersonalWorkspaceHint";
import type { ContextPacket } from "@/lib/contextClient";
import {
  chapterScopeForMode,
  getWorkspaceMode,
  type WorkspaceMode,
} from "@/lib/workspacePrefs";

type WritingPageClientProps = {
  context: ContextPacket;
};

export function WritingPageClient({ context }: WritingPageClientProps) {
  const mode: WorkspaceMode = useMemo(() => getWorkspaceMode(), []);
  const chapterScope = chapterScopeForMode(mode);

  return (
    <div className="space-y-6">
      {mode === "demo" ? <DemoWorkspaceBanner /> : <PersonalWorkspaceHint />}
      <WritingContextBar packet={context} />
      <WritingWorkspace contextPacket={context} chapterScope={chapterScope} />
    </div>
  );
}
