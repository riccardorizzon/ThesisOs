import { SourcesEnrichedList } from "@/components/sources/SourcesEnrichedList";
import type { LibrarySource } from "@/lib/libraryStub";
import type { SourceListItem } from "@/lib/sourcesTypes";

export type SourcesViewProps = {
  sources: LibrarySource[] | SourceListItem[];
  chapterContext?: string;
  className?: string;
};

function toSourceListItem(source: LibrarySource): SourceListItem {
  return {
    id: source.id,
    slug: source.id,
    type: "source",
    title: source.title,
    subtitle: source.subtitle,
    summary: source.meta,
    confidence: "non_valutata",
    knowledge_state:
      source.status === "esclusa"
        ? "deprecated"
        : source.status === "approvata"
          ? "validated"
          : "candidate",
    linked_counts: {
      sources: 0,
      chapters: 0,
      concepts: source.relatedConceptIds.length,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "importazione",
    proposal_state: "nessuna",
    is_core: false,
    related_concepts: source.relatedConceptIds.map((id) => ({
      id,
      slug: id,
      title: id,
    })),
    corpus_status: source.status,
  };
}

function normalizeSources(
  sources: LibrarySource[] | SourceListItem[]
): SourceListItem[] {
  if (sources.length === 0) return [];
  const first = sources[0];
  if ("related_concepts" in first) {
    return sources as SourceListItem[];
  }
  return (sources as LibrarySource[]).map(toSourceListItem);
}

/** Compatibility wrapper — PX3-EWO-002 enriched list. */
export function SourcesView({ sources, ...rest }: SourcesViewProps) {
  return (
    <SourcesEnrichedList
      initialSources={normalizeSources(sources)}
      {...rest}
    />
  );
}
