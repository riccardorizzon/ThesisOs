import {
  JobFsmObservationStrip,
  KnowledgeGraphPanelLazy,
} from "@/components/knowledge/graph";
import { ApiErrorBanner } from "@/components/ui/ApiErrorBanner";
import { getJobFsmObservation, getKnowledgeGraph } from "@/lib/knowledgeClient";

type KnowledgeGraphPageProps = {
  searchParams: Promise<{ focus?: string; depth?: string; view?: string }>;
};

function isNetworkFetchError(err: unknown): boolean {
  return err instanceof Error && err.message === "fetch failed";
}

function graphLoadMessage(err: unknown): string {
  if (isNetworkFetchError(err)) {
    return "Connessione al grafo Knowledge non disponibile. Torna all'elenco concetti e riprova.";
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "Impossibile caricare il grafo concettuale.";
}

export default async function KnowledgeGraphPage({
  searchParams,
}: KnowledgeGraphPageProps) {
  const params = await searchParams;
  const focus = params.focus;
  const depth = params.depth != null ? Number.parseInt(params.depth, 10) : 1;
  const view = params.view === "list" ? "list" : undefined;

  try {
    const graph = await getKnowledgeGraph({
      focus,
      depth: Number.isFinite(depth) ? depth : 1,
      view,
    });

    let jobFsm = null;
    try {
      jobFsm = await getJobFsmObservation();
    } catch {
      // Optional MB2 strip — graph remains usable without conformance observation.
    }

    return (
      <main className="mx-auto max-w-content space-y-6 px-4 py-8">
        {jobFsm != null ? <JobFsmObservationStrip observation={jobFsm} /> : null}
        <KnowledgeGraphPanelLazy graph={graph} />
      </main>
    );
  } catch (err) {
    return (
      <main className="mx-auto max-w-content px-4 py-8" data-testid="knowledge-graph-error">
        <ApiErrorBanner
          title="Grafo non disponibile"
          message={graphLoadMessage(err)}
          backHref="/knowledge"
          backLabel="← Torna a Knowledge"
          testId="knowledge-graph-error-banner"
        />
      </main>
    );
  }
}
