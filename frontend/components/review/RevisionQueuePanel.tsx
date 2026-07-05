"use client";

import Link from "next/link";
import { useMemo } from "react";
import { cn } from "@/lib/cn";
import {
  getPendingProposals,
  type WritingProposal,
} from "@/lib/proposalQueue";

export type RevisionQueuePanelProps = {
  chapterId?: string;
  className?: string;
};

function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("it-IT", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function groupByChapter(proposals: WritingProposal[]): Map<string, WritingProposal[]> {
  const map = new Map<string, WritingProposal[]>();
  for (const p of proposals) {
    const list = map.get(p.chapterId) ?? [];
    list.push(p);
    map.set(p.chapterId, list);
  }
  return map;
}

/**
 * Inline revision queue — lists pending chapter proposals (Integration C wires into RightRail).
 * Layer: Business (Product Plane)
 */
export function RevisionQueuePanel({ chapterId, className }: RevisionQueuePanelProps) {
  const pending = getPendingProposals();
  const filtered = chapterId
    ? pending.filter((p) => p.chapterId === chapterId)
    : pending;

  const grouped = useMemo(() => groupByChapter(filtered), [filtered]);

  if (filtered.length === 0) {
    return (
      <aside
        aria-label="Coda revisioni"
        className={cn("p-4 text-center", className)}
        data-testid="revision-queue-empty"
      >
        <p className="text-sm text-ink-muted">Nessuna revisione in sospeso</p>
        <Link
          href="/review"
          className="mt-3 inline-block text-sm font-medium text-accent hover:underline cursor-pointer"
        >
          Avvia revisione
        </Link>
      </aside>
    );
  }

  return (
    <aside
      aria-label="Coda revisioni"
      className={cn("flex flex-col", className)}
      data-testid="revision-queue-panel"
    >
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Revisioni in sospeso</h2>
        <p className="mt-0.5 text-xs text-ink-muted">
          {filtered.length} proposta{filtered.length === 1 ? "" : "e"}
        </p>
      </header>

      <ul className="divide-y divide-border overflow-y-auto">
        {chapterId
          ? filtered.map((proposal) => (
              <li key={proposal.id}>
                <RevisionQueueItem proposal={proposal} />
              </li>
            ))
          : [...grouped.entries()].map(([cid, items]) => (
              <li key={cid}>
                <p className="px-4 py-2 text-xs font-medium uppercase tracking-wide text-ink-muted">
                  Capitolo {cid}
                </p>
                <ul>
                  {items.map((proposal) => (
                    <li key={proposal.id}>
                      <RevisionQueueItem proposal={proposal} />
                    </li>
                  ))}
                </ul>
              </li>
            ))}
      </ul>
    </aside>
  );
}

function RevisionQueueItem({ proposal }: { proposal: WritingProposal }) {
  const href = `/review?chapter=${encodeURIComponent(proposal.chapterId)}&proposal=${encodeURIComponent(proposal.id)}`;

  return (
    <Link
      href={href}
      className="block px-4 py-3 transition-colors hover:bg-surface-muted cursor-pointer"
      data-testid={`revision-queue-item-${proposal.id}`}
    >
      <span className="block text-sm font-medium text-ink">{proposal.actionLabel}</span>
      <span className="mt-0.5 line-clamp-2 block text-xs text-ink-muted">
        {proposal.preview}
      </span>
      <span className="mt-1 block text-xs text-ink-muted">
        {formatRelativeTime(proposal.createdAt)}
      </span>
    </Link>
  );
}

export { getPendingProposals as listPendingProposalsForRevisionQueue };
