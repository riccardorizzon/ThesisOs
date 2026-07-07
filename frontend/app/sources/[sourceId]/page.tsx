import { SourceApiDetailView } from "@/components/sources/SourceApiDetailView";
import { SourcesErrorState } from "@/components/sources/SourcesErrorState";
import { getSource } from "@/lib/sourcesClient";

type Props = {
  params: Promise<{ sourceId: string }>;
  searchParams: Promise<{ chapter?: string }>;
};

export default async function SourceDetailPage({ params, searchParams }: Props) {
  const { sourceId } = await params;
  const { chapter } = await searchParams;

  try {
    const source = await getSource(sourceId);
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
