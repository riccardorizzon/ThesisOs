import { ContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
import { loadContext } from "@/lib/contextLoad";

export default async function WritingPage() {
  const context = await loadContext();

  return (
    <div className="space-y-6">
      <ContextBar packet={context} />
      <WritingWorkspace />
    </div>
  );
}
