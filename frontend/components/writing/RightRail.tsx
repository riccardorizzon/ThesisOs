"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { cn } from "@/lib/cn";
import type { ContextPacket } from "@/lib/contextClient";
import { ContextInspector } from "@/components/context";
import { SourcePeekReader } from "@/components/sources/SourcePeekReader";
import { corpusClient } from "@/lib/corpusClient";
import { dispatchInsertCitation, formatCitationMarker } from "@/lib/citationInsert";
import { RailTabs, type RailTabId } from "@/components/writing/RailTabs";
import { WritingAiPanel } from "@/components/writing/WritingAiPanel";
import { useRightRailEvents } from "@/components/writing/rightRailIntegration";
import { RevisionQueuePanel } from "@/components/review/RevisionQueuePanel";
import { useRailTabChrome } from "@/lib/writingChromeIntegration";

export type RightRailProps = {
  chapterId?: string;
  contextPacket: ContextPacket;
  selectionText?: string | null;
  selectionAnchor?: string | null;
  chapterContent?: string | null;
  defaultTab?: RailTabId;
  peekSourceId?: string | null;
  onPeekSourceChange?: (sourceId: string | null) => void;
  editorFocusRef?: React.RefObject<HTMLElement | null>;
  className?: string;
};

/**
 * Tabbed right rail — AI | Contesto | Fonte | Revisione (UI spec §5.4).
 * Layer: Business (Product Plane)
 */
export function RightRail({
  chapterId,
  contextPacket,
  selectionText,
  selectionAnchor,
  chapterContent,
  defaultTab = "ai",
  peekSourceId,
  onPeekSourceChange,
  editorFocusRef,
  className,
}: RightRailProps) {
  const [activeTab, setActiveTab] = useState<RailTabId>(defaultTab);
  const [reviewerDecisionId, setReviewerDecisionId] = useState<string | null>(null);

  const peekSource = useMemo(
    () => (peekSourceId ? corpusClient.getById(peekSourceId) : undefined),
    [peekSourceId]
  );

  useEffect(() => {
    setActiveTab(defaultTab);
  }, [defaultTab]);

  useEffect(() => {
    if (peekSourceId) setActiveTab("fonte");
  }, [peekSourceId]);

  const handleTabChange = useCallback((tab: RailTabId) => {
    setActiveTab(tab);
  }, []);

  useRightRailEvents({
    onTabChange: handleTabChange,
    onAskReviewer: (decisionId) => setReviewerDecisionId(decisionId),
    onOpenFontePeek: (sourceId) => onPeekSourceChange?.(sourceId),
  });

  useRailTabChrome(handleTabChange);

  return (
    <aside
      className={cn("flex h-full flex-col", className)}
      aria-label="Pannello laterale scrittura"
      data-testid="right-rail"
    >
      <RailTabs activeTab={activeTab} onTabChange={handleTabChange} />

      <div className="min-h-0 flex-1 overflow-hidden">
        <div
          role="tabpanel"
          id="rail-panel-ai"
          aria-labelledby="rail-tab-ai"
          hidden={activeTab !== "ai"}
          className={cn("h-full", activeTab !== "ai" && "hidden")}
        >
          <WritingAiPanel
            chapterId={chapterId}
            contextPacket={contextPacket}
            selectionText={selectionText}
            selectionAnchor={selectionAnchor}
            chapterContent={chapterContent}
            reviewerDecisionId={reviewerDecisionId}
          />
        </div>

        <div
          role="tabpanel"
          id="rail-panel-contesto"
          aria-labelledby="rail-tab-contesto"
          hidden={activeTab !== "contesto"}
          className={cn("h-full overflow-y-auto p-3", activeTab !== "contesto" && "hidden")}
        >
          <ContextInspector
            packet={contextPacket}
            selectionAnchor={selectionAnchor}
          />
        </div>

        <div
          role="tabpanel"
          id="rail-panel-fonte"
          aria-labelledby="rail-tab-fonte"
          hidden={activeTab !== "fonte"}
          className={cn("h-full", activeTab !== "fonte" && "hidden")}
        >
          {peekSource ? (
            <SourcePeekReader
              source={peekSource}
              chapterId={chapterId}
              focusReturnRef={editorFocusRef}
              onDismiss={() => onPeekSourceChange?.(null)}
              onCite={(source, quote) => {
                dispatchInsertCitation({
                  marker: formatCitationMarker(source),
                  sourceId: source.id,
                  quote,
                });
              }}
            />
          ) : (
            <div className="flex h-full flex-col p-4" data-testid="source-peek-slot">
              <p className="text-sm font-medium text-ink">Anteprima fonte</p>
              <p className="mt-2 text-xs text-ink-muted">
                Usa Cita (⌘⇧C) o seleziona una fonte dal corpus.
              </p>
            </div>
          )}
        </div>

        <div
          role="tabpanel"
          id="rail-panel-revisione"
          aria-labelledby="rail-tab-revisione"
          hidden={activeTab !== "revisione"}
          className={cn("h-full overflow-y-auto", activeTab !== "revisione" && "hidden")}
        >
          <RevisionQueuePanel chapterId={chapterId} />
        </div>
      </div>
    </aside>
  );
}

