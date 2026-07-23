import { Suspense } from "react";

import { AiChatView } from "@/components/AiChatView";

/** Chat-first home — the latest workspace opens directly on the agent. */
export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="p-4 text-sm text-ink-muted" data-testid="agent-page-loading">
          Caricamento…
        </div>
      }
    >
      <AiChatView />
    </Suspense>
  );
}
