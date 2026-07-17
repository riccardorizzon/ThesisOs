import { cookies } from "next/headers";
import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";
import {
  computeProgressPct,
  findContinueTarget,
  type ProgressChapter,
} from "@/lib/progress";
import {
  chapterScopeForMode,
  readWorkspaceModeCookie,
} from "@/lib/workspacePrefs";

type ChaptersLoadResult = {
  chapters: ProgressChapter[];
  error: string | null;
};

async function loadChapters(
  projectId: string,
  scope: "all" | "owned" | "demo",
): Promise<ChaptersLoadResult> {
  try {
    const list = await chapterClient.list({ project_id: projectId, scope });
    return {
      chapters: list.map((c) => ({
        id: c.id,
        title: c.title,
        status: c.status,
      })),
      error: null,
    };
  } catch (err) {
    const message =
      err instanceof Error
        ? err.message
        : "Impossibile caricare i capitoli dal server.";
    return { chapters: [], error: message };
  }
}

export default async function Home() {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  const mode = readWorkspaceModeCookie(cookieHeader);
  const scope = chapterScopeForMode(mode);
  const projectId =
    readActiveProjectIdCookie(cookieHeader) ?? DEFAULT_PROJECT_ID;
  const { chapters, error } = await loadChapters(projectId, scope);
  const progressPct = error != null ? 0 : computeProgressPct(chapters);
  const continueTarget = findContinueTarget(chapters);

  return (
    <HomeView
      progressPct={progressPct}
      continueTarget={continueTarget}
      activity={[]}
      chaptersLoadError={error}
      fashionEmptyPhase={projectId === DEFAULT_PROJECT_ID}
    />
  );
}
