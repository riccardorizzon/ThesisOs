import { cookies } from "next/headers";

import { SourcesEnrichedList } from "@/components/sources/SourcesEnrichedList";
import { SourcesErrorState } from "@/components/sources/SourcesErrorState";
import { listSources } from "@/lib/sourcesClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";

type Props = {
  searchParams: Promise<{ chapter?: string }>;
};

export default async function SourcesPage({ searchParams }: Props) {
  const { chapter } = await searchParams;

  try {
    const cookieStore = await cookies();
    const projectId =
      readActiveProjectIdCookie(cookieStore.toString()) ?? DEFAULT_PROJECT_ID;
    const res = await listSources({ projectId });
    return (
      <SourcesEnrichedList initialSources={res.sources} chapterContext={chapter} />
    );
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Impossibile caricare le fonti dal server.";
    return (
      <SourcesErrorState
        title="Errore caricamento Sources"
        message={message}
        chapterContext={chapter}
      />
    );
  }
}
