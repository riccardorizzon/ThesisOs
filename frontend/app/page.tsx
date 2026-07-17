import { cookies } from "next/headers";
import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
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

async function loadChapters(scope: "all" | "owned" | "demo"): Promise<ChaptersLoadResult> {
  try {
    // SSR has no localStorage; scope to the product default until client remounts.
    const list = await chapterClient.list({ project_id: DEFAULT_PROJECT_ID, scope });
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
  const mode = readWorkspaceModeCookie(cookieStore.toString());
  const scope = chapterScopeForMode(mode);
  const { chapters, error } = await loadChapters(scope);
  const progressPct = error != null ? 0 : computeProgressPct(chapters);
  const continueTarget = findContinueTarget(chapters);

  return (
    <HomeView
      progressPct={progressPct}
      continueTarget={continueTarget}
      activity={[]}
      chaptersLoadError={error}
    />
  );
}
