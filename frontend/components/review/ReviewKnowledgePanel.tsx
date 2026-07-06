"use client";

import Link from "next/link";
import type { ContextPacket } from "@/lib/contextClient";
import { cn } from "@/lib/cn";

export type ReviewKnowledgePanelProps = {
  packet: ContextPacket;
  chapterId?: string | null;
  className?: string;
};

/**
 * Review flow — surfaces Knowledge concepts linked to project context (PX4-EWO-010).
 */
export function ReviewKnowledgePanel({
  packet,
  chapterId,
  className,
}: ReviewKnowledgePanelProps) {
  const concepts = packet.concepts;

  return (
    <section
      className={cn(
        "rounded-lg border border-border bg-surface-muted p-4",
        className
      )}
      aria-labelledby="review-knowledge-heading"
      data-testid="review-knowledge-panel"
    >
      <h2
        id="review-knowledge-heading"
        className="text-sm font-semibold text-ink"
      >
        Concetti rilevanti
      </h2>
      {chapterId && (
        <p className="mt-1 text-xs text-ink-muted">
          Capitolo in revisione: {chapterId}
        </p>
      )}
      {concepts.length === 0 ? (
        <p className="mt-3 text-sm text-ink-muted">
          Nessun concetto nel contesto. Esplora{" "}
          <Link href="/knowledge" className="text-accent hover:underline">
            Knowledge
          </Link>
          .
        </p>
      ) : (
        <ul className="mt-3 flex flex-wrap gap-2">
          {concepts.map((concept) => (
            <li key={concept.id}>
              <Link
                href={`/knowledge/${concept.slug ?? concept.id}`}
                className="inline-flex rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-ink hover:border-accent hover:text-accent"
              >
                {concept.title}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
