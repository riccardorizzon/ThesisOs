"use client";

import { useState } from "react";
import { cn } from "@/lib/cn";
import { WritingAiPanel } from "@/components/writing/WritingAiPanel";
import { WritingEditorShell } from "@/components/writing/WritingEditorShell";
import { WritingOutline } from "@/components/writing/WritingOutline";
import type { WritingOutlineChapter } from "@/components/writing/writingStub";

export type WritingWorkspaceProps = {
  chapterId?: string;
  chapters?: WritingOutlineChapter[];
  className?: string;
};

/**
 * Three-panel Writing layout shell — Spec §5.3.
 * Outline | Markdown editor | AI action panel.
 * Layer: Business (Product Plane)
 */
export function WritingWorkspace({
  chapterId,
  chapters,
  className,
}: WritingWorkspaceProps) {
  const [showOutline, setShowOutline] = useState(false);
  const [showAiPanel, setShowAiPanel] = useState(false);

  const panelShell =
    "overflow-hidden rounded-lg border border-border bg-surface shadow-sm";

  return (
    <div className={cn("space-y-3", className)} data-testid="writing-workspace">
      <div className="flex gap-2 lg:hidden">
        <button
          type="button"
          aria-pressed={showOutline}
          aria-controls="writing-outline-panel"
          onClick={() => setShowOutline((open) => !open)}
          className={cn(
            "rounded-md border px-3 py-1.5 text-xs font-medium transition-colors duration-200",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "focus-visible:outline-accent cursor-pointer",
            showOutline
              ? "border-accent bg-accent-subtle text-accent"
              : "border-border bg-surface text-ink-muted"
          )}
        >
          Outline
        </button>
        <button
          type="button"
          aria-pressed={showAiPanel}
          aria-controls="writing-ai-panel"
          onClick={() => setShowAiPanel((open) => !open)}
          className={cn(
            "rounded-md border px-3 py-1.5 text-xs font-medium transition-colors duration-200",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "focus-visible:outline-accent cursor-pointer",
            showAiPanel
              ? "border-accent bg-accent-subtle text-accent"
              : "border-border bg-surface text-ink-muted"
          )}
        >
          Azioni AI
        </button>
      </div>

      <div className="flex min-h-[32rem] flex-col gap-3 lg:min-h-[36rem] lg:flex-row lg:gap-4">
        <div
          id="writing-outline-panel"
          className={cn(
            panelShell,
            "lg:w-panel lg:shrink-0",
            showOutline ? "block" : "hidden lg:block"
          )}
        >
          <WritingOutline chapters={chapters} activeChapterId={chapterId} />
        </div>

        <div className={cn(panelShell, "min-w-0 flex-1")}>
          <WritingEditorShell chapterId={chapterId} />
        </div>

        <div
          id="writing-ai-panel"
          className={cn(
            panelShell,
            "lg:w-panel lg:shrink-0",
            showAiPanel ? "block" : "hidden lg:block"
          )}
        >
          <WritingAiPanel />
        </div>
      </div>
    </div>
  );
}
