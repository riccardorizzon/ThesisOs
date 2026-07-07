import { ResearchHubPage } from "@/components/research/ResearchHubPage";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";
import { LIBRARY_CONCEPTS } from "@/lib/libraryStub";

async function resolveConceptCount(): Promise<number> {
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    return res.objects.length;
  } catch {
    return LIBRARY_CONCEPTS.length;
  }
}

export default async function ResearchPage() {
  const conceptCount = await resolveConceptCount();
  return <ResearchHubPage conceptCount={conceptCount} />;
}
