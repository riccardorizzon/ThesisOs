"use client";

import { ReviewCompare } from "./ReviewCompare";
import type { WritingProposal } from "@/lib/proposalQueue";

export type ReviewComparePanelProps = {
  chapterId: string | null;
  proposal: WritingProposal | null;
  onResolved?: (action: "accepted" | "rejected" | "partial") => void;
  className?: string;
};

/**
 * Compare panel wrapper — delegates to ReviewCompare when chapter + proposal selected.
 * Layer: Business (Product Plane)
 */
export function ReviewComparePanel({
  chapterId,
  proposal,
  onResolved,
  className,
}: ReviewComparePanelProps) {
  if (!chapterId || !proposal) {
    return (
      <section
        aria-labelledby="review-compare-heading"
        className={className}
        data-testid="review-compare-empty"
      >
        <h2
          id="review-compare-heading"
          className="mb-3 text-sm font-semibold uppercase tracking-wide text-ink-muted"
        >
          Confronto revisioni
        </h2>
        <div className="rounded-lg border border-dashed border-border bg-surface-muted p-8 text-center">
          <p className="text-sm text-ink-muted">
            Seleziona un capitolo con proposte in sospeso per visualizzare il confronto.
          </p>
        </div>
      </section>
    );
  }

  return (
    <ReviewCompare
      chapterId={chapterId}
      proposal={proposal}
      onResolved={onResolved}
      className={className}
    />
  );
}
