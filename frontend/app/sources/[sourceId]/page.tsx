import Link from "next/link";
import { SourceDetailView } from "@/components/library/SourceDetailView";
import { getSourceById } from "@/lib/libraryStub";

type Props = {
  params: Promise<{ sourceId: string }>;
  searchParams: Promise<{ chapter?: string }>;
};

export default async function SourceDetailPage({ params, searchParams }: Props) {
  const { sourceId } = await params;
  const { chapter } = await searchParams;
  const source = getSourceById(sourceId);

  if (source == null) {
    return (
      <div className="mx-auto max-w-content">
        <h1 className="text-2xl font-semibold text-ink">Fonte non trovata</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Fonte non trovata o esclusa — nessuna fonte con id{" "}
          <code className="font-mono text-xs">{sourceId}</code>.
        </p>
        <Link
          href={chapter ? `/sources?chapter=${chapter}` : "/sources"}
          className="mt-4 inline-block text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Torna a Sources
        </Link>
      </div>
    );
  }

  return <SourceDetailView source={source} chapterContext={chapter} />;
}
