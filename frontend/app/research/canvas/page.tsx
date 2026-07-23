import { cookies } from "next/headers";

import { ResearchCanvasPage } from "@/components/research/ResearchCanvasPage";
import { getKnowledgeGraph } from "@/lib/knowledgeClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";

type Props = {
  searchParams: Promise<{ focus?: string; view?: string }>;
};

export default async function ResearchCanvasRoute({ searchParams }: Props) {
  const params = await searchParams;
  const focus = params.focus;
  const view = params.view;

  const cookieStore = await cookies();
  const projectId =
    readActiveProjectIdCookie(cookieStore.toString()) ?? DEFAULT_PROJECT_ID;
  const graph = await getKnowledgeGraph({
    projectId,
    focus,
    depth: 2,
    maxNodes: 80,
    profile: "canvas",
  });

  return <ResearchCanvasPage graph={graph} focus={focus} view={view} />;
}
