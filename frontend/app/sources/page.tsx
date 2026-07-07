import { SourcesEnrichedList } from "@/components/sources/SourcesEnrichedList";
import { SourcesErrorState } from "@/components/sources/SourcesErrorState";
import { listSources } from "@/lib/sourcesClient";

type Props = {
  searchParams: Promise<{ chapter?: string }>;
};

export default async function SourcesPage({ searchParams }: Props) {
  const { chapter } = await searchParams;

  try {
    const res = await listSources();
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
