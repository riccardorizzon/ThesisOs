import {
  JobFsmObservationStrip,
  KnowledgeGraphPanelLazy,
} from "@/components/knowledge/graph";
import { getJobFsmObservation, getKnowledgeGraph } from "@/lib/knowledgeClient";

type KnowledgeGraphPageProps = {
  searchParams: Promise<{ focus?: string; depth?: string; view?: string }>;
};

export default async function KnowledgeGraphPage({
  searchParams,
}: KnowledgeGraphPageProps) {
  const params = await searchParams;
  const focus = params.focus;
  const depth = params.depth != null ? Number.parseInt(params.depth, 10) : 1;
  const view = params.view === "list" ? "list" : undefined;

  const [graph, jobFsm] = await Promise.all([
    getKnowledgeGraph({
      focus,
      depth: Number.isFinite(depth) ? depth : 1,
      view,
    }),
    getJobFsmObservation(),
  ]);

  return (
    <main className="mx-auto max-w-content space-y-6 px-4 py-8">
      <JobFsmObservationStrip observation={jobFsm} />
      <KnowledgeGraphPanelLazy graph={graph} />
    </main>
  );
}
