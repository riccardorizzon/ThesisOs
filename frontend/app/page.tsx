import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
import {
  computeProgressPct,
  findContinueTarget,
  type ProgressChapter,
} from "@/lib/progress";

type ChaptersLoadResult = {
  chapters: ProgressChapter[];
  error: string | null;
};

async function loadChapters(): Promise<ChaptersLoadResult> {
  try {
    const list = await chapterClient.list();
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
  const { chapters, error } = await loadChapters();
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
