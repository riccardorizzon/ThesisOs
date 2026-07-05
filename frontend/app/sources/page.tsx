import { SourcesEnrichedList } from "@/components/sources/SourcesEnrichedList";
import { listSources } from "@/lib/sourcesClient";
import { LIBRARY_SOURCES } from "@/lib/libraryStub";
import type { SourceListItem } from "@/lib/sourcesTypes";

type Props = {
  searchParams: Promise<{ chapter?: string }>;
};

function stubSources(): SourceListItem[] {
  return LIBRARY_SOURCES.filter((s) => s.status !== "esclusa").map((s) => ({
    id: s.id,
    slug: s.id,
    type: "source" as const,
    title: s.title,
    subtitle: s.subtitle,
    summary: s.meta,
    confidence: "non_valutata" as const,
    knowledge_state:
      s.status === "approvata"
        ? ("validated" as const)
        : ("candidate" as const),
    linked_counts: {
      sources: 0,
      chapters: 0,
      concepts: s.relatedConceptIds.length,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "importazione" as const,
    proposal_state: "nessuna" as const,
    is_core: false,
    related_concepts: s.relatedConceptIds.map((id) => ({
      id,
      slug: id,
      title: id,
    })),
    corpus_status: s.status,
  }));
}

export default async function SourcesPage({ searchParams }: Props) {
  const { chapter } = await searchParams;
  let sources: SourceListItem[];
  try {
    const res = await listSources();
    sources = res.sources;
  } catch {
    sources = stubSources();
  }

  return (
    <SourcesEnrichedList initialSources={sources} chapterContext={chapter} />
  );
}
