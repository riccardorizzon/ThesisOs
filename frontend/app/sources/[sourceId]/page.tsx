import Link from "next/link";
import { SourceDetailView } from "@/components/library/SourceDetailView";
import { getSourceById } from "@/lib/libraryStub";

type Props = { params: Promise<{ sourceId: string }> };

export default async function SourceDetailPage({ params }: Props) {
  const { sourceId } = await params;
  const source = getSourceById(sourceId);

  if (source == null) {
    return (
      <div className="mx-auto max-w-content">
        <h1 className="text-2xl font-semibold text-ink">Fonte non trovata</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Nessuna fonte con id{" "}
          <code className="font-mono text-xs">{sourceId}</code>.
        </p>
        <Link
          href="/sources"
          className="mt-4 inline-block text-sm font-medium text-accent underline-offset-2 hover:underline cursor-pointer"
        >
          ← Torna a Sources
        </Link>
      </div>
    );
  }

  return <SourceDetailView source={source} />;
}
