import { cookies } from "next/headers";

import { KnowledgeWorkspace } from "@/components/knowledge/KnowledgeWorkspace";
import { KnowledgeExplorerLoadError } from "@/components/knowledge/explorer/KnowledgeExplorerLoadError";
import { listKnowledgeObjects } from "@/lib/knowledgeClient";
import { DEFAULT_PROJECT_ID } from "@/lib/projectContext";
import { readActiveProjectIdCookie } from "@/lib/projectPrefs";

function knowledgeLoadMessage(err: unknown): string {
  if (err instanceof Error) {
    if (err.message.includes("fetch failed")) {
      return "Connessione al servizio Knowledge non disponibile. Riprova tra qualche secondo.";
    }
    return err.message;
  }
  return "Errore sconosciuto durante il caricamento.";
}

type KnowledgePageProps = {
  searchParams: Promise<{ view?: string }>;
};

export default async function KnowledgePage({
  searchParams,
}: KnowledgePageProps) {
  const { view: rawView } = await searchParams;
  const view = rawView === "notes" ? "notes" : "concepts";
  if (view === "notes") {
    return <KnowledgeWorkspace concepts={[]} view="notes" />;
  }
  try {
    const cookieStore = await cookies();
    const projectId =
      readActiveProjectIdCookie(cookieStore.toString()) ?? DEFAULT_PROJECT_ID;
    const res = await listKnowledgeObjects({ type: "concept", projectId });
    return <KnowledgeWorkspace concepts={res.objects} view="concepts" />;
  } catch (err) {
    return <KnowledgeExplorerLoadError message={knowledgeLoadMessage(err)} />;
  }
}
