"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/cn";
import { dispatchOpenReview } from "@/components/review/reviewIntegration";
import type { ContextPacket } from "@/lib/contextClient";
import { CONTEXT_STUB } from "@/lib/contextClient";
import { chapterClient, type Chapter } from "@/lib/chapterClient";
import { parseWritingUrlState, saveSessionState, type PanelTab } from "@/lib/sessionState";
import { RightRail } from "@/components/writing/RightRail";
import { type RailTabId } from "@/components/writing/RailTabs";
import { WritingEditorShell } from "@/components/writing/WritingEditorShell";
import { WritingOutline } from "@/components/writing/WritingOutline";
import { LinkedSourcesFooter } from "@/components/writing/LinkedSourcesFooter";
import type { MarkdownSection } from "@/components/writing/MarkdownEditor";
import {
  WRITING_OUTLINE_STUB,
  type WritingOutlineChapter,
} from "@/components/writing/writingStub";
import {
  useOutlineSectionChrome,
  useWritingPanelChrome,
} from "@/lib/writingChromeIntegration";

export type WritingWorkspaceProps = {
  chapterId?: string;
  contextPacket?: ContextPacket;
  chapters?: WritingOutlineChapter[];
  className?: string;
};

function useMobileReadOnly(breakpoint = 768): boolean {
  const [mobile, setMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);
    const update = () => setMobile(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, [breakpoint]);

  return mobile;
}

function chapterToOutline(ch: Chapter): WritingOutlineChapter {
  return { id: ch.id, title: ch.title, status: ch.status };
}

function panelFromParam(value: string | null): RailTabId | undefined {
  if (value === "ai" || value === "contesto" || value === "fonte" || value === "revisione") {
    return value;
  }
  return undefined;
}

/**
 * Three-panel Writing layout — Outline | Editor | RightRail (Integration B).
 * Layer: Business (Product Plane)
 */
