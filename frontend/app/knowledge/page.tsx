import { KnowledgeExplorer } from "@/components/knowledge/explorer";
import { KnowledgeExplorerLoadError } from "@/components/knowledge/explorer/KnowledgeExplorerLoadError";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";

export default async function KnowledgePage() {
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    return <KnowledgeExplorer concepts={res.objects} />;
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Errore sconosciuto durante il caricamento.";
    return <KnowledgeExplorerLoadError message={message} />;
  }
}
