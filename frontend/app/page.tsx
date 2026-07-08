import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
import {
  computeProgressPct,
  findContinueTarget,
  type ProgressChapter,
} from "@/lib/progress";

async function loadChapters(): Promise<ProgressChapter[]> {
  try {
    const list = await chapterClient.list();
    return list.map((c) => ({
      id: c.id,
      title: c.title,
      status: c.status,
    }));
  } catch {
    return [];
  }
}

export default async function Home() {
  const chapters = await loadChapters();
  const progressPct = computeProgressPct(chapters);
  const continueTarget = findContinueTarget(chapters);

  return (
    <HomeView
      progressPct={progressPct}
      continueTarget={continueTarget}
      activity={[]}
    />
  );
}
