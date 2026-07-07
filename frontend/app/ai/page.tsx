import { Suspense } from "react";

import { AiChatView } from "@/components/AiChatView";

export default function AiPage() {
  return (
    <Suspense
      fallback={
        <div className="p-4 text-sm text-ink-muted" data-testid="ai-page-loading">
          Caricamento…
        </div>
      }
    >
      <AiChatView />
    </Suspense>
  );
}
