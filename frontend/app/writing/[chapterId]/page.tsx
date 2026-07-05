import { Suspense } from "react";
import { WritingContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
import { loadContext } from "@/lib/contextLoad";

type Props = { params: Promise<{ chapterId: string }> };

export default async function WritingChapterPage({ params }: Props) {
  const { chapterId } = await params;
  const context = await loadContext({
    entityType: "chapter",
    entityId: chapterId,
  });

  return (
    <div className="space-y-6">
      <WritingContextBar packet={context} selectionAnchor={context.selection_anchor} />
      <Suspense fallback={<p className="text-sm text-ink-muted">Caricamento workspace…</p>}>
        <WritingWorkspace chapterId={chapterId} contextPacket={context} />
      </Suspense>
    </div>
  );
}
