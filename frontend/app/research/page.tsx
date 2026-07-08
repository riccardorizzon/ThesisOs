import { ResearchHubPage } from "@/components/research/ResearchHubPage";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";

async function resolveConceptCount(): Promise<number> {
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    return res.objects.length;
  } catch {
    return 0;
  }
}

export default async function ResearchPage() {
  const conceptCount = await resolveConceptCount();
  return <ResearchHubPage conceptCount={conceptCount} />;
}
