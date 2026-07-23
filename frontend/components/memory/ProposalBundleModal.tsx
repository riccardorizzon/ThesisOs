"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";
import {
  readPendingProposals,
  resolveProposalBundle,
  type PendingProposal,
} from "@/lib/sessionState";

export type ProposalBundleModalProps = {
  open: boolean;
  onClose: () => void;
  onResolved?: (action: "approve" | "reject", proposals: PendingProposal[]) => void;
};

/**
 * OR-7 session close — atomic approve/reject all pending proposals.
 * Layer: Business (Product Plane)
 */
export function ProposalBundleModal({
  open,
  onClose,
  onResolved,
}: ProposalBundleModalProps) {
  const [proposals, setProposals] = useState<PendingProposal[]>([]);

  useEffect(() => {
    if (open) {
      setProposals(readPendingProposals());
    }
  }, [open]);

  if (!open) return null;

  const count = proposals.length;

  function handleResolve(action: "approve" | "reject") {
    if (count === 0) {
      onClose();
      return;
    }
    const resolved = resolveProposalBundle(action);
    onResolved?.(action, resolved);
    onClose();
  }

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-ink/20 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="proposal-bundle-title"
      data-testid="proposal-bundle-modal"
    >
      <div className="w-full max-w-lg rounded-lg border border-border bg-surface p-6 shadow-md">
        <h2
          id="proposal-bundle-title"
          className="text-lg font-semibold text-ink"
        >
          Chiudi sessione
          {count > 0 && (
            <span className="ml-2 text-sm font-normal text-ink-muted">
              — {count} {count === 1 ? "modifica" : "modifiche"} in sospeso
            </span>
          )}
        </h2>

        {count === 0 ? (
          <p className="mt-3 text-sm text-ink-muted">
            Nessuna proposta in sospeso. Puoi chiudere la sessione in sicurezza.
          </p>
        ) : (
          <>
            <p className="mt-2 text-sm text-ink-muted">
              Accetta o rifiuta tutte le proposte insieme — non è possibile
              approvarne solo alcune.
            </p>
            <ul
              className="mt-4 max-h-64 space-y-2 overflow-y-auto"
              data-testid="proposal-bundle-list"
            >
              {proposals.map((p) => (
                <li
                  key={p.id}
                  className="rounded-md border border-border bg-surface-muted p-3"
                >
                  <span className="block text-sm font-medium text-ink">
                    {p.title}
                  </span>
                  {p.summary != null && (
                    <span className="mt-0.5 block text-sm text-ink-muted">
                      {p.summary}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </>
        )}

        <div className="mt-6 flex flex-wrap justify-end gap-2">
          <button
            type="button"
            className={cn(
              "rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200",
              "bg-surface-muted text-ink hover:bg-border cursor-pointer",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
              "focus-visible:outline-accent"
            )}
            onClick={onClose}
          >
            Annulla
          </button>
          {count > 0 ? (
            <>
              <button
                type="button"
                className={cn(
                  "rounded-md px-4 py-2 text-sm font-medium transition-colors duration-200",
                  "border border-border bg-surface text-ink hover:bg-surface-muted cursor-pointer",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent"
                )}
                data-testid="reject-all-proposals"
                onClick={() => handleResolve("reject")}
              >
                Rifiuta tutte
              </button>
              <button
                type="button"
                className={cn(
                  "rounded-md px-4 py-2 text-sm font-medium text-ink-inverse transition-colors duration-200",
                  "bg-accent hover:bg-accent-muted cursor-pointer",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                  "focus-visible:outline-accent"
                )}
                data-testid="approve-all-proposals"
                onClick={() => handleResolve("approve")}
              >
                Accetta tutte
              </button>
            </>
          ) : (
            <button
              type="button"
              className={cn(
                "rounded-md px-4 py-2 text-sm font-medium text-ink-inverse transition-colors duration-200",
                "bg-accent hover:bg-accent-muted cursor-pointer",
                "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                "focus-visible:outline-accent"
              )}
              onClick={onClose}
            >
              Chiudi
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
