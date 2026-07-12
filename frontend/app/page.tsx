import { cookies } from "next/headers";
import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
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
    const list = await chapterClient.list({ scope });
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
