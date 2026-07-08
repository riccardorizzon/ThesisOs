import Link from "next/link";
import { Suspense } from "react";
import { WritingContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
import { WritingWorkspaceSkeleton } from "@/components/ui/PageSkeleton";
import { ContextApiError } from "@/lib/contextClient";
import { loadContext } from "@/lib/contextLoad";

type Props = { params: Promise<{ chapterId: string }> };

function contextErrorMessage(err: unknown): string {
  if (err instanceof ContextApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Contesto di scrittura non disponibile";
}

export default async function WritingChapterPage({ params }: Props) {
  const { chapterId } = await params;

  let context;
  try {
    context = await loadContext({
      entityType: "chapter",
      entityId: chapterId,
    });
  } catch (err) {
    return (
      <div className="space-y-4" data-testid="writing-context-error">
        <h1 className="text-xl font-semibold text-ink">Scrittura</h1>
        <p className="text-sm text-ink-muted" role="alert">
          {contextErrorMessage(err)}
        </p>
        <Link href="/writing" className="text-sm font-medium text-accent underline-offset-2 hover:underline">
          ← Torna all&apos;outline
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <WritingContextBar packet={context} selectionAnchor={context.selection_anchor} />
      <Suspense fallback={<WritingWorkspaceSkeleton />}>
        <WritingWorkspace chapterId={chapterId} contextPacket={context} />
      </Suspense>
    </div>
  );
}
