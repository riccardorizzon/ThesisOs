import { KnowledgeExplorer } from "@/components/knowledge/explorer";
import { KnowledgeExplorerLoadError } from "@/components/knowledge/explorer/KnowledgeExplorerLoadError";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";

function knowledgeLoadMessage(err: unknown): string {
  if (err instanceof Error) {
    if (err.message.includes("fetch failed")) {
      return "Connessione al servizio Knowledge non disponibile. Riprova tra qualche secondo.";
    }
    return err.message;
  }
  return "Errore sconosciuto durante il caricamento.";
}

export default async function KnowledgePage() {
  try {
    const res = await listKnowledgeObjects({ type: "concept" });
    return <KnowledgeExplorer concepts={res.objects} />;
  } catch (err) {
    return <KnowledgeExplorerLoadError message={knowledgeLoadMessage(err)} />;
  }
}
