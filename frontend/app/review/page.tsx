import { Suspense } from "react";
import { ReviewMode } from "@/components/review/ReviewMode";
import { loadContext } from "@/lib/contextLoad";

export default async function ReviewPage() {
  const context = await loadContext({ surface: "writing" });

  return (
    <Suspense
      fallback={
        <p className="p-6 text-sm text-ink-muted">Caricamento workspace revisione…</p>
      }
    >
      <ReviewMode contextPacket={context} />
    </Suspense>
  );
}
