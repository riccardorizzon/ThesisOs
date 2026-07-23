import { cookies } from "next/headers";

import { ResearchHubPage } from "@/components/research/ResearchHubPage";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";

type ConceptCountResult = {
  count: number;
  status: "ok" | "empty" | "unavailable";
};

async function resolveConceptCount(projectId: string): Promise<ConceptCountResult> {
  try {
    const res = await listKnowledgeObjects({ type: "concept", projectId });
    const count = res.objects.length;
    return { count, status: count === 0 ? "empty" : "ok" };
  } catch {
    return { count: 0, status: "unavailable" };
  }
}

export default async function ResearchPage() {
  const cookieStore = await cookies();
  const projectId =
    readActiveProjectIdCookie(cookieStore.toString()) ?? DEFAULT_PROJECT_ID;
  const { count, status } = await resolveConceptCount(projectId);
  return (
    <ResearchHubPage conceptCount={count} conceptCountStatus={status} />
  );
}
