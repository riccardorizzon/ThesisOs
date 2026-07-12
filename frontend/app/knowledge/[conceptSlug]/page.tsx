import { ExplainPageShell } from "@/components/knowledge/explain";
import {
  getConceptDefinition,
  getConceptHeader,
} from "@/lib/knowledgeClient";

type Props = { params: Promise<{ conceptSlug: string }> };

export default async function KnowledgeConceptExplainPage({ params }: Props) {
  const { conceptSlug } = await params;

  try {
    const header = await getConceptHeader(conceptSlug);
    let definition = null;
    try {
      definition = await getConceptDefinition(conceptSlug);
    } catch {
      // Supervisor gate or missing definition — client shell may retry.
    }
    return (
      <ExplainPageShell
        conceptSlug={conceptSlug}
        initialHeader={header}
        initialDefinition={definition}
      />
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : "";
    if (message === "concept_not_found") {
      return <ExplainPageShell conceptSlug={conceptSlug} initialNotFound />;
    }
    return (
      <ExplainPageShell
        conceptSlug={conceptSlug}
        initialError={
          message.includes("fetch failed")
            ? "Connessione al servizio Knowledge non disponibile. Riprova tra qualche secondo."
            : "Errore nel caricamento del concetto."
        }
      />
    );
  }
}
