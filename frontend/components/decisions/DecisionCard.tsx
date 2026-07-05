"use client";

import { useState } from "react";
import { cn } from "@/lib/cn";
import {
  dispatchAskReviewer,
  type DecisionView,
} from "@/lib/decisionClient";

export type DecisionCardProps = {
  decision: DecisionView;
  className?: string;
  onEditAttempt?: (decision: DecisionView) => void;
};

function StatusBadge({ status }: { status: DecisionView["status"] }) {
  const isBinding = status === "vincolante";
  return (
    <span
      className={cn(
        "rounded-full px-2 py-0.5 text-xs font-medium",
        isBinding
          ? "bg-warning/10 text-warning"
          : "bg-accent-subtle text-accent"
      )}
      data-testid="decision-status-badge"
    >
      {isBinding ? "Vincolante" : "Aperta"}
    </span>
  );
}

function FrozenEditModal({
  displayId,
  onDismiss,
}: {
  displayId: string;
  onDismiss: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/20 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="frozen-decision-title"
      data-testid="frozen-decision-modal"
    >
      <div className="w-full max-w-sm rounded-lg border border-border bg-surface p-4 shadow-md">
        <h3
          id="frozen-decision-title"
          className="text-sm font-semibold text-ink"
        >
          {displayId}
        </h3>
        <p className="mt-2 text-sm text-ink-muted">
          Decisione vincolante — non modificabile
        </p>
        <div className="mt-4 flex justify-end">
          <button
            type="button"
            className="rounded-md bg-surface-muted px-3 py-1.5 text-sm font-medium text-ink hover:bg-border"
            onClick={onDismiss}
          >
            Chiudi
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Decision card — Spec §12.2, UI spec §6.2.
 * Layer: Business (Product Plane)
 */
export function DecisionCard({
  decision,
  className,
  onEditAttempt,
}: DecisionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [showBlockedModal, setShowBlockedModal] = useState(false);

  const handleEditAttempt = () => {
    if (decision.frozen) {
      setShowBlockedModal(true);
      onEditAttempt?.(decision);
      return;
    }
    onEditAttempt?.(decision);
  };

  const influencedLabel =
    decision.influencedChapters.length > 0
      ? decision.influencedChapters.join(", ")
      : null;

  return (
    <>
      <article
        className={cn(
          "space-y-3 rounded-lg border border-border bg-surface p-4",
          className
        )}
        data-testid={`decision-card-${decision.id}`}
        aria-label={`Decisione ${decision.displayId}, ${decision.status}`}
      >
        <div className="flex items-start justify-between gap-2">
          <p className="font-mono text-xs text-ink-subtle">
            {decision.displayId}
          </p>
          <StatusBadge status={decision.status} />
        </div>

        <div className="space-y-1">
          <p className="line-clamp-2 text-sm font-medium text-ink">
            {decision.title}
          </p>
          {!expanded && (
            <p className="line-clamp-2 text-sm text-ink-muted">
              {decision.summary}
            </p>
          )}
        </div>

        {influencedLabel && (
          <p className="text-xs text-ink-muted">
            Influenza: {influencedLabel}
          </p>
        )}

        {expanded && (
          <div
            className="border-t border-border pt-3 text-sm text-ink-muted"
            data-testid="decision-full-summary"
          >
            {decision.fullSummary}
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-surface-muted"
            aria-expanded={expanded}
            onClick={() => setExpanded((open) => !open)}
          >
            {expanded ? "Chiudi" : "Leggi"}
          </button>
          <button
            type="button"
            className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent-muted"
            onClick={() => dispatchAskReviewer(decision.id)}
            data-testid="ask-reviewer-button"
          >
            Chiedi al revisore
          </button>
          {!decision.frozen && (
            <button
              type="button"
              className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink-muted hover:bg-surface-muted"
              onClick={handleEditAttempt}
            >
              Modifica
            </button>
          )}
        </div>

        {decision.frozen && (
          <>
            <p
              className="text-xs text-ink-subtle"
              data-testid="frozen-readonly-hint"
            >
              Decisione vincolante — non modificabile
            </p>
            <button
              type="button"
              className="sr-only"
              data-testid="decision-frozen-edit-guard"
              onClick={handleEditAttempt}
            >
              Tentativo modifica decisione vincolante
            </button>
          </>
        )}
      </article>

      {showBlockedModal && (
        <FrozenEditModal
          displayId={decision.displayId}
          onDismiss={() => setShowBlockedModal(false)}
        />
      )}
    </>
  );
}

/** Programmatic frozen guard for external edit triggers (e.g. editor integration). */
export function attemptDecisionEdit(decision: DecisionView): boolean {
  return !decision.frozen;
}
