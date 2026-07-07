"use client";

import { useEffect, useState } from "react";
import type { ContextPacket } from "@/lib/contextClient";
import { ContextBar } from "@/components/context/ContextBar";
import { useDecisionWarning } from "@/lib/useDecisionWarning";
import { consumeCanvasBasketHandoff } from "@/lib/canvasBasket";

export type WritingContextBarProps = {
  packet: ContextPacket;
  selectionAnchor?: string | null;
  onScopeClick?: () => void;
  onOpenContestoTab?: () => void;
};

/**
 * Writing route ContextBar with decision warning wiring (Integration A).
 * Layer: Business (Product Plane)
 */
export function WritingContextBar({
  packet,
  selectionAnchor,
  onScopeClick,
  onOpenContestoTab,
}: WritingContextBarProps) {
  const [selectionText, setSelectionText] = useState("");
  const [canvasBasketCount, setCanvasBasketCount] = useState(0);

  useEffect(() => {
    const imported = consumeCanvasBasketHandoff();
    if (imported.length > 0) {
      setCanvasBasketCount(imported.length);
    }
  }, []);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    const syncSelection = () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        setSelectionText(window.getSelection()?.toString().trim() ?? "");
      }, 300);
    };
    document.addEventListener("selectionchange", syncSelection);
    return () => {
      document.removeEventListener("selectionchange", syncSelection);
      if (timer) clearTimeout(timer);
    };
  }, []);

  const warning = useDecisionWarning({ packet, selectionText });

  return (
    <>
      {canvasBasketCount > 0 && (
        <p
          className="mb-2 rounded-md border border-accent/30 bg-accent-subtle px-3 py-2 text-sm text-ink"
          data-testid="writing-canvas-basket-chip"
        >
          Basket canvas importato ({canvasBasketCount} elementi) — disponibile nel pannello
          Contesto.
        </p>
      )}
      <ContextBar
      packet={packet}
      selectionAnchor={selectionAnchor}
      warningState={{
        active: warning.active,
        message: warning.message ?? undefined,
      }}
      onScopeClick={onScopeClick}
      onOpenContestoTab={onOpenContestoTab}
    />
    </>
  );
}
