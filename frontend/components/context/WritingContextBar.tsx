"use client";

import { useEffect, useState } from "react";
import type { ContextPacket } from "@/lib/contextClient";
import { ContextBar } from "@/components/context/ContextBar";
import { useDecisionWarning } from "@/lib/useDecisionWarning";

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
  );
}
