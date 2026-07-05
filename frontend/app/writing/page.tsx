import { Suspense } from "react";
import { WritingContextBar } from "@/components/context";
import { WritingWorkspace } from "@/components/writing";
import { loadContext } from "@/lib/contextLoad";

export default async function WritingPage() {
  const context = await loadContext();

  return (
    <div className="space-y-6">
      <WritingContextBar packet={context} />
      <Suspense fallback={<p className="text-sm text-ink-muted">Caricamento workspace…</p>}>
        <WritingWorkspace contextPacket={context} />
      </Suspense>
    </div>
  );
}
