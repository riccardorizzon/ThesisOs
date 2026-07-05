"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export const OPEN_COMMAND_PALETTE_EVENT = "thesisos:open-command-palette";

const CHORD_TIMEOUT_MS = 1000;

export type KeyboardShortcutHandlers = {
  onOpenCommandPalette?: () => void;
};

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  return target.isContentEditable;
}

function dispatchOpenCommandPalette(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(OPEN_COMMAND_PALETTE_EVENT));
}

/**
 * Global keyboard shortcuts — G→W/S/H chords and palette openers.
 * Feature-owned chords (⌘1-4, ⌘⇧R, ⌘⇧C) are listed in CommandPalette only.
 * Layer: Business (Product Plane)
 */
export function useKeyboardShortcuts(handlers?: KeyboardShortcutHandlers): void {
  const router = useRouter();
  const pendingChord = useRef<string | null>(null);
  const chordTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const openPalette = () => {
      handlers?.onOpenCommandPalette?.();
      dispatchOpenCommandPalette();
    };

    const clearChord = () => {
      pendingChord.current = null;
      if (chordTimer.current != null) {
        clearTimeout(chordTimer.current);
        chordTimer.current = null;
      }
    };

    const onKeyDown = (event: KeyboardEvent) => {
      const meta = event.metaKey || event.ctrlKey;

      if (meta && event.key.toLowerCase() === "k" && !event.shiftKey) {
        event.preventDefault();
        openPalette();
        return;
      }

      if (meta && event.shiftKey && event.key.toLowerCase() === "p") {
        event.preventDefault();
        openPalette();
        return;
      }

      if (isEditableTarget(event.target)) return;

      if (event.key.toLowerCase() === "g" && !meta && !event.altKey && !event.ctrlKey) {
        clearChord();
        pendingChord.current = "g";
        chordTimer.current = setTimeout(clearChord, CHORD_TIMEOUT_MS);
        return;
      }

      if (pendingChord.current === "g" && !meta && !event.altKey && !event.ctrlKey) {
        const key = event.key.toLowerCase();
        if (key === "w" || key === "s" || key === "h") {
          event.preventDefault();
          clearChord();
          if (key === "w") router.push("/writing");
          else if (key === "s") router.push("/sources");
          else router.push("/");
          return;
        }
        clearChord();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      clearChord();
    };
  }, [handlers, router]);
}
