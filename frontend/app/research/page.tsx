import { ResearchHubPage } from "@/components/research/ResearchHubPage";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";

type ConceptCountResult = {
  count: number;
  status: "ok" | "empty" | "unavailable";
};

async function resolveConceptCount(): Promise<ConceptCountResult> {
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    const count = res.objects.length;
    return { count, status: count === 0 ? "empty" : "ok" };
  } catch {
    return { count: 0, status: "unavailable" };
  }
}

export default async function ResearchPage() {
  const { count, status } = await resolveConceptCount();
  return (
    <ResearchHubPage conceptCount={count} conceptCountStatus={status} />
  );
}
