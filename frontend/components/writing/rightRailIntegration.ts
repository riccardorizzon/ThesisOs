"use client";

import { useEffect } from "react";
import { CONTEXT_OPEN_CONTESTO_EVENT } from "@/lib/contextClient";
import { ASK_REVIEWER_EVENT, type AskReviewerDetail } from "@/lib/decisionClient";
import {
  railTabFromShortcut,
  type RailTabId,
} from "@/components/writing/RailTabs";

export const OPEN_FONTE_PEEK_EVENT = "thesisos:open-fonte-peek";

export type OpenFontePeekDetail = {
  sourceId: string;
};

export function dispatchOpenFontePeek(sourceId: string): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(OPEN_FONTE_PEEK_EVENT, { detail: { sourceId } })
  );
}

export type RightRailEventHandlers = {
  onTabChange: (tab: RailTabId) => void;
  onAskReviewer?: (decisionId: string) => void;
  onOpenFontePeek?: (sourceId: string) => void;
};

/**
 * Event wiring for RightRail — consumed by Integration B when mounting RightRail.
 * Layer: Business (Product Plane)
 */
export function useRightRailEvents({
  onTabChange,
  onAskReviewer,
  onOpenFontePeek,
}: RightRailEventHandlers): void {
  useEffect(() => {
    const onOpenContesto = () => onTabChange("contesto");
    window.addEventListener(CONTEXT_OPEN_CONTESTO_EVENT, onOpenContesto);
    return () => window.removeEventListener(CONTEXT_OPEN_CONTESTO_EVENT, onOpenContesto);
  }, [onTabChange]);

  useEffect(() => {
    const onAsk = (event: Event) => {
      const detail = (event as CustomEvent<AskReviewerDetail>).detail;
      onTabChange("ai");
      onAskReviewer?.(detail.decisionId);
    };
    window.addEventListener(ASK_REVIEWER_EVENT, onAsk);
    return () => window.removeEventListener(ASK_REVIEWER_EVENT, onAsk);
  }, [onTabChange, onAskReviewer]);

  useEffect(() => {
    const onFonte = (event: Event) => {
      const detail = (event as CustomEvent<OpenFontePeekDetail>).detail;
      if (!detail?.sourceId) return;
      onTabChange("fonte");
      onOpenFontePeek?.(detail.sourceId);
    };
    window.addEventListener(OPEN_FONTE_PEEK_EVENT, onFonte);
    return () => window.removeEventListener(OPEN_FONTE_PEEK_EVENT, onFonte);
  }, [onTabChange, onOpenFontePeek]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || event.shiftKey || event.altKey || event.ctrlKey) return;
      const digit = Number.parseInt(event.key, 10);
      if (digit < 1 || digit > 4) return;
      const tab = railTabFromShortcut(digit);
      if (!tab) return;
      event.preventDefault();
      onTabChange(tab);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onTabChange]);
}

export function bindRightRailEvents(handlers: RightRailEventHandlers): () => void {
  const onOpenContesto = () => handlers.onTabChange("contesto");
  const onAsk = (event: Event) => {
    const detail = (event as CustomEvent<AskReviewerDetail>).detail;
    handlers.onTabChange("ai");
    handlers.onAskReviewer?.(detail.decisionId);
  };
  const onKeyDown = (event: KeyboardEvent) => {
    if (!event.metaKey || event.shiftKey || event.altKey || event.ctrlKey) return;
    const digit = Number.parseInt(event.key, 10);
    if (digit < 1 || digit > 4) return;
    const tab = railTabFromShortcut(digit);
    if (!tab) return;
    event.preventDefault();
    handlers.onTabChange(tab);
  };

  window.addEventListener(CONTEXT_OPEN_CONTESTO_EVENT, onOpenContesto);
  window.addEventListener(ASK_REVIEWER_EVENT, onAsk);
  window.addEventListener("keydown", onKeyDown);

  return () => {
    window.removeEventListener(CONTEXT_OPEN_CONTESTO_EVENT, onOpenContesto);
    window.removeEventListener(ASK_REVIEWER_EVENT, onAsk);
    window.removeEventListener("keydown", onKeyDown);
  };
}
