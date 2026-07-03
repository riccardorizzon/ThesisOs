import Link from "next/link";
import { KnowledgeDetailView } from "@/components/library/KnowledgeDetailView";
import { getConceptById } from "@/lib/libraryStub";

type Props = { params: Promise<{ conceptId: string }> };

export default async function KnowledgeConceptPage({ params }: Props) {
  const { conceptId } = await params;
  const concept = getConceptById(conceptId);

  if (concept == null) {
    return (
      <div className="mx-auto max-w-content">
        <h1 className="text-2xl font-semibold text-ink">Concetto non trovato</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Nessun concetto con id{" "}
          <code className="font-mono text-xs">{conceptId}</code>.
        </p>
        <Link
          href="/knowledge"
          className="mt-4 inline-block text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Torna a Knowledge
        </Link>
      </div>
    );
  }

  return <KnowledgeDetailView concept={concept} />;
}
