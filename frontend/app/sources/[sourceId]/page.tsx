import { cookies } from "next/headers";

import { SourceApiDetailView } from "@/components/sources/SourceApiDetailView";
import { SourcesErrorState } from "@/components/sources/SourcesErrorState";
import { getSource } from "@/lib/sourcesClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";

type Props = {
  params: Promise<{ sourceId: string }>;
  searchParams: Promise<{ chapter?: string }>;
};

export default async function SourceDetailPage({ params, searchParams }: Props) {
  const { sourceId } = await params;
  const { chapter } = await searchParams;

  try {
    const cookieStore = await cookies();
    const projectId =
      readActiveProjectIdCookie(cookieStore.toString()) ?? DEFAULT_PROJECT_ID;
    const source = await getSource(sourceId, projectId);
    return (
      <SourceApiDetailView source={source} chapterContext={chapter} />
    );
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Fonte non disponibile.";
    return (
      <SourcesErrorState
        title="Fonte non trovata"
        message={message}
        chapterContext={chapter}
      />
    );
  }
}
