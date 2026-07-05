"use client";

import { useEffect } from "react";
import {
  APPLY_AI_SUGGESTION_EVENT,
  CITE_SOURCE_EVENT,
  FIND_IN_CHAPTER_EVENT,
  FORCE_SAVE_EVENT,
  OUTLINE_NEXT_SECTION_EVENT,
  OUTLINE_PREV_SECTION_EVENT,
  TOGGLE_OUTLINE_EVENT,
  TOGGLE_RIGHT_RAIL_EVENT,
} from "@/components/chrome/CommandPalette";
import { railTabFromShortcut, type RailTabId } from "@/components/writing/RailTabs";

/** Integration D — palette / shortcut events → writing workspace (supervisor-owned). */

export function useWritingPanelChrome({
  toggleOutline,
  toggleRail,
}: {
  toggleOutline: () => void;
  toggleRail: () => void;
}): void {
  useEffect(() => {
    const onToggleOutline = () => toggleOutline();
    const onToggleRail = () => toggleRail();

    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || event.altKey || event.ctrlKey) return;
      if (event.shiftKey && event.key === "\\") {
        event.preventDefault();
        toggleRail();
        return;
      }
      if (!event.shiftKey && event.key === "\\") {
        event.preventDefault();
        toggleOutline();
      }
    };

    window.addEventListener(TOGGLE_OUTLINE_EVENT, onToggleOutline);
    window.addEventListener(TOGGLE_RIGHT_RAIL_EVENT, onToggleRail);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener(TOGGLE_OUTLINE_EVENT, onToggleOutline);
      window.removeEventListener(TOGGLE_RIGHT_RAIL_EVENT, onToggleRail);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [toggleOutline, toggleRail]);
}

export function useWritingEditorChrome({
  onForceSave,
  onFindInChapter,
  onCiteSource,
}: {
  onForceSave: () => void;
  onFindInChapter?: () => void;
  onCiteSource?: () => void;
}): void {
  useEffect(() => {
    const onSave = () => onForceSave();
    const onFind = () => onFindInChapter?.();
    const onCite = () => onCiteSource?.();

    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || event.altKey || event.ctrlKey) return;
      if (!event.shiftKey && event.key.toLowerCase() === "s") {
        event.preventDefault();
        onForceSave();
        return;
      }
      if (event.shiftKey && event.key.toLowerCase() === "f") {
        event.preventDefault();
        onFindInChapter?.();
      }
    };

    window.addEventListener(FORCE_SAVE_EVENT, onSave);
    window.addEventListener(FIND_IN_CHAPTER_EVENT, onFind);
    window.addEventListener(CITE_SOURCE_EVENT, onCite);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener(FORCE_SAVE_EVENT, onSave);
      window.removeEventListener(FIND_IN_CHAPTER_EVENT, onFind);
      window.removeEventListener(CITE_SOURCE_EVENT, onCite);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [onForceSave, onFindInChapter, onCiteSource]);
}

export function useOutlineSectionChrome({
  sectionIds,
  activeSectionId,
  onNavigate,
}: {
  sectionIds: string[];
  activeSectionId?: string;
  onNavigate: (sectionId: string) => void;
}): void {
  useEffect(() => {
    const step = (delta: number) => {
      if (sectionIds.length === 0) return;
      const currentIndex = activeSectionId
        ? sectionIds.indexOf(activeSectionId)
        : -1;
      const nextIndex =
        currentIndex === -1
          ? delta > 0
            ? 0
            : sectionIds.length - 1
          : currentIndex + delta;
      if (nextIndex < 0 || nextIndex >= sectionIds.length) return;
      onNavigate(sectionIds[nextIndex]);
    };

    const onPrev = () => step(-1);
    const onNext = () => step(1);

    const onKeyDown = (event: KeyboardEvent) => {
      if (!event.metaKey || event.shiftKey || event.altKey || event.ctrlKey) return;
      if (event.key === "ArrowUp") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "ArrowDown") {
        event.preventDefault();
        step(1);
      }
    };

    window.addEventListener(OUTLINE_PREV_SECTION_EVENT, onPrev);
    window.addEventListener(OUTLINE_NEXT_SECTION_EVENT, onNext);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener(OUTLINE_PREV_SECTION_EVENT, onPrev);
      window.removeEventListener(OUTLINE_NEXT_SECTION_EVENT, onNext);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [sectionIds, activeSectionId, onNavigate]);
}

export function useRailTabChrome(onTabChange: (tab: RailTabId) => void): void {
  useEffect(() => {
    const handlers = [1, 2, 3, 4].map((digit) => {
      const tab = railTabFromShortcut(digit);
      if (!tab) return null;
      const handler = () => onTabChange(tab);
      const eventName = `thesisos:rail-tab-${digit}`;
      window.addEventListener(eventName, handler);
      return { eventName, handler };
    });

    return () => {
      handlers.forEach((entry) => {
        if (entry) {
          window.removeEventListener(entry.eventName, entry.handler);
        }
      });
    };
  }, [onTabChange]);
}

export function useApplyAiSuggestionChrome(onApply: () => void): void {
  useEffect(() => {
    const handler = () => onApply();
    window.addEventListener(APPLY_AI_SUGGESTION_EVENT, handler);
    return () => window.removeEventListener(APPLY_AI_SUGGESTION_EVENT, handler);
  }, [onApply]);
}
