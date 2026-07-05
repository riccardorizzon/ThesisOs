import { KnowledgeExplorer } from "@/components/knowledge/explorer";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";
import { LIBRARY_CONCEPTS } from "@/lib/libraryStub";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

function stubConcepts(): KnowledgeObjectEnvelope[] {
  return LIBRARY_CONCEPTS.map((c) => ({
    id: c.id,
    slug: c.id,
    type: "concept" as const,
    title: c.title,
    subtitle: c.subtitle,
    summary: c.definition,
    confidence: c.id === "stigmata" || c.id === "aura" ? ("alta" as const) : ("media" as const),
    knowledge_state:
      c.relatedSourceIds.length >= 2
        ? ("linked" as const)
        : ("validated" as const),
    linked_counts: {
      sources: c.relatedSourceIds.length,
      chapters: 0,
      concepts: 0,
      decisions: 0,
      authors: 0,
      citations: 0,
    },
    created_by: "operatore" as const,
    proposal_state: "nessuna" as const,
    is_core: c.id === "stigmata",
  }));
}

export default async function KnowledgePage() {
  let concepts: KnowledgeObjectEnvelope[];
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    concepts = res.objects;
  } catch {
    concepts = stubConcepts();
  }

  return <KnowledgeExplorer concepts={concepts} />;
}
