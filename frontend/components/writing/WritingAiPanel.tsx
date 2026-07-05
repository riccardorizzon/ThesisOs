"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/cn";
import type { ContextPacket } from "@/lib/contextClient";
import { formatScopeChipLabel } from "@/lib/contextClient";
import {
  getAvailableActions,
  streamWritingAction,
  type WritingActionId,
} from "@/lib/aiActions";
import { addProposal } from "@/lib/proposalQueue";
import { findConflictingDecision, parseDecisionsFromPacket } from "@/lib/decisionClient";
import { useApplyAiSuggestionChrome } from "@/lib/writingChromeIntegration";

export type WritingAiPanelProps = {
  chapterId?: string;
  contextPacket?: ContextPacket;
  selectionText?: string | null;
  selectionAnchor?: string | null;
  chapterContent?: string | null;
  reviewerDecisionId?: string | null;
  className?: string;
};

type StreamPhase = "idle" | "streaming" | "complete" | "preview";

/**
 * AI action panel — streaming actions + proposal queue (Spec §5.4, §15.3).
 * Applica never silent-writes; proposals go to queue (IR-2).
 * Layer: Business (Product Plane)
 */
export function WritingAiPanel({
  chapterId = "draft",
  contextPacket,
  selectionText,
  selectionAnchor,
  chapterContent,
  reviewerDecisionId,
  className,
}: WritingAiPanelProps) {
  const [phase, setPhase] = useState<StreamPhase>("idle");
  const [streamText, setStreamText] = useState("");
  const [activeActionId, setActiveActionId] = useState<WritingActionId | null>(null);
  const [activeActionLabel, setActiveActionLabel] = useState("");
  const [appliedNotice, setAppliedNotice] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const liveRef = useRef<HTMLDivElement>(null);

  const actions = getAvailableActions(selectionText, chapterContent);
  const decisions = contextPacket ? parseDecisionsFromPacket(contextPacket) : [];
  const conflict = contextPacket
    ? findConflictingDecision(
        decisions,
        contextPacket.entity ?? null,
        selectionText
      )
    : null;

  const scopeLabel = contextPacket
    ? formatScopeChipLabel(contextPacket, selectionAnchor)
    : selectionText?.trim()
      ? "Passaggio selezionato"
      : "Capitolo intero";

  const resetStream = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setPhase("idle");
    setStreamText("");
    setActiveActionId(null);
    setActiveActionLabel("");
  }, []);

  const runAction = useCallback(
    async (actionId: WritingActionId, label: string) => {
      if (!contextPacket) return;
      resetStream();
      setAppliedNotice(null);
      setActiveActionId(actionId);
      setActiveActionLabel(label);
      setPhase("streaming");

      const controller = new AbortController();
      abortRef.current = controller;
      let accumulated = "";

      await streamWritingAction(
        {
          actionId,
          chapterId,
          selectionText,
          chapterContent,
          contextPacket,
        },
        (event) => {
          if (controller.signal.aborted) return;
          if (event.event === "token") {
            accumulated += event.data.text;
            setStreamText(accumulated);
          } else if (event.event === "done") {
            setStreamText(event.data.draft);
            setPhase("complete");
          } else if (event.event === "error") {
            setStreamText(event.data.message);
            setPhase("complete");
          }
        },
        controller.signal
      );

      if (!controller.signal.aborted) {
        setPhase((current) => (current === "streaming" ? "complete" : current));
      }
    },
    [chapterId, chapterContent, contextPacket, resetStream, selectionText]
  );

  useEffect(() => {
    if (reviewerDecisionId && contextPacket) {
      void runAction("verify", "Verifica");
    }
  }, [reviewerDecisionId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (phase === "complete" && liveRef.current) {
      liveRef.current.textContent = "Risposta AI completata";
    }
  }, [phase]);

  const handleCancel = () => {
    abortRef.current?.abort();
    resetStream();
  };

  const handleApplica = useCallback(() => {
    if (!streamText.trim() || !activeActionId) return;
    setPhase("preview");
  }, [streamText, activeActionId]);

  useApplyAiSuggestionChrome(handleApplica);

  const handleConfirmProposal = () => {
    if (!streamText.trim() || !activeActionId) return;
    addProposal({
      actionId: activeActionId,
      actionLabel: activeActionLabel,
      chapterId,
      selectionText: selectionText ?? null,
      selectionAnchor: selectionAnchor ?? null,
      preview: streamText,
    });
    setAppliedNotice("Proposta aggiunta alla coda — il capitolo non è stato modificato.");
    resetStream();
  };

  const showStreamArea = phase !== "idle";
  const canApplica = phase === "complete" && Boolean(streamText.trim());

  return (
    <aside
      aria-label="Azioni AI contestuali"
      className={cn("flex h-full flex-col", className)}
      data-testid="writing-ai-panel"
    >
      <header className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Azioni AI</h2>
        <p className="mt-0.5 text-xs text-ink-muted">{scopeLabel}</p>
      </header>

      {conflict && (
        <div
          className="border-b border-warning/30 bg-warning/10 px-4 py-2 text-xs text-warning"
          role="status"
          data-testid="ai-conflict-banner"
        >
          Conflitto possibile con {conflict.displayId}
        </div>
      )}

      {appliedNotice && (
        <div
          className="border-b border-success/30 bg-success/10 px-4 py-2 text-xs text-success"
          role="status"
          aria-live="polite"
        >
          {appliedNotice}
        </div>
      )}

      <ul className="space-y-2 overflow-y-auto p-3">
        {actions.map((action) => (
          <li key={action.id}>
            <button
              type="button"
              disabled={!action.enabled || phase === "streaming" || !contextPacket}
              aria-disabled={!action.enabled || phase === "streaming" || !contextPacket}
              title={
                !contextPacket
                  ? "Contesto non disponibile"
                  : action.disabledReason ?? undefined
              }
              onClick={() => void runAction(action.id, action.label)}
              className={cn(
                "w-full rounded-md border border-border bg-surface px-3 py-2 text-left transition-colors duration-200",
                "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
                "focus-visible:outline-accent",
                action.enabled && contextPacket && phase !== "streaming"
                  ? "cursor-pointer hover:border-accent/40 hover:bg-accent-subtle/30"
                  : "cursor-not-allowed opacity-70"
              )}
            >
              <span className="block text-sm font-medium text-ink">{action.label}</span>
              <span className="mt-0.5 block text-xs text-ink-muted">
                {action.description}
              </span>
            </button>
          </li>
        ))}
      </ul>

      {showStreamArea && (
        <div className="flex min-h-0 flex-1 flex-col border-t border-border">
          <div
            className="flex-1 overflow-y-auto p-3 font-mono text-sm text-ink"
            data-testid="ai-stream-output"
          >
            {streamText || (phase === "streaming" ? "…" : "")}
          </div>

          <div
            ref={liveRef}
            aria-live="polite"
            aria-atomic="true"
            className="sr-only"
          />

          {phase === "preview" && (
            <div
              className="border-t border-border bg-surface px-3 py-3"
              data-testid="ai-anteprima"
            >
              <p className="text-xs font-medium text-ink">Anteprima proposta</p>
              <p className="mt-1 max-h-24 overflow-y-auto text-xs text-ink-muted">
                {streamText}
              </p>
              <div className="mt-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => setPhase("complete")}
                  className="rounded-md border border-border px-2 py-1 text-xs text-ink-muted cursor-pointer"
                >
                  Indietro
                </button>
                <button
                  type="button"
                  onClick={handleConfirmProposal}
                  className="rounded-md bg-accent px-2 py-1 text-xs font-medium text-white cursor-pointer"
                  data-testid="confirm-proposal"
                >
                  Aggiungi alla coda
                </button>
              </div>
            </div>
          )}

          {phase !== "preview" && (
            <div className="flex gap-2 border-t border-border p-3">
              <button
                type="button"
                onClick={handleCancel}
                className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink-muted cursor-pointer"
              >
                Annulla
              </button>
              <button
                type="button"
                onClick={handleApplica}
                disabled={!canApplica}
                className="rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white cursor-pointer disabled:opacity-50"
                data-testid="applica-button"
              >
                Applica
              </button>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