export function WritingWorkspace({
  chapterId,
  contextPacket = CONTEXT_STUB,
  chapters: chaptersProp,
  className,
}: WritingWorkspaceProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const urlState = parseWritingUrlState(searchParams.toString());
  const activeSectionId = urlState.section ?? searchParams.get("section") ?? undefined;
  const readOnly = useMobileReadOnly();
  const editorFocusRef = useRef<HTMLElement | null>(null);

  const [showOutline, setShowOutline] = useState(false);
  const [showRail, setShowRail] = useState(false);
  const [chapters, setChapters] = useState<WritingOutlineChapter[]>(
    chaptersProp ?? WRITING_OUTLINE_STUB
  );
  const [sections, setSections] = useState<MarkdownSection[]>([]);
  const [activeChapter, setActiveChapter] = useState<Chapter | null>(null);
  const [selectionText, setSelectionText] = useState("");
  const [peekSourceId, setPeekSourceId] = useState<string | null>(urlState.source ?? null);
  const [railTab, setRailTab] = useState<RailTabId>(panelFromParam(urlState.panel ?? null) ?? "ai");

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

  useEffect(() => {
    if (chaptersProp) {
      setChapters(chaptersProp);
      return;
    }
    void chapterClient
      .list()
      .then((list) => {
        if (list.length > 0) setChapters(list.map(chapterToOutline));
      })
      .catch(() => {
        /* keep stub fallback */
      });
  }, [chaptersProp]);

  useEffect(() => {
    if (!chapterId) return;
    saveSessionState({
      chapterId,
      chapterTitle: activeChapter?.title,
      section: activeSectionId,
      source: peekSourceId ?? undefined,
      panel: railTab as PanelTab,
      route: `/writing/${chapterId}`,
    });
  }, [chapterId, activeChapter?.title, activeSectionId, peekSourceId, railTab]);

  useEffect(() => {
    if (urlState.source) setPeekSourceId(urlState.source);
    const panel = panelFromParam(urlState.panel ?? null);
    if (panel) setRailTab(panel);
  }, [urlState.source, urlState.panel]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || !event.shiftKey || event.key.toLowerCase() !== "r") return;
      event.preventDefault();
      if (chapterId) {
        router.push(`/review?chapter=${encodeURIComponent(chapterId)}`);
      } else {
        dispatchOpenReview();
        router.push("/review");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [chapterId, router]);

  const handleChapterUpdated = useCallback((ch: Chapter) => {
    setActiveChapter(ch);
    setChapters((prev) => {
      const idx = prev.findIndex((c) => c.id === ch.id);
      const next = chapterToOutline(ch);
      if (idx === -1) return [...prev, next];
      const copy = [...prev];
      copy[idx] = next;
      return copy;
    });
  }, []);

  const handleSectionsChange = useCallback((next: MarkdownSection[]) => {
    setSections(next);
  }, []);

  const toggleOutline = useCallback(() => setShowOutline((open) => !open), []);
  const toggleRail = useCallback(() => setShowRail((open) => !open), []);

  useWritingPanelChrome({ toggleOutline, toggleRail });

  const sectionIds = sections.map((section) => section.id);
  const navigateSection = useCallback(
    (sectionId: string) => {
      if (!chapterId) return;
      router.push(
        `/writing/${chapterId}?section=${encodeURIComponent(sectionId)}`
      );
    },
    [chapterId, router]
  );

  useOutlineSectionChrome({
    sectionIds,
    activeSectionId,
    onNavigate: navigateSection,
  });

  const panelShell =
    "overflow-hidden rounded-lg border border-border bg-surface shadow-sm";

  const resolvedChapterId = chapterId;
  const chapterContent =
    activeChapter && activeChapter.id === resolvedChapterId
      ? activeChapter.content_md
      : null;

  return (
    <div className={cn("space-y-3", className)} data-testid="writing-workspace">
      {readOnly && (
        <div
          className="rounded-md border border-warning/30 bg-warning/10 px-4 py-2 text-sm text-warning"
          role="status"
          data-testid="writing-readonly-banner"
        >
          Usa desktop per scrivere — l&apos;editor è in sola lettura su schermi piccoli.
        </div>
      )}

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
          aria-pressed={showRail}
          aria-controls="writing-rail-panel"
          onClick={() => setShowRail((open) => !open)}
          className={cn(
            "rounded-md border px-3 py-1.5 text-xs font-medium transition-colors duration-200",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "focus-visible:outline-accent cursor-pointer",
            showRail
              ? "border-accent bg-accent-subtle text-accent"
              : "border-border bg-surface text-ink-muted"
          )}
        >
          Pannello
        </button>
      </div>

      <div className="flex min-h-[32rem] flex-col gap-3 lg:min-h-[36rem] lg:flex-row lg:gap-4">
        <div
          id="writing-outline-panel"
          className={cn(
            panelShell,
            "w-full shrink-0 lg:w-outline",
            showOutline ? "block" : "hidden lg:block"
          )}
        >
          <WritingOutline
            chapters={chapters}
            activeChapterId={resolvedChapterId}
            activeSectionId={activeSectionId}
            sections={sections}
          />
        </div>

        <div className={cn(panelShell, "min-w-0 min-w-editor flex-1")}>
          <WritingEditorShell
            chapterId={resolvedChapterId}
            chapter={activeChapter?.id === resolvedChapterId ? activeChapter : null}
            activeSectionId={activeSectionId}
            readOnly={readOnly}
            onChapterUpdated={handleChapterUpdated}
            onSectionsChange={handleSectionsChange}
          />
        </div>

        <div
          id="writing-rail-panel"
          className={cn(
            panelShell,
            "w-full shrink-0 lg:w-rail",
            showRail ? "block" : "hidden lg:block"
          )}
        >
          <RightRail
            chapterId={resolvedChapterId}
            contextPacket={contextPacket}
            selectionText={selectionText}
            selectionAnchor={activeSectionId ?? null}
            chapterContent={chapterContent}
            defaultTab={railTab}
            peekSourceId={peekSourceId}
            onPeekSourceChange={setPeekSourceId}
            editorFocusRef={editorFocusRef}
          />
        </div>
      </div>

      <LinkedSourcesFooter chapterId={resolvedChapterId} />
    </div>
  );
}
