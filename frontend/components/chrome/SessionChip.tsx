"use client";

import { useCallback, useEffect, useState } from "react";
import { cn } from "@/lib/cn";
import { ProposalBundleModal } from "@/components/memory/ProposalBundleModal";
import {
  formatSessionDuration,
  ensureSessionState,
  getPendingProposalCount,
} from "@/lib/sessionState";

export type SessionChipProps = {
  className?: string;
};

/**
 * AppShell session indicator — Spec §14.2, UI spec §4.1
 * Layer: Business (Product Plane)
 */
export function SessionChip({ className }: SessionChipProps) {
  const [duration, setDuration] = useState("—");
  const [pendingCount, setPendingCount] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);

  const refresh = useCallback(() => {
    const session = ensureSessionState();
    setDuration(formatSessionDuration(session.startedAt) ?? "—");
    setPendingCount(getPendingProposalCount());
  }, []);

  useEffect(() => {
    refresh();
    const interval = window.setInterval(refresh, 60_000);
    const onBundle = () => refresh();
    window.addEventListener("thesisos:proposal-bundle-resolved", onBundle);
    return () => {
      window.clearInterval(interval);
      window.removeEventListener("thesisos:proposal-bundle-resolved", onBundle);
    };
  }, [refresh]);

  const proposalLabel =
    pendingCount === 1
      ? "1 proposta in sospeso"
      : `${pendingCount} proposte in sospeso`;

  return (
    <>
      <button
        type="button"
        onClick={() => setModalOpen(true)}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-md px-2.5 py-1",
          "text-xs font-medium text-ink-muted transition-colors duration-200",
          "hover:bg-surface-muted hover:text-ink",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
          "focus-visible:outline-accent cursor-pointer",
          className
        )}
        aria-label={`Sessione attiva, ${duration}, ${proposalLabel}. Chiudi sessione`}
        data-testid="session-chip"
      >
        <span>Sessione</span>
        <span aria-hidden="true">·</span>
        <span>{duration}</span>
        {pendingCount > 0 && (
          <>
            <span aria-hidden="true">·</span>
            <span className="text-accent">{pendingCount}</span>
            <span className="sr-only">{proposalLabel}</span>
          </>
        )}
      </button>

      <ProposalBundleModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onResolved={() => {
          refresh();
          setModalOpen(false);
        }}
      />
    </>
  );
}
