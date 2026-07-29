import {
  chapterClient,
  type Chapter,
  type ChapterStatus,
} from "@/lib/chapterClient";

export type ChapterMetadataPatch = {
  title?: string;
  status?: ChapterStatus;
};

/**
 * Persist chapter title/status via PATCH with optimistic concurrency.
 */
export async function persistChapterMetadata(
  chapter: Pick<Chapter, "id" | "version">,
  patch: ChapterMetadataPatch
): Promise<Chapter> {
  const body: {
    title?: string;
    status?: ChapterStatus;
    expected_version: number;
  } = {
    expected_version: chapter.version,
  };

  if (patch.title !== undefined) {
    const trimmed = patch.title.trim();
    if (!trimmed) {
      throw new Error("Titolo obbligatorio");
    }
    body.title = trimmed;
  }

  if (patch.status !== undefined) {
    body.status = patch.status;
  }

  return chapterClient.update(chapter.id, body);
}
