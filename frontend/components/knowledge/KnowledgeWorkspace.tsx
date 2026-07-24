import Link from "next/link";

import { KnowledgeExplorer } from "@/components/knowledge/explorer";
import { KnowledgeNotesPanel } from "@/components/knowledge/notes/KnowledgeNotesPanel";
import type { KnowledgeObjectEnvelope } from "@/lib/knowledgeTypes";

type KnowledgeWorkspaceProps = {
  concepts: KnowledgeObjectEnvelope[];
  view: "concepts" | "notes";
};

export function KnowledgeWorkspace({
  concepts,
  view,
}: KnowledgeWorkspaceProps) {
  return (
    <div className="space-y-5">
      <nav
        aria-label="Sezioni Knowledge"
        className="mx-auto flex max-w-content gap-1 border-b border-border"
      >
        <Link
          href="/knowledge"
          aria-current={view === "concepts" ? "page" : undefined}
          className={`border-b-2 px-3 py-2 text-sm font-medium ${
            view === "concepts"
              ? "border-accent text-accent"
              : "border-transparent text-ink-muted"
          }`}
        >
          Concetti
        </Link>
        <Link
          href="/knowledge?view=notes"
          aria-current={view === "notes" ? "page" : undefined}
          className={`border-b-2 px-3 py-2 text-sm font-medium ${
            view === "notes"
              ? "border-accent text-accent"
              : "border-transparent text-ink-muted"
          }`}
        >
          Note
        </Link>
      </nav>
      {view === "notes" ? (
        <KnowledgeNotesPanel />
      ) : (
        <KnowledgeExplorer concepts={concepts} />
      )}
    </div>
  );
}
