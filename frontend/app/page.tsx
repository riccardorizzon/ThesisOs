import { HomeView } from "@/components/HomeView";
import { chapterClient } from "@/lib/chapterClient";
import { HOME_ACTIVITY_STUB, STUB_CHAPTERS } from "@/lib/homeStub";
import {
  computeProgressPct,
  findContinueTarget,
  type ProgressChapter,
} from "@/lib/progress";

async function loadChapters(): Promise<ProgressChapter[]> {
  try {
    const list = await chapterClient.list();
    if (list.length === 0) return STUB_CHAPTERS;
    return list.map((c) => ({
      id: c.id,
      title: c.title,
      status: c.status,
    }));
  } catch {
    return STUB_CHAPTERS;
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
      activity={HOME_ACTIVITY_STUB}
    />
  );
}
