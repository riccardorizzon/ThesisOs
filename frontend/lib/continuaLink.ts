/**
 * Continua deep link — restores last writing session from localStorage (PX-2.5)
 * Layer: Business (Product Plane)
 */

import type { ContinueTarget } from "@/lib/progress";
import {
  loadSessionState,
  serializeWritingUrlState,
  sessionStateToUrlState,
} from "@/lib/sessionState";

export type ContinuaLinkOptions = {
  /** Fallback when no persisted session exists */
  fallback: ContinueTarget;
};

/**
 * Build Continua href + label from last session in localStorage.
 * Restores chapter, section query params, panel tab, and section hash anchor.
 */
export function buildContinuaLink(options: ContinuaLinkOptions): ContinueTarget {
  const session = loadSessionState();
  if (!session?.chapterId) {
    return options.fallback;
  }

  const urlState = sessionStateToUrlState(session);
  const href = serializeWritingUrlState(session.chapterId, urlState, {
    scrollAnchor: session.section ? `section-${session.section.replace(/\./g, "-")}` : undefined,
  });

  const sectionPart = session.section ? ` · §${session.section}` : "";
  const label =
    session.chapterTitle != null
      ? `${session.chapterTitle}${sectionPart}`
      : options.fallback.label + sectionPart;

  return { href, label: label.trim() };
}

/** Merge chapter-derived fallback with persisted session state. */
export function mergeContinuaTarget(fallback: ContinueTarget): ContinueTarget {
  return buildContinuaLink({ fallback });
}
