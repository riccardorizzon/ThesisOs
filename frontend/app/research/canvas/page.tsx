import { ResearchCanvasPage } from "@/components/research/ResearchCanvasPage";
import { getKnowledgeGraph } from "@/lib/knowledgeClient";
import { buildStubResearchGraph } from "@/lib/researchCanvasStub";

type Props = {
  searchParams: Promise<{ focus?: string; view?: string }>;
};

export default async function ResearchCanvasRoute({ searchParams }: Props) {
  const params = await searchParams;
  const focus = params.focus;
  const view = params.view;

  let graph;
  try {
    graph = await getKnowledgeGraph({
      focus,
      depth: 2,
      maxNodes: 80,
      profile: "canvas",
    });
  } catch {
    graph = buildStubResearchGraph(focus);
  }

  return <ResearchCanvasPage graph={graph} focus={focus} view={view} />;
}
