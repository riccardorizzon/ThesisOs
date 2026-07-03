import { ContextBar } from "@/components/context";
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
      <ContextBar packet={context} />
      <WritingWorkspace chapterId={chapterId} />
    </div>
  );
}
