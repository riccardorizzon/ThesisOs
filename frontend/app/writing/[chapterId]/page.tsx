import { ContextBar } from "@/components/context";
import { ModuleStub } from "@/components/ModuleStub";
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
      <ModuleStub
        title={`Writing — capitolo ${chapterId}`}
        milestone="PX-2"
        description="Editor e pannello AI per il capitolo selezionato."
      />
    </div>
  );
}
