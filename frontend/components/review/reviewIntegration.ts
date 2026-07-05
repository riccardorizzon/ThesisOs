"use client";

/**
 * Review workspace entry hooks — PX2-EWO-007.
 * Integration C wires Writing ⌘⇧R to dispatchOpenReview().
 * Layer: Business (Product Plane)
 */

export const OPEN_REVIEW_EVENT = "thesisos:open-review";

export type OpenReviewDetail = {
  chapterId?: string;
};

export function dispatchOpenReview(chapterId?: string): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent<OpenReviewDetail>(OPEN_REVIEW_EVENT, {
      detail: { chapterId },
    })
  );
}
